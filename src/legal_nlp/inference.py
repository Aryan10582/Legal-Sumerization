"""Local inference; never interpret an untrained classifier head as a prediction."""
from pathlib import Path
import json, time
from .common import LABELS, runtime
from .text import bounded_segments,clean
from .summarization import select_text,transformer_summary
from .training import predict_classifier

class Engine:
    def __init__(self,cfg,task,method):
        self.cfg=cfg; self.task=task; self.method=method; self.device,_=runtime(cfg)
        self.model=None; self.tokenizer=None; self.meta={}
        from transformers import AutoTokenizer,AutoModelForSequenceClassification,AutoModelForSeq2SeqLM
        root=Path(cfg['output_dir'])/method
        if task=='classification':
            if method not in ['tfidf','legalbert']: raise ValueError('Invalid classification method')
            if not (root/'run.json').exists(): raise ValueError('Train this classifier first: python -m legal_nlp baseline or train --task classification')
            self.meta=json.loads((root/'run.json').read_text(encoding='utf-8'))
            if method=='tfidf':
                import joblib
                local_tok=root/'tokenizer_config.json'
                self.tokenizer=AutoTokenizer.from_pretrained(root) if local_tok.exists() else AutoTokenizer.from_pretrained(cfg[task]['model'],revision=cfg[task]['revision'])
                self.model=joblib.load(root/'model.joblib')
            else:
                if not self.meta.get('fine_tuned'): raise ValueError('Classifier checkpoint has not been fine-tuned')
                self.tokenizer=AutoTokenizer.from_pretrained(root)
                self.model=AutoModelForSequenceClassification.from_pretrained(root).to(self.device).eval()
        elif method=='t5':
            if not (root/'run.json').exists(): raise ValueError('Fine-tune the summarizer first: python -m legal_nlp train --task summarization')
            self.meta=json.loads((root/'run.json').read_text(encoding='utf-8'))
            if not self.meta.get('fine_tuned'): raise ValueError('Summary checkpoint has not been fine-tuned')
            self.tokenizer=AutoTokenizer.from_pretrained(root)
            self.model=AutoModelForSeq2SeqLM.from_pretrained(root).to(self.device).eval()
        elif method!='extractive': raise ValueError('Invalid summarization method')

    def run(self,text):
        text=clean(text)
        if len(text)<20: raise ValueError('Enter at least 20 characters')
        if len(text)>300000: raise ValueError('The lab demonstration accepts up to 300,000 characters; use the offline scripts for larger corpora')
        start=time.perf_counter()
        if self.task=='classification':
            max_tokens=self.meta.get('settings',{}).get('max_tokens',self.cfg['classification']['max_tokens'])
            rows=bounded_segments(text,self.tokenizer,max_tokens)
            if self.method=='tfidf': probabilities=self.model.predict_proba([r['text'] for r in rows])
            else: probabilities=predict_classifier(rows,self.tokenizer,self.model,self.device,max_tokens=max_tokens)
            threshold=self.meta['threshold']
            return {'task':self.task,'method':self.method,'threshold':threshold,'seconds':time.perf_counter()-start,
                    'scope':'Eight CUAD categories; English non-Indian benchmark. Scores are uncalibrated. No detected label does not establish that a clause is legally safe.',
                    'segments':[{**r,'labels':[l for l,p in zip(LABELS,probs) if p>=threshold],
                                 'scores':dict(zip(LABELS,map(float,probs)))} for r,probs in zip(rows,probabilities)]}
        if self.method=='extractive':
            # Offline path needs no model download; length uses words, clearly labelled.
            summary,trace=select_text(text,None,150)
            trace['budget_unit']='whitespace words (150); benchmark baseline uses 128 T5 tokens'
        else:
            summary,trace=transformer_summary(text,self.tokenizer,self.model,self.device,**{k:self.meta['settings'][k] for k in ['max_source_tokens','max_target_tokens','num_beams']})
            trace['budget_unit']='T5 tokens'
        return {'task':self.task,'method':self.method,'summary':summary,'trace':trace,'seconds':time.perf_counter()-start,
                'scope':'Research aid. Verify names, dates, legal issues, reasoning and disposition against the original judgment.'}
