"""Document-first splits; exact and approximate near-duplicate isolation."""
import re, hashlib, random
from collections import defaultdict
from .text import canonical
from .common import digest

def duplicate_groups(documents, near_threshold=.9):
    parent=list(range(len(documents)))
    def find(i):
        while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
        return i
    def join(i,j): parent[find(i)]=find(j)
    seen={}; buckets=defaultdict(list); sketches=[]; exact=near=0
    for i,d in enumerate(documents):
        s=canonical(d['text']); h=digest(s)
        if h in seen: join(i,seen[h]); exact+=1
        else: seen[h]=i
        words=re.findall(r"\w+",s)
        # Bottom-64 sketch; eight shared minima generate candidates. Approximate,
        # not a guarantee against all paraphrases or all near-duplicates.
        sh={int.from_bytes(hashlib.blake2b(' '.join(words[k:k+5]).encode(),digest_size=8).digest(),'big') for k in range(max(0,len(words)-4))}
        sketch=set(sorted(sh)[:64]); sketches.append(sketch)
        candidates=set(j for key in sorted(sketch)[:8] for j in buckets[key])
        for j in candidates:
            union=sketch|sketches[j]
            if union and len(sketch&sketches[j])/len(union)>=near_threshold and find(i)!=find(j):
                join(i,j); near+=1
        for key in sorted(sketch)[:8]: buckets[key].append(i)
    groups=[find(i) for i in range(len(documents))]
    return groups,{"exact_duplicate_documents":exact,"near_duplicate_links":near,"near_threshold":near_threshold,"method":"normalized SHA256 plus bottom-64 five-word sketch Jaccard; candidate search on eight minima; approximate"}

def partition(documents, seed=42, validation_fraction=.15):
    groups,audit=duplicate_groups(documents)
    official_test={g for d,g in zip(documents,groups) if d['official_split']=='test'}
    eligible=sorted({g for d,g in zip(documents,groups) if d['official_split']=='train' and g not in official_test})
    random.Random(seed).shuffle(eligible)
    n=max(1,round(len(eligible)*validation_fraction))
    val=set(eligible[:n]); out={s:[] for s in ['train','validation','test']}
    retained=set(); quarantined=[]
    for d,g in zip(documents,groups):
        if d['official_split']=='train' and g in official_test:
            quarantined.append(d['id']); continue
        split='test' if g in official_test else ('validation' if g in val else 'train')
        # Keep one representative per duplicate group, including within test.
        if g in retained: continue
        retained.add(g)
        out[split].append({**d,'group_id':str(g),'split':split})
    audit.update({"quarantined_train_ids":quarantined,"retained_documents":{k:len(v) for k,v in out.items()}})
    return out,audit

def limit_splits(splits, limits, seed):
    out={}
    for s,rows in splits.items():
        rows=sorted(rows,key=lambda r:r['id']); random.Random(seed).shuffle(rows)
        out[s]=rows if not limits.get(s) else rows[:limits[s]]
    return out

def assert_integrity(splits):
    for key in ['id','group_id']:
        seen=set()
        for rows in splits.values():
            values={r[key] for r in rows}
            if seen & values: raise ValueError(f"Split leakage in {key}")
            seen |= values
    seen=set()
    for rows in splits.values():
        values={digest(canonical(r['text'])) for r in rows}
        if seen & values: raise ValueError("Exact text duplicate crosses splits")
        seen |= values
