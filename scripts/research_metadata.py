"""Retrieve original Crossref-deposited metadata for a transparent reference audit."""
import concurrent.futures as cf
import urllib.request, urllib.parse, json, re, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TITLES=[
"Deep learning in law: Early adaptation and legal word embeddings trained on large corpora",
"Predicting judicial decisions of the European Court of Human Rights: A natural language processing perspective",
"Evaluation of automatic legal text summarization techniques for Greek case law",
"A high-precision two-stage legal judgment summarization",
"A comprehensive analysis of Indian legal documents summarization techniques",
"Natural language processing in law: Prediction of outcomes in the higher courts of Turkey",
"A general approach for predicting the behavior of the Supreme Court of the United States",
"Automated detection of contractual risk clauses from construction specifications using bidirectional encoder representations from transformers (BERT)",
"Using machine learning to predict decisions of the European Court of Human Rights",
"Enhancing Indian legal judgment classification with embeddings, feature selection, and ensemble strategies",
"Legal judgment prediction via legal knowledge extraction and fusion",
"Legal information retrieval systems: State-of-the-art and open issues",
"Effective deep learning approaches for summarization of legal texts",
"Text summarization from legal documents: A survey",
"Improving abstractive summarization of legal rulings through textual entailment",
"A case study for automated attribute extraction from legal documents using large language models",
"Transformers for multi-intent classification and slot filling of Supreme Court decisions related to sexual violence law",
"Legal text classification in Korean sexual offense cases: From traditional machine learning to large language models with XAI insights",
"DyLas: A dynamic label alignment strategy for large-scale multi-label text classification",
"Applicability of large language models and generative models for legal case judgement summarization",
"Ensemble methods for improving extractive summarization of legal case judgements",
"A sentence is known by the company it keeps: Improving Legal Document Summarization Using Deep Clustering",
"Enhancing legal judgment summarization with integrated semantic and structural information",
"Summarizing judicial documents: a hybrid extractive-abstractive model with legal domain knowledge",
"Automated multi-label classification of risk clauses in construction contracts using GPT-driven data augmentation",
"LSDK-LegalSum: improving legal judgment summarization using logical structure and domain knowledge",
"A support system for the detection of abusive clauses in B2C contracts",
]
def get(i,title):
    path=ROOT/f"research/crossref/{i:02d}.json"
    if path.exists(): data=json.loads(path.read_text(encoding="utf-8"))
    else:
        url="https://api.crossref.org/works?rows=3&query.title="+urllib.parse.quote(title)
        req=urllib.request.Request(url,headers={"User-Agent":"AcademicMiniProject/1.0 (bibliographic audit)"})
        for retry in range(6):
            try:
                with urllib.request.urlopen(req,timeout=60) as resp: data=json.load(resp)
                break
            except Exception:
                if retry == 5: raise
                time.sleep(3 * (retry+1))
        path.parent.mkdir(exist_ok=True,parents=True); path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    out=[]
    for m in data['message']['items']:
        out.append({k:m.get(k) for k in ['title','author','container-title','type','published','published-print','published-online','volume','issue','page','article-number','DOI','ISSN','abstract','link']})
    return {'id':i,'query':title,'candidates':out}
if __name__=='__main__':
    all=[]
    with cf.ThreadPoolExecutor(max_workers=1) as ex:
        for x in ex.map(lambda it:get(*it),enumerate(TITLES,1)):
            all.append(x); m=x['candidates'][0]
            print(x['id'],m['title'],m['DOI'],m['container-title'],m['published'],m['volume'],m['issue'],m['page'],m['article-number'],flush=True)
    (ROOT/'research/reference-candidates.json').write_text(json.dumps(all,ensure_ascii=False,indent=2),encoding='utf-8')
