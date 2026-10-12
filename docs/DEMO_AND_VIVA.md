# Demonstration (about five minutes)

1. From the project root run `powershell -ExecutionPolicy Bypass -File scripts/run_demo.ps1`; open http://localhost:8501 . Existing local checkpoints are available in this workspace. The offline launcher avoids network checks. A fresh copied package must first acquire data/models and run training.
2. Choose Judgment summarization / Extractive baseline. Paste `examples/demo_judgment.txt`. Explain that this is a small synthetic input for interface demonstration, not a scored test judgment. Process; compare the original and summary. Export TXT and JSON. Show selected-unit count and retained source fraction.
3. Choose Fine-tuned T5 and repeat. Explain its 512-token selected input / 128-token output limit, one-epoch pilot and need to verify disposition. A plausible sentence is not proof of faithful reasoning.
4. Switch to Clause classification. Paste `examples/demo_contract.txt`; run TF-IDF, then LEGAL-BERT. Export CSV/JSON. Show overlapping categories and uncalibrated scores. This synthetic Indian-law wording is a demonstration of operation, not an Indian contract accuracy benchmark.
5. Open `reports/Final_Report.pdf` and actual metrics in `artifacts/pilot/*/test/metrics.json`. Explain why high subset accuracy can coexist with poor rare-label F1. Mention the official test restrictions, tiny pilot and larger unexecuted config.
6. Upload a searchable PDF/TXT/DOCX if desired. A scanned PDF requires OCR outside this app. The local app does not save uploaded documents; output exports are user actions.

## Likely viva questions

**Why combine two tasks?** They support reading different legal documents through one interface. Each has separate sources, models, labels and metrics; no shared accuracy or common supervision is implied.

**Is the whole system trained on Indian law?** No. IN-Abs is Indian Supreme Court summarization. CUAD is commercial contract data from SEC filings; Indian contractual transfer has not been evaluated.

**Why multi-label?** One segment may overlap several CUAD answer categories. Eight sigmoid outputs and binary cross-entropy model independent labels; softmax would incorrectly force one category. The baseline uses one-vs-rest logistic regression.

**How did QA become classification?** Verified character spans are overlaid on line-aware, token-bounded passages. Any overlapping category sets a binary label. This weak labeling can include partial clauses. Zero labels mean no selected annotation, not safety.

**How is leakage prevented?** Documents are grouped for exact/approximate duplicates before splitting, official test retained, validation drawn from train groups. Then segments are created and exact repeated segment texts removed from lower-priority splits. Sketch matching cannot guarantee all semantic duplicates are found.

**Why does a simple model sometimes win?** Sparse lexical indicators work well on clause boilerplate. Pilot transformer training is small, imbalance is severe and validation support is low. A fine-tuned transformer is not automatically better.

**What was genuinely fine-tuned?** All LEGAL-BERT parameters and its eight-output head for three epochs on 1,636 segments from 40 contracts; T5-small for one epoch on 64 judgment–summary pairs. Checkpoint metadata record seed, revision, hardware, timing and data hashes.

**Why not Longformer?** An encoder accepting long input is not inherently a generator. A generative LED setup would require different checkpoints/training and more resources. This version uses a genuine small encoder-decoder with measured selection loss.

**How are long judgments handled?** Full text is divided into units, scored by TF-IDF centroid relevance and maximum-marginal-relevance redundancy penalty, selected under the budget and restored to source order. Only selected text goes to T5. Coverage is visible; important content can be omitted.

**What does ROUGE measure?** Stemmed token/n-gram and longest-common-subsequence overlap with full reference headnotes. It does not establish legal faithfulness or preserve every named entity/outcome. Qualitative examples are needed.

**Which accuracy?** Exact multi-label subset accuracy: every label must match for a segment. It is dominated by many all-zero segments. Macro F1 weights categories equally; weighted F1 weights support. Each label has its own TN/FP/FN/TP confusion matrix.

**How was the threshold chosen?** One global threshold for each classifier, selected using validation macro F1 over 0.10–0.90, step 0.05. The held-out test did not choose it. Scores are not calibrated confidence.

**Can you resume training?** Saved checkpoints reload for inference. Optimizer/scheduler state is not saved, so exact interrupted training resume is not supported. A new training run starts from the pinned base model; code can be extended for warm-start training.

**What is unfinished?** Full corpus runs, independent Indian contract labels/testing, OCR, multilingual data, calibrated probabilities, expert faithfulness checks and authenticated indexing/Turnitin submission checks. Team/guide placeholders must be completed.
