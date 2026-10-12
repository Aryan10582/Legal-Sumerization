from collections import defaultdict
from pathlib import Path
import numpy as np
from .common import LABELS, write_json, write_jsonl

def classification_metrics(y, p, threshold):
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, hamming_loss, multilabel_confusion_matrix, average_precision_score
    pred=p>=threshold
    result={'subset_accuracy':float(accuracy_score(y,pred)),'hamming_loss':float(hamming_loss(y,pred)),
            'threshold':threshold,'rows':len(y),'negative_rows':int((y.sum(axis=1)==0).sum())}
    for avg in ['micro','macro','weighted']:
        precision,recall,f1,_=precision_recall_fscore_support(y,pred,average=avg,zero_division=0)
        result[avg]={'precision':float(precision),'recall':float(recall),'f1':float(f1)}
    precision,recall,f1,support=precision_recall_fscore_support(y,pred,average=None,zero_division=0)
    matrices=multilabel_confusion_matrix(y,pred)
    result['per_class']={label:{'precision':float(precision[i]),'recall':float(recall[i]),'f1':float(f1[i]),'support':int(support[i]),
                               'average_precision':float(average_precision_score(y[:,i],p[:,i])) if support[i] else None,
                               'confusion_matrix_tn_fp_fn_tp':matrices[i].ravel().tolist()} for i,label in enumerate(LABELS)}
    return result

def rouge_metrics(references,predictions):
    from rouge_score import rouge_scorer
    scorer=rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'],use_stemmer=True)
    rows=[{k:float(v.fmeasure) for k,v in scorer.score(r,p).items()} for r,p in zip(references,predictions)]
    return {'count':len(rows),'scale':'0 to 1','aggregation':'arithmetic document mean of F1',
            'configuration':'rouge-score 0.1.2; default English alphanumeric tokenizer; Porter stemming; ROUGE-L (not Lsum); full reference',
            **{k:float(np.mean([r[k] for r in rows])) for k in ['rouge1','rouge2','rougeL']}},rows

def paired_bootstrap(y,p,metric,seed=42,repeats=200,groups=None):
    """Optional document-cluster bootstrap; not used for model selection."""
    rng=np.random.default_rng(seed)
    if groups is None: groups=np.arange(len(y))
    unique=np.unique(groups); scores=[]
    for _ in range(repeats):
        chosen=rng.choice(unique,len(unique),replace=True)
        ids=np.concatenate([np.where(groups==g)[0] for g in chosen])
        scores.append(metric(y[ids],p[ids]))
    return np.quantile(scores,[.025,.975]).tolist()

def save_classification(out,rows,y,p,threshold,metadata):
    result={**classification_metrics(y,p,threshold),**metadata}
    write_json(Path(out)/'metrics.json',result)
    # Store identifiers + predictions; raw copyrighted contracts remain under data/.
    write_jsonl(Path(out)/'predictions.jsonl',[{'id':r['id'],'document_id':r['document_id'],'truth':r['labels'],
        'prediction':[l for l,s in zip(LABELS,probs) if s>=threshold],'probabilities':dict(zip(LABELS,map(float,probs)))} for r,probs in zip(rows,p)])
    return result
