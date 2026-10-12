"""Explicit PyTorch fine-tuning, validation selection, and checkpoint provenance."""
from pathlib import Path
import math, time, json, copy
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from .common import LABELS, read_jsonl, write_json, seed_all, runtime, select_threshold, digest
from .summarization import select_text

def data_fingerprint(directory,task):
    return {s:digest((Path(directory)/task/(s+'.jsonl')).read_text(encoding='utf-8')) for s in ['train','validation','test']}

class Encoded(Dataset):
    def __init__(self,rows,tok,task,settings):
        self.data=[]; self.target_shortened=0; self.coverage=[]
        for r in rows:
            if task=='classification':
                enc=tok(r['text'],truncation=False)
                if len(enc['input_ids'])>settings['max_tokens']: raise ValueError('Prepared segment exceeds transformer limit; prepare again')
                enc['labels']=r['label_vector']
            else:
                budget=settings['max_source_tokens']-len(tok.encode('summarize: ',add_special_tokens=True))-1
                selected,trace=select_text(r['text'],tok,budget)
                enc=tok('summarize: '+selected,truncation=False)
                if len(enc['input_ids'])>settings['max_source_tokens']: raise ValueError('Source budget exceeded')
                target=tok(r['summary'],truncation=False)['input_ids']
                self.target_shortened+=int(len(target)>settings['max_target_tokens'])
                target=target[:settings['max_target_tokens']-1]+[tok.eos_token_id] if len(target)>settings['max_target_tokens'] else target
                enc['labels']=target; self.coverage.append(trace['coverage_fraction'])
            self.data.append(enc)
    def __len__(self): return len(self.data)
    def __getitem__(self,i): return self.data[i]

def collator(tok,task):
    def collate(items):
        labels=[item['labels'] for item in items]
        inputs=tok.pad([{k:v for k,v in item.items() if k!='labels'} for item in items],return_tensors='pt')
        if task=='classification': inputs['labels']=torch.tensor(labels,dtype=torch.float32)
        else:
            padded=torch.full((len(labels),max(map(len,labels))),-100,dtype=torch.long)
            for i,label in enumerate(labels): padded[i,:len(label)]=torch.tensor(label)
            inputs['labels']=padded
        return inputs
    return collate

def load_base(task,settings):
    from transformers import AutoTokenizer, AutoConfig, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
    tok=AutoTokenizer.from_pretrained(settings['model'],revision=settings['revision'])
    if task=='classification':
        c=AutoConfig.from_pretrained(settings['model'],revision=settings['revision'])
        # The original SMALL card config has a string architectures field.
        c.architectures=['BertForSequenceClassification']
        c.num_labels=len(LABELS); c.id2label=dict(enumerate(LABELS)); c.label2id={l:i for i,l in enumerate(LABELS)}
        c.problem_type='multi_label_classification'
        model=AutoModelForSequenceClassification.from_pretrained(settings['model'],revision=settings['revision'],config=c)
    else: model=AutoModelForSeq2SeqLM.from_pretrained(settings['model'],revision=settings['revision'])
    return tok,model

def predict_classifier(rows,tok,model,device,batch_size=8,max_tokens=256):
    model.eval(); out=[]
    with torch.inference_mode():
        for i in range(0,len(rows),batch_size):
            batch=rows[i:i+batch_size]
            enc=tok([r['text'] for r in batch],padding=True,truncation=False,return_tensors='pt')
            if enc.input_ids.shape[-1]>max_tokens: raise ValueError('Input exceeds checkpoint token limit')
            logits=model(**enc.to(device)).logits
            out.append(torch.sigmoid(logits).cpu().numpy())
    return np.concatenate(out) if out else np.empty((0,len(LABELS)))

def train_transformer(cfg,task):
    seed_all(cfg['seed']); device,hardware=runtime(cfg); settings=cfg[task]
    rows={s:read_jsonl(Path(cfg['data_dir'])/task/(s+'.jsonl')) for s in ['train','validation']}
    start=time.perf_counter(); tok,model=load_base(task,settings); model.to(device)
    datasets={s:Encoded(r,tok,task,settings) for s,r in rows.items()}
    generator=torch.Generator().manual_seed(cfg['seed'])
    loaders={s:DataLoader(d,batch_size=settings['batch_size'],shuffle=s=='train',generator=generator,collate_fn=collator(tok,task),num_workers=0) for s,d in datasets.items()}
    out=Path(cfg['output_dir'])/('legalbert' if task=='classification' else 't5'); out.mkdir(parents=True,exist_ok=True)
    optimizer=torch.optim.AdamW(model.parameters(),lr=settings['learning_rate'],weight_decay=settings['weight_decay'])
    acc=settings['accumulation_steps']; total=math.ceil(len(loaders['train'])/acc)*settings['epochs']
    warmup=max(1,round(.1*total))
    def lr_scale(step): return min((step+1)/warmup,max(0,(total-step)/max(1,total-warmup)))
    scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,lr_scale)
    if task=='classification':
        y=np.array([r['label_vector'] for r in rows['train']]); positives=y.sum(axis=0)
        if np.any(positives==0): raise ValueError(f'No training positives for {[LABELS[i] for i,p in enumerate(positives) if p==0]}; increase training documents')
        weights=torch.tensor(np.clip((len(y)-positives)/positives,1,20),dtype=torch.float32,device=device)
        criterion=torch.nn.BCEWithLogitsLoss(pos_weight=weights)
    log=[]; best=-float('inf'); best_epoch=None
    for epoch in range(settings['epochs']):
        epoch_start=time.perf_counter(); model.train(); optimizer.zero_grad(); losses=[]
        for step,batch in enumerate(loaders['train']):
            batch={k:v.to(device) for k,v in batch.items()}
            if task=='classification':
                labels=batch.pop('labels'); loss=criterion(model(**batch).logits,labels)
            else: loss=model(**batch).loss
            if not torch.isfinite(loss): raise ValueError('Non-finite training loss')
            losses.append(float(loss.detach().cpu()))
            group_start=(step//acc)*acc
            actual_acc=min(acc,len(loaders['train'])-group_start)
            (loss/actual_acc).backward()
            if (step+1)%acc==0 or step+1==len(loaders['train']):
                torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
                optimizer.step(); scheduler.step(); optimizer.zero_grad()
            if step%25==0: print(task,'epoch',epoch+1,'batch',step+1,'/',len(loaders['train']),'loss',round(losses[-1],4),flush=True)
        model.eval()
        if task=='classification':
            p=predict_classifier(rows['validation'],tok,model,device,settings['batch_size'],settings['max_tokens'])
            yval=np.array([r['label_vector'] for r in rows['validation']]); threshold,grid=select_threshold(yval,p)
            score=max(g['macro_f1'] for g in grid); validation={'macro_f1':score,'threshold':threshold}
        else:
            vals=[]
            with torch.inference_mode():
                for batch in loaders['validation']:
                    batch={k:v.to(device) for k,v in batch.items()}
                    vals.append((float(model(**batch).loss),len(batch['input_ids'])))
            val_loss=sum(v*n for v,n in vals)/sum(n for _,n in vals)
            score=-val_loss; validation={'teacher_forced_loss':val_loss}; threshold=None
        entry={'epoch':epoch+1,'train_loss_batch_mean':float(np.mean(losses)),'validation':validation,'epoch_seconds':time.perf_counter()-epoch_start}
        log.append(entry); print(entry,flush=True); write_json(out/'training_log.json',log)
        if score>best:
            best=score; best_epoch=epoch+1
            model.save_pretrained(out); tok.save_pretrained(out)
            metadata={'task':task,'fine_tuned':True,'model':settings['model'],'revision':settings['revision'],'settings':settings,
                      'seed':cfg['seed'],'hardware':hardware,'best_epoch':best_epoch,'validation_selection':validation,
                      'threshold':threshold,'data_fingerprint':data_fingerprint(cfg['data_dir'],task),'train_rows':len(rows['train']),
                      'validation_rows':len(rows['validation']),'parameter_count':sum(p.numel() for p in model.parameters()),
                      'target_shortened_train':datasets['train'].target_shortened,'target_shortened_validation':datasets['validation'].target_shortened,
                      'mean_training_source_character_coverage':float(np.mean(datasets['train'].coverage)) if datasets['train'].coverage else None,
                      'positive_loss_weights':weights.cpu().tolist() if task=='classification' else None,
                      'optimizer':'AdamW','gradient_clip_norm':1.,'scheduler':'linear 10% warmup','mixed_precision':False,
                      'resume_support':'saved checkpoint for inference / warm start; optimizer state is not saved',
                      'training_seconds':time.perf_counter()-start}
            write_json(out/'run.json',metadata)
    metadata=json.loads((out/'run.json').read_text(encoding='utf-8')); metadata['training_seconds']=time.perf_counter()-start
    metadata['epochs_completed']=settings['epochs']; write_json(out/'run.json',metadata)
    return metadata

def train_baseline(cfg):
    import joblib
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.multiclass import OneVsRestClassifier
    start=time.perf_counter(); seed_all(cfg['seed']); _,hardware=runtime(cfg)
    train=read_jsonl(Path(cfg['data_dir'])/'classification/train.jsonl')
    val=read_jsonl(Path(cfg['data_dir'])/'classification/validation.jsonl')
    pipeline=Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=40000,sublinear_tf=True)),
                       ('classifier',OneVsRestClassifier(LogisticRegression(C=1.,class_weight='balanced',solver='liblinear',max_iter=1000,random_state=cfg['seed'])))])
    y=np.array([r['label_vector'] for r in train])
    if np.any(y.sum(axis=0)==0): raise ValueError('Training split lacks a selected label; increase documents')
    pipeline.fit([r['text'] for r in train],y)
    p=pipeline.predict_proba([r['text'] for r in val]); threshold,grid=select_threshold(np.array([r['label_vector'] for r in val]),p)
    out=Path(cfg['output_dir'])/'tfidf'; out.mkdir(parents=True,exist_ok=True)
    joblib.dump(pipeline,out/'model.joblib')
    from transformers import AutoTokenizer
    AutoTokenizer.from_pretrained(cfg['classification']['model'],revision=cfg['classification']['revision']).save_pretrained(out)
    metadata={'task':'classification','fine_tuned':False,'trained':True,'labels':LABELS,'threshold':threshold,
              'validation_threshold_grid':grid,'data_fingerprint':data_fingerprint(cfg['data_dir'],'classification'),
              'training_seconds':time.perf_counter()-start,'train_rows':len(train),'validation_rows':len(val),'seed':cfg['seed'],
              'hardware':hardware,'settings':{'ngrams':[1,2],'min_df':2,'max_features':40000,'C':1,'class_weight':'balanced','max_iter':1000}}
    write_json(out/'run.json',metadata)
    return metadata
