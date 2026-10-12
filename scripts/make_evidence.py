from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from legal_nlp.common import read_jsonl,write_json,LABELS
out=Path('reports/figures'); out.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(figsize=(3.25,5.1)); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
def box(x,y,w,h,text,color='#e8eef5'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.10,rounding_size=.12',facecolor=color,edgecolor='#34465b',linewidth=1))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=7.5,color='#172a40')
def arrow(x,y,xx,yy): ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops={'arrowstyle':'->','color':'#34465b','lw':1.3})
box(.4,8.9,9.2,.7,'LOCAL INPUT: paste or upload English text')
box(.4,7.55,9.2,.8,'Extract TXT / DOCX / searchable PDF\nCheck text; reject missing OCR')
arrow(5,8.9,5,8.35)
box(.4,5.65,9.2,1.2,'JUDGMENT → Indian IN-Abs pairs\nFull-text TF-IDF / MMR selection\nExtractive baseline or fine-tuned T5','#e4f1ea')
arrow(5,7.55,5,6.85)
box(.4,3.75,9.2,1.2,'CONTRACT → non-Indian CUAD QA spans\nOffset-preserving multi-label passages\nTF-IDF / LR or fine-tuned LEGAL-BERT','#e8edf8')
ax.text(5,5.34,'OR — separate task',ha='center',va='center',fontsize=7.5,color='#34465b')
box(.4,2.05,9.2,1,'Held-out metrics: ROUGE for summaries;\nper-label P/R/F1 for clauses')
arrow(5,3.75,5,3.05)
box(.4,.4,9.2,1,'Streamlit: source beside output\nTXT / CSV / JSON export; human review')
arrow(5,2.05,5,1.4)
fig.savefig(out/'architecture.png',dpi=240,bbox_inches='tight',pad_inches=.04); plt.close(fig)

test={r['id']:r for r in read_jsonl('data/processed/pilot/classification/test.jsonl')}
preds=read_jsonl('artifacts/pilot/legalbert/test/predictions.jsonl')
examples=[]
for label,kind in [('Cap On Liability','false_positive'),('Post-Termination Services','false_negative'),('Governing Law','true_positive')]:
    def matches(r):
        t=label in r['truth']; p=label in r['prediction']
        return (p and not t) if kind=='false_positive' else ((t and not p) if kind=='false_negative' else (t and p))
    r=next(r for r in preds if matches(r))
    examples.append({**r,'label_reviewed':label,'error_kind':kind,'source':test[r['id']]['text']})
summ=read_jsonl('data/processed/pilot/summarization/test.jsonl')
t5=read_jsonl('artifacts/pilot/t5/test/predictions.jsonl'); ext=read_jsonl('artifacts/pilot/extractive/test/predictions.jsonl')
write_json('artifacts/qualitative_examples.json',{'classification':examples,'summarization':{'id':summ[0]['id'],'reference':summ[0]['summary'],'source_ending':summ[0]['text'][-2400:],'t5':t5[0],'extractive':ext[0]},'note':'Representative examples selected after evaluation for explanation, not selection or hyperparameter tuning. Some original source OCR errors retained.'})
lines=['# Actual pilot evidence','', 'Values below are read from the saved metric JSONs. Scale 0–1; same held-out data within each task.','']
metrics={name:json.loads(Path(f'artifacts/pilot/{name}/test/metrics.json').read_text()) for name in ['tfidf','legalbert','extractive','t5']}
for name,m in metrics.items():
    lines.append(f'## {name}\n\n```json\n'+json.dumps({k:v for k,v in m.items() if k not in ['hardware','training_run','data_fingerprint']},indent=2)+'\n```\n')
lines+=['## Qualitative review','', 'IN-Abs test 3542: reference and original ending explicitly allow the appeals and drop contempt proceedings. T5 recounts the letter and deponents’ position but omits disposition and the reasoning on accepting an apology without a contempt finding. This is material omission; the output must not be read as the court’s final holding. The extractive summary retains the apology reasoning but also omits the final order and ends with the fragment “The High.” Sentence splitting at abbreviations/periods is a known source of incomplete units.','', 'LEGAL-BERT: Cap On Liability has 20 false positives, one false negative and seven true positives. Post-Termination Services misses all eight positives. A threshold of 0.90 chosen on small validation support cannot be assumed to work across jurisdictions. The qualitative JSON includes actual passages for inspection. No expert-enforceability or hallucination-rate score was measured.','', 'Always-zero subset accuracy = 2340 / 2404 = 0.9733777, macro F1 = 0. Both trained classifiers have lower subset accuracy but detect real positives. No significance or broad generalization claim is made from ten test contracts and twenty test judgments.']
Path('docs/EXPERIMENT_RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(examples,indent=2)[:8000])
