import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const ROOT = 'D:/3rd year/Legal Sumerization';
const SKILL = 'C:/Users/aryan/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const PYTHON = 'C:/Users/aryan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const OUT = path.join(ROOT, 'slides_build');
const FINAL = path.join(ROOT, 'presentations', 'Project_Presentation.pptx');
const C = { bg:'#F8F7F4', white:'#FFFFFF', ink:'#183044', muted:'#536679', line:'#D7DEE2', orange:'#C4512E', teal:'#13757B', pale:'#E7F0EF', lightOrange:'#FAECE6' };
const pres = Presentation.create({slideSize:{width:1280,height:720}});

function box(slide,x,y,w,h,fill=C.white,stroke='none',radius=false){return slide.shapes.add({geometry:radius?'roundRect':'rect',position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:stroke==='none'?0:1}})}
function txt(slide,s,x,y,w,h,size=25,color=C.ink,bold=false,align='left'){
  const q=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});
  q.text=s; q.text.style={typeface:'Arial',fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',wrap:'square',autoFit:'shrinkText',insets:0}; return q;
}
function base(section,title,kicker=''){
  const s=pres.slides.add();s.background.fill=C.bg;
  box(s,0,0,1280,12,C.orange); txt(s,section.toUpperCase(),58,37,500,20,15,C.teal,true);
  txt(s,title,58,68,1160,76,39,C.ink,true);
  if(kicker)txt(s,kicker,58,147,1160,48,19,C.muted);
  box(s,58,650,1164,1,C.line);txt(s,'LEGAL NLP MINI-PROJECT  •  PILOT RESULTS',58,664,880,18,13,C.muted,true);
  txt(s,String(pres.slides.items.length).padStart(2,'0'),1150,660,72,28,17,C.orange,true,'right');return s;
}
function card(s,x,y,w,h,num,head,body,fill=C.white){box(s,x,y,w,h,fill,C.line,true);txt(s,num,x+22,y+21,52,38,27,C.orange,true);txt(s,head,x+78,y+21,w-104,40,24,C.ink,true);txt(s,body,x+24,y+75,w-48,h-95,19,C.muted);}
function note(s,t){s.speakerNotes.text=t;}

// 1 — cover
{
 const s=pres.slides.add();s.background.fill=C.bg;box(s,0,0,1280,14,C.orange);
 const b=await fs.readFile(path.join(OUT,'assets','mit-logo.png'));
 s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:'Manipal Institute of Technology institutional header supplied in front-page document',fit:'contain',position:{left:108,top:38,width:1064,height:127}});
 txt(s,'AI-BASED SUMMARIZATION AND\nCLAUSE CLASSIFICATION',92,207,1090,134,49,C.ink,true);
 txt(s,'of legal documents using NLP and transformer models',92,354,1090,54,26,C.teal);
 box(s,92,437,1096,2,C.orange);
 txt(s,'Machine Learning mini-project  •  B.Tech. CSE (AI & ML)',92,463,1000,33,20,C.ink,true);
 txt(s,'Vedant jitani  •  240962492  •  Roll 41',92,511,1040,29,19,C.muted);
 txt(s,'Other team members: [Name / ID pending]  •  [Name / ID pending]',92,547,1090,30,17,C.muted);
 txt(s,'Guide: [confirm from supplied documents]  •  Academic year 2026–27',92,586,1090,30,17,C.muted);
 txt(s,'PILOT EXPERIMENT  |  OCTOBER 2026',92,657,1090,21,15,C.orange,true);
 note(s,'Source: supplied synopsis and front-page DOCX. The guide spelling and whether there are one or two guides conflict across the supplied documents, so this remains a placeholder. Two team-member details are missing.');
}
// 2
{
 const s=base('01 / context','One interface, two distinct legal NLP tasks','The outputs support document review; they do not make legal determinations.');
 card(s,58,233,553,317,'01','Judgment summarization','Indian Supreme Court judgments → concise draft summaries.\n\nTraining and evaluation: IN-Abs judgment–headnote pairs.');
 card(s,637,233,585,317,'02','Clause classification','Commercial contract passages → eight possible clause categories.\n\nTraining and evaluation: CUAD, a non-Indian corpus.');
 txt(s,'The two tasks have separate data, models and metrics. No combined “legal accuracy” is claimed.',58,574,1160,53,22,C.orange,true);
 note(s,'The synopsis proposes summarization and clause classification. Actual contract benchmarking uses CUAD from SEC/EDGAR filings, so performance on Indian contracts is unknown. See docs/DATA_CARD.md.');
}
// 3
{
 const s=base('02 / objectives','Three measurable objectives');
 card(s,58,221,370,348,'1','Prepare evidence','Acquire public corpora; verify spans and metadata; split by document; prevent duplicate leakage.');
 card(s,455,221,370,348,'2','Compare models','Benchmark TF-IDF models against fine-tuned LEGAL-BERT and T5-small on the same held-out subsets.');
 card(s,852,221,370,348,'3','Deliver a demo','Accept searchable PDF, DOCX or TXT; show summaries or clause labels; export the output.');
 note(s,'Objectives follow the executed pilot, not the unexecuted full-dataset aspiration. Sources: docs/DATA_CARD.md, docs/EXPERIMENT_RESULTS.md, docs/DEMO_AND_VIVA.md.');
}
// 4
{
 const s=base('03 / prior work','Research basis and project gap','Domain-specific legal language models help, but results depend on corpus and evaluation setting.');
 box(s,58,224,1164,347,C.white,C.line,true);
 txt(s,'Legal-domain encoders',90,249,500,38,25,C.teal,true);
 txt(s,'Use contextual representations for specialist vocabulary and long-form legal structure.',90,298,482,73,20,C.muted);
 txt(s,'Judgment summarization',674,249,500,38,25,C.teal,true);
 txt(s,'Indian case summaries demand outcome coverage, not only lexical overlap.',674,298,480,73,20,C.muted);
 box(s,628,248,1,278,C.line);
 txt(s,'Project gap',90,414,340,36,25,C.orange,true);
 txt(s,'A reproducible, local comparison across both tasks, with visible baselines, data provenance and failure analysis.',90,456,1075,66,22,C.ink);
 txt(s,'Selected literature and dataset citations are on the final slide; full 20-item journal survey is in the report.',58,590,1160,36,17,C.muted);
 note(s,'This is not a novelty or priority claim. Literature survey and indexed bibliography: research/LITERATURE_REVIEW.md and reports/Final_Report.pdf. Operational dataset papers: Shukla et al. AACL 2022 for IN-Abs; The Atticus Project for CUAD.');
}
// 5
{
 const s=base('04 / data','Two public corpora, different jurisdictions','Published corpus sizes and executed pilot sizes are stated separately.');
 box(s,58,223,1164,358,C.white,C.line,true);
 txt(s,'DATASET',82,241,277,32,16,C.teal,true);txt(s,'PUBLISHED',390,241,217,32,16,C.teal,true);txt(s,'RETAINED POOL',660,241,230,32,16,C.teal,true);txt(s,'PILOT',940,241,250,32,16,C.teal,true);
 box(s,82,283,1109,1,C.line);
 txt(s,'IN-Abs\nIndian judgments',82,309,265,89,24,C.ink,true);txt(s,'7,130 pairs\n7,128 usable',390,309,238,83,24,C.ink);txt(s,'5,949 / 1,050 / 100\ntrain / val / test',660,309,260,83,23,C.ink);txt(s,'64 / 12 / 20\njudgment pairs',940,309,250,83,23,C.orange,true);
 box(s,82,416,1109,1,C.line);
 txt(s,'CUAD v1\nCommercial contracts',82,438,270,92,24,C.ink,true);txt(s,'510 contracts\n41 source categories',390,438,238,86,23,C.ink);txt(s,'345 / 61 / 102\ntrain / val / test',660,438,260,86,23,C.ink);txt(s,'40 / 10 / 10\ncontracts',940,438,250,86,23,C.orange,true);
 txt(s,'CUAD is not an Indian contract benchmark.',58,601,1160,31,20,C.orange,true);
 note(s,'IN-Abs: published 7,130 pairs, two empty train pairs; retained pool after grouping 5,949/1,050/100; executed pilot 64/12/20. CUAD v1: 510 published, official 408/102 split; retained 345/61/102; executed pilot 40/10/10. See docs/DATA_CARD.md and dataset URLs in final references.');
}
// 6
{
 const s=base('05 / data engineering','How CUAD becomes multi-label classification','Verified answer spans are projected onto bounded passages; this is weak labeling.');
 card(s,58,225,360,310,'1','Verify source','Reconstruct 510 contracts and check every answer offset against untouched text.');
 card(s,459,225,360,310,'2','Split + segment','Group near duplicates, reserve official test, then create ≤256-token passages.');
 card(s,860,225,362,310,'3','Apply labels','Mark any passage overlapping an answer span; allow multiple of eight labels.');
 txt(s,'Eight labels: Governing Law · Non-Compete · Exclusivity · Anti-Assignment · Termination for Convenience · Cap on Liability · Audit Rights · Post-Termination Services',58,559,1164,71,18,C.muted);
 note(s,'Zero invalid CUAD answer offsets were found. Any-character overlap yields an 8-dimensional binary label, so a positive may include a partial clause; zero means no selected annotation, not legal safety. Training negatives capped at 3 per positive; evaluation retains all. Source: docs/DATA_CARD.md.');
}
// 7
{
 const s=base('06 / method','Long judgment handling is an explicit trade-off','A complete judgment is read for selection, but only selected text enters T5-small.');
 card(s,58,223,360,325,'1','Read + segment','Extract searchable text from PDF, DOCX or TXT; preserve names, citations and negation.');
 card(s,459,223,360,325,'2','Select units','TF-IDF relevance + redundancy control; restore source order under a token budget.');
 card(s,860,223,362,325,'3','Summarize','Compare an extractive baseline with one-epoch fine-tuned T5-small.');
 box(s,58,567,1164,55,C.lightOrange);txt(s,'Pilot cap: 512 selected input tokens → 128 output tokens. Mean selected training-source coverage: 16%.',78,577,1126,35,19,C.orange,true);
 note(s,'All 64 training and all 12 validation target headnotes exceeded the 128-token cap and were shortened; held-out references stayed full length. T5 cannot claim full-document comprehension. Source: docs/DATA_CARD.md.');
}
// 8
{
 const s=base('07 / models','Actual models and training','Baselines remain essential because the fine-tuned models are trained on small pilot samples.');
 box(s,58,220,1164,360,C.white,C.line,true);
 txt(s,'TASK',83,239,250,30,16,C.teal,true);txt(s,'BASELINE',350,239,300,30,16,C.teal,true);txt(s,'FINE-TUNED MODEL',704,239,440,30,16,C.teal,true);box(s,82,280,1106,1,C.line);
 txt(s,'Clause labeling',82,307,251,50,23,C.ink,true);txt(s,'TF-IDF + 8 one-vs-rest\nlogistic regressions',350,306,315,74,21,C.ink);txt(s,'LEGAL-BERT + eight sigmoid outputs\n3 epochs · 1,636 train passages',704,306,469,76,21,C.ink);
 box(s,82,402,1106,1,C.line);txt(s,'Judgment summary',82,429,260,56,23,C.ink,true);txt(s,'TF-IDF / MMR extractive\nselection',350,428,315,72,21,C.ink);txt(s,'T5-small encoder–decoder\n1 epoch · 64 train pairs',704,428,469,73,21,C.ink);
 txt(s,'Runs were CPU-only. Model weights, predictions and metrics are stored locally.',58,595,1164,35,19,C.muted);
 note(s,'LEGAL-BERT trained 3 epochs (723.75 s), T5-small 1 epoch (152.02 s), CPU 4 threads. Checkpoints and metrics in artifacts/pilot. No full-corpus run is claimed.');
}
// 9
{
 const s=base('08 / evaluation','Held-out evaluation and leakage control','Document-level partitions precede passage creation; test data are not used to choose thresholds.');
 card(s,58,227,555,333,'01','Classification','10 held-out CUAD contracts → 2,404 passages. Report macro / weighted F1 and exact multi-label subset accuracy.');
 card(s,639,227,583,333,'02','Summarization','20 held-out Indian judgments. Report ROUGE-1 / ROUGE-2 / ROUGE-L versus full reference headnotes.');
 txt(s,'2,340 of 2,404 classifier test passages have none of the eight selected labels; accuracy alone is misleading.',58,580,1164,55,20,C.orange,true);
 note(s,'Document duplicate groups are separated before splitting; exact repeated cross-split passage strings are quarantined. Approximate duplicate matching is not exhaustive. Threshold chosen on validation macro F1. See docs/DATA_CARD.md and docs/EXPERIMENT_RESULTS.md.');
}
// 10 classification chart
{
 const s=base('09 / results','Clause classification: macro F1 improves','Same 2,404 held-out passages from 10 non-Indian CUAD contracts; scores 0–1.');
 const ch=s.charts.add('bar',{position:{left:74,top:216,width:791,height:358},title:'F1 by averaging scheme',categories:['Macro F1','Weighted F1'],series:[{name:'TF-IDF',values:[0.385,0.409],fill:C.teal},{name:'LEGAL-BERT',values:[0.447,0.509],fill:C.orange}],hasLegend:true,barOptions:{direction:'column',grouping:'clustered',gapWidth:100},dataLabels:{showValue:true,position:'outEnd',textStyle:{fill:C.ink,fontSize:15}},yAxis:{minimumScale:0,maximumScale:0.6,majorUnit:0.1,majorGridlines:{style:'solid',fill:C.line,width:1}},chartFill:'none',plotAreaFill:'none'});
 applyPresentationChartFont(ch,{fontFamily:'Arial'});
 box(s,898,237,324,324,C.white,C.line,true);txt(s,'+0.062',923,270,273,66,42,C.orange,true);txt(s,'macro F1 vs. baseline',923,345,271,53,21,C.ink,true);
 txt(s,'Subset accuracy: 0.970 → 0.972; always-zero prediction would score 0.973 because negatives dominate.',923,417,268,119,18,C.muted);
 txt(s,'Rare classes remain weak; Exclusivity has only 3 positive test passages.',58,592,1164,41,20,C.orange,true);
 note(s,'Exact metrics: TF-IDF macro F1 0.385256, weighted 0.408894, accuracy 0.970050; LEGAL-BERT macro 0.447039, weighted 0.509143, accuracy 0.972130. Test rows 2404, all-zero 2340. Source: artifacts/pilot/tfidf/test/metrics.json and artifacts/pilot/legalbert/test/metrics.json (also docs/EXPERIMENT_RESULTS.md).');
}
// 11 summarization chart
{
 const s=base('10 / results','Summary baseline beats pilot T5-small','Held-out IN-Abs test: 20 Indian judgment–headnote pairs; ROUGE scores 0–1.');
 const ch=s.charts.add('bar',{position:{left:74,top:216,width:795,height:359},title:'ROUGE against full reference summaries',categories:['ROUGE-1','ROUGE-2','ROUGE-L'],series:[{name:'Extractive',values:[0.216,0.120,0.145],fill:C.teal},{name:'T5-small',values:[0.149,0.079,0.105],fill:C.orange}],hasLegend:true,barOptions:{direction:'column',grouping:'clustered',gapWidth:90},dataLabels:{showValue:true,position:'outEnd',textStyle:{fill:C.ink,fontSize:14}},yAxis:{minimumScale:0,maximumScale:0.3,majorUnit:0.05,majorGridlines:{style:'solid',fill:C.line,width:1}},chartFill:'none',plotAreaFill:'none'});
 applyPresentationChartFont(ch,{fontFamily:'Arial'});
 box(s,899,238,323,323,C.white,C.line,true);txt(s,'Why?',923,269,274,47,37,C.orange,true);txt(s,'Only 64 training pairs and 1 epoch. The 512-token selected input covered roughly 16% of training source text on average.',923,333,271,177,20,C.muted);
 txt(s,'Lexical overlap is not a legal-faithfulness test; disposition must be checked against the source.',58,593,1164,40,19,C.orange,true);
 note(s,'Exact scores: extractive R1 0.2164466, R2 0.1200588, RL 0.1445487. T5 R1 0.1494678, R2 0.0797391, RL 0.1045632. All held-out references full length. Source: artifacts/pilot/extractive/test/metrics.json and artifacts/pilot/t5/test/metrics.json.');
}
// 12
{
 const s=base('11 / analysis','Failure analysis: what the scores conceal','Interpretation should follow error cases, not only aggregate averages.');
 card(s,58,219,552,340,'A','Rare clause labels','Three categories have small positive support. The transformer misses some instances and creates false positives.');
 card(s,638,219,584,340,'B','Judgment outcomes','Source selection can omit the final order. Fluent short text can miss the legal disposition or a key qualification.');
 txt(s,'The app exposes source text, selected units and outputs so users can verify them.',58,583,1164,51,21,C.orange,true);
 note(s,'Classification: Exclusivity has 3 positives; Post-Termination Services 8. A reviewed test judgment (~3,542 words) showed disposition omission in a generated summary. These examples motivate source-side checks. See docs/EXPERIMENT_RESULTS.md and reports/Final_Report.pdf.');
}
// 13
{
 const s=base('12 / demonstration','Five-minute local demonstration','The sample texts demonstrate the interface, not benchmark performance.');
 card(s,58,217,360,344,'1','Summarize','Paste a synthetic judgment; compare extractive and T5 outputs; inspect retained source coverage.');
 card(s,459,217,360,344,'2','Classify','Paste a synthetic contract; compare TF-IDF and LEGAL-BERT labels and scores.');
 card(s,860,217,362,344,'3','Export','Save TXT / JSON summary or CSV / JSON clauses; open the report and saved metric JSONs.');
 txt(s,'Input: searchable PDF, DOCX, TXT. Scanned PDFs need OCR outside this app.',58,587,1164,39,20,C.orange,true);
 note(s,'Run scripts/run_demo.ps1 and open localhost:8501. Existing local checkpoints are available in this workspace. Synthetic demo inputs are examples/demo_judgment.txt and examples/demo_contract.txt. The copied ZIP needs setup and retraining. See docs/DEMO_AND_VIVA.md.');
}
// 14
{
 const s=base('13 / conclusion','What this pilot establishes — and what comes next','A transparent baseline-to-transformer comparison is possible on a modest local machine.');
 box(s,58,219,555,353,C.pale,C.line,true);txt(s,'Established',83,245,495,43,28,C.teal,true);
 txt(s,'• Reproducible preprocessing and held-out splits\n• Genuine LEGAL-BERT and T5 fine-tuning\n• Working local demo and export\n• Baselines expose mixed outcomes',83,309,498,230,21,C.ink);
 box(s,639,219,583,353,C.lightOrange,C.line,true);txt(s,'Next work',664,245,520,43,28,C.orange,true);
 txt(s,'• Full-corpus experiments\n• Independent Indian contract annotations\n• Longer-input summarization and OCR\n• Expert review of summary faithfulness',664,309,523,231,21,C.ink);
 txt(s,'Use the system as review assistance, with the source document beside every output.',58,592,1164,38,19,C.orange,true);
 note(s,'Do not characterize the pilot as validated for Indian contract review. Full-corpus configuration exists but has not been executed. Other work includes multilingual evaluation and calibrated probabilities. Source: docs/DATA_CARD.md and docs/DEMO_AND_VIVA.md.');
}
// 15
{
 const s=base('14 / references','Sources and reproducibility','Selected sources; the final report contains the full literature review and 20 journal references.');
 box(s,58,214,1164,388,C.white,C.line,true);
 txt(s,'DATA',83,239,171,27,17,C.teal,true);
 txt(s,'IN-Abs: Shukla et al., AACL 2022; Zenodo DOI 10.5281/zenodo.7152317.\nCUAD v1: The Atticus Project, 2021; github.com/The-Atticus-Project/cuad.',268,238,918,80,18,C.ink);
 box(s,83,333,1108,1,C.line);txt(s,'MODELS',83,356,171,28,17,C.teal,true);
 txt(s,'Chalkidis et al., “LEGAL-BERT,” Findings of EMNLP 2020.\nRaffel et al., “Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer,” JMLR 2020.',268,354,922,95,18,C.ink);
 box(s,83,467,1108,1,C.line);txt(s,'PROJECT',83,490,171,28,17,C.teal,true);
 txt(s,'reports/Final_Report.pdf  ·  docs/DATA_CARD.md\ndocs/EXPERIMENT_RESULTS.md  ·  artifacts/pilot/*/test/metrics.json',268,489,916,84,18,C.ink);
 note(s,'Dataset URLs: https://zenodo.org/records/7152317 ; https://www.atticusprojectai.org/cuad ; https://github.com/The-Atticus-Project/cuad . Paper URLs and verified bibliography metadata are in research/bibliography-ieee.txt and reports/Final_Report.pdf. Local source documents: templates/.');
}

await fs.mkdir(path.join(OUT,'renders'),{recursive:true});
for(let i=0;i<pres.slides.items.length;i++){
 const png=await pres.export({slide:pres.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(OUT,'renders',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const staging=path.join(OUT,'.codex-finalizer');await fs.mkdir(staging,{recursive:true});await fs.mkdir(path.dirname(FINAL),{recursive:true});
const candidate=path.join(staging,'candidate.pptx');await (await PresentationFile.exportPptx(pres)).save(candidate);
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:FINAL,pythonExecutable:PYTHON,integrityValidatorPath:path.join(SKILL,'container_tools','inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools','inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],requiredNativeChartOwnerSlides:[10,11],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(staging,'presentation.validation.json')});
console.log(JSON.stringify({slides:pres.slides.items.length,result,final:FINAL}));
