from pathlib import Path
import json,time
import numpy as np
from .common import read_jsonl,write_json,write_jsonl,runtime,LABELS
from .training import data_fingerprint,predict_classifier
from .evaluation import save_classification,rouge_metrics
from .summarization import select_text,transformer_summary

def evaluate(cfg,task,model_name):
    device,hardware=runtime(cfg); rows=read_jsonl(Path(cfg['data_dir'])/task/'test.jsonl')
    base=Path(cfg['output_dir'])/model_name; out=base/'test'; out.mkdir(parents=True,exist_ok=True)
    from transformers import AutoTokenizer,AutoModelForSequenceClassification,AutoModelForSeq2SeqLM
    metadata={}
    if model_name!='extractive':
        metadata=json.loads((base/'run.json').read_text(encoding='utf-8'))
        if metadata['task']!=task or metadata['data_fingerprint']!=data_fingerprint(cfg['data_dir'],task):
            raise ValueError('Checkpoint/task/data manifest mismatch; use the config for this experiment')
    if task=='classification':
        y=np.array([r['label_vector'] for r in rows])
        if model_name=='tfidf':
            import joblib
            model=joblib.load(base/'model.joblib') # Load only locally generated, trusted checkpoints.
            start=time.perf_counter(); p=model.predict_proba([r['text'] for r in rows])
        elif model_name=='legalbert':
            tok=AutoTokenizer.from_pretrained(base); model=AutoModelForSequenceClassification.from_pretrained(base).to(device)
            start=time.perf_counter(); p=predict_classifier(rows,tok,model,device,cfg[task]['batch_size'],metadata['settings']['max_tokens'])
        else: raise ValueError('Classification model must be tfidf or legalbert')
        return save_classification(out,rows,y,p,metadata['threshold'],{'inference_seconds':time.perf_counter()-start,'hardware':hardware,
                  'test_document_count':len({r['document_id'] for r in rows}),'training_run':metadata,'dataset':'CUAD-derived eight-label segments; non-Indian contracts'})
    if model_name=='extractive':
        tok=AutoTokenizer.from_pretrained(cfg[task]['model'],revision=cfg[task]['revision']); model=None
    elif model_name=='t5':
        tok=AutoTokenizer.from_pretrained(base); model=AutoModelForSeq2SeqLM.from_pretrained(base).to(device).eval()
    else: raise ValueError('Summarization model must be extractive or t5')
    predictions=[]; details=[]; start=time.perf_counter()
    for i,r in enumerate(rows):
        before=time.perf_counter()
        if model is None: pred,trace=select_text(r['text'],tok,cfg[task]['max_target_tokens'])
        else: pred,trace=transformer_summary(r['text'],tok,model,device,**{k:metadata['settings'][k] for k in ['max_source_tokens','max_target_tokens','num_beams']})
        predictions.append(pred); details.append({'id':r['id'],'prediction':pred,'trace':trace,'seconds':time.perf_counter()-before})
        print(model_name,'test',i+1,'/',len(rows),flush=True)
    metrics,scores=rouge_metrics([r['summary'] for r in rows],predictions)
    metrics.update({'inference_seconds':time.perf_counter()-start,'hardware':hardware,'training_run':metadata or None,
                    'data_fingerprint':data_fingerprint(cfg['data_dir'],task),'dataset':'IN-Abs English Indian Supreme Court judgments'})
    write_json(out/'metrics.json',metrics)
    write_jsonl(out/'predictions.jsonl',[{**d,'rouge':s} for d,s in zip(details,scores)])
    return metrics
