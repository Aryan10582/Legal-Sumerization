from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import hashlib, json, re, random
import requests
from .common import LABELS, write_json, write_jsonl, digest
from .text import bounded_segments, clean, canonical
from .splitting import partition, limit_splits, assert_integrity

CUAD_COMMIT="67faa0e6023b04fcaae6cc09497ab00e5d63a2a2"
SOURCES={
    "cuad":(f"https://raw.githubusercontent.com/The-Atticus-Project/cuad/{CUAD_COMMIT}/data.zip","24b7c808f1cb6373ae8f4faf49364f98"),
    "inabs":("https://zenodo.org/api/records/7152317/files/dataset.zip/content","c77948fe580d26200f5c9fe53b81485d"),
}

def download(raw_dir="data/raw"):
    root=Path(raw_dir); root.mkdir(parents=True,exist_ok=True); records=[]
    for name,(url,md5) in SOURCES.items():
        path=root/(name+'.zip')
        if not path.exists():
            temp=path.with_suffix('.part')
            with requests.get(url,stream=True,timeout=(30,180)) as r:
                r.raise_for_status()
                with temp.open('wb') as f:
                    for chunk in r.iter_content(1024*1024): f.write(chunk)
            temp.replace(path)
        data=path.read_bytes()
        if md5 and hashlib.md5(data).hexdigest()!=md5: raise ValueError(f"{name} archive checksum mismatch; remove the incomplete archive and retry")
        with ZipFile(path) as z:
            if z.testzip(): raise ValueError(f"Corrupt ZIP: {path}")
        records.append({'dataset':name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'md5':hashlib.md5(data).hexdigest()})
    write_json(root/'downloads.json',records)
    return records

def read_cuad(path):
    with ZipFile(path) as z:
        full=json.loads(z.read('CUADv1.json'))['data']
        test=json.loads(z.read('test.json'))['data']
    test_titles={d['title'] for d in test}
    out=[]; invalid=[]; all_labels=Counter()
    for doc in full:
        context_parts=[]; annotations=[]; base=0
        for p in doc['paragraphs']:
            context=p['context']; context_parts.append(context)
            for qa in p['qas']:
                label=qa['id'].rsplit('__',1)[-1]
                all_labels[label]+=len(qa['answers'])
                for ans in qa['answers']:
                    start=ans['answer_start']; end=start+len(ans['text'])
                    if context[start:end]!=ans['text']:
                        invalid.append({'document':doc['title'],'question':qa['id'],'start':start}); continue
                    if label in LABELS: annotations.append({'start':base+start,'end':base+end,'label':label})
            base+=len(context)+2
        text='\n\n'.join(context_parts)
        # DO NOT clean CUAD contexts before mapping official character offsets.
        out.append({'id':doc['title'],'text':text,'annotations':annotations,
                    'official_split':'test' if doc['title'] in test_titles else 'train'})
    return out,{'published_documents':510,'loaded_documents':len(out),'official_test_documents':len(test_titles),
                'official_train_documents':len(out)-len(test_titles),'all_41_label_span_counts':dict(all_labels),'invalid_answer_offsets':invalid}

def read_inabs(path):
    out=[]; missing=[]
    with ZipFile(path) as z:
        names=set(z.namelist())
        candidates=sorted(n for n in names if re.search(r"IN-Abs/(train-data|test-data)/judgement/[^/]+$",n))
        for name in candidates:
            summary=name.replace('/judgement/','/summary/')
            if summary not in names: missing.append(name); continue
            text=clean(z.read(name).decode('utf-8-sig',errors='strict'))
            target=clean(z.read(summary).decode('utf-8-sig',errors='strict'))
            if not text or not target: missing.append(name); continue
            out.append({'id':'inabs:'+Path(name).name,'text':text,'summary':target,
                        'official_split':'test' if '/test-data/' in name else 'train'})
    if not out: raise ValueError('IN-Abs archive layout not recognized')
    return out,{'published_documents':7130,'published_train':7030,'published_test':100,'loaded_pairs':len(out),'missing_or_empty':missing}

def clause_rows(documents, tokenizer, max_tokens):
    out=[]
    for doc in documents:
        for i,s in enumerate(bounded_segments(doc['text'],tokenizer,max_tokens)):
            labels=sorted({a['label'] for a in doc['annotations'] if a['start']<s['end'] and a['end']>s['start']})
            out.append({'id':doc['id']+':'+str(i),'document_id':doc['id'],'group_id':doc['group_id'],
                        **s,'labels':labels,'label_vector':[int(l in labels) for l in LABELS]})
    return out

def prepare(cfg, raw_dir='data/raw', full=False):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(cfg['classification']['model'],revision=cfg['classification']['revision'])
    root=Path(cfg['data_dir']); root.mkdir(parents=True,exist_ok=True)
    complete={}
    for task,loader,raw in [('classification',read_cuad,'cuad.zip'),('summarization',read_inabs,'inabs.zip')]:
        docs,source=loader(Path(raw_dir)/raw)
        split,audit=partition(docs,cfg['seed'])
        limits={s:None if full else cfg[task][s+'_documents'] for s in ['train','validation','test']}
        split=limit_splits(split,limits,cfg['seed']); assert_integrity(split)
        exact_seen={}; removed=Counter(); counts={}; label_counts={}
        # Test first: quarantine exact repeated segments from lower-priority sets.
        rows_by_split={s:clause_rows(d,tok,cfg[task]['max_tokens']) if task=='classification' else d for s,d in split.items()}
        for s in ['test','validation','train']:
            kept=[]
            for row in rows_by_split[s]:
                if task=='classification':
                    h=digest(canonical(row['text']))
                    if h in exact_seen and exact_seen[h]!=s: removed[s]+=1; continue
                    exact_seen[h]=s
                kept.append(row)
            rows_by_split[s]=kept
        # Negative downsampling only in TRAIN. Evaluation retains every segment.
        if task=='classification':
            positive=[r for r in rows_by_split['train'] if r['labels']]
            negative=[r for r in rows_by_split['train'] if not r['labels']]
            random.Random(cfg['seed']).shuffle(negative)
            ratio=cfg[task]['max_negative_ratio']
            rows_by_split['train']=positive+negative[:max(1,len(positive)*ratio)]
            random.Random(cfg['seed']).shuffle(rows_by_split['train'])
        for s,rows in rows_by_split.items():
            if not rows: raise ValueError(f'Empty {task} {s} split')
            write_jsonl(root/task/(s+'.jsonl'),rows)
            counts[s]={'documents':len(split[s]),'rows':len(rows)}
            if task=='classification': label_counts[s]=dict(Counter(l for r in rows for l in r['labels']))
        manifests={s:[{'id':d['id'],'group_id':d['group_id'],'sha256':digest(canonical(d['text']))} for d in rows] for s,rows in split.items()}
        write_json(root/task/'split_manifest.json',manifests)
        complete[task]={'source':source,'split_audit':audit,'actual_counts':counts,'label_counts':label_counts,
                        'cross_split_exact_segments_quarantined':dict(removed),'seed':cfg['seed'],'full':full,
                        'segment_label_policy':'Any character overlap with verified answer span; zero vector = no selected annotation, not a verified neutral legal clause' if task=='classification' else None}
        print(task,counts,flush=True)
    write_json(root/'preparation.json',complete)
    return complete
