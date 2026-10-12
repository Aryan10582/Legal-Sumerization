# Legal document lab

**AI-Based Summarization and Clause Classification of Indian Legal Documents Using NLP and Transformer Models**

Runnable undergraduate mini-project, genuine CPU fine-tuning and a measured pilot. Summarization uses Indian judgments; contract classification uses non-Indian CUAD data. Read `docs/ACADEMIC_CHECKLIST.md` before submission: missing team/guide fields, Turnitin and final library indexing checks remain.

## What is included

`src/legal_nlp/` contains acquisition, duplicate grouping, document-first splits, span conversion, training, evaluation and local inference. `app.py` offers upload/paste, separate tasks, source/output comparison and TXT/CSV/JSON export. `config.yaml` reproduces the executed pilot; `config.full.yaml` proposes an unexecuted larger run. `artifacts/pilot/` contains real model metadata, training logs, local checkpoints, test predictions and scores. `reports/` contains editable DOCX/PDF and template/visual QA. `templates/` preserves the supplied reference files and retrieved IEEE template for report regeneration. `research/` holds the 19-entry synopsis audit, twenty journal references, indexing evidence and analytical survey. `docs/` provides data/provenance, requirements, demo and viva notes.

## Setup (Python 3.12 recommended; tested on Windows CPU)

Run from the project root. Existing `.venv` and checkpoints are ready in this workspace. For a new checkout:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m pip install --no-deps -e .
$env:HF_HOME=(Join-Path (Get-Location) 'artifacts\hf-cache')
$env:HF_HUB_DISABLE_XET='1'
.venv\Scripts\python.exe -m legal_nlp download
.venv\Scripts\python.exe -m legal_nlp prepare
.venv\Scripts\python.exe -m legal_nlp baseline
.venv\Scripts\python.exe -m legal_nlp train --task classification
.venv\Scripts\python.exe -m legal_nlp train --task summarization
```

The lock file records versions actually installed together; `pip check` passed. It is a Windows CPU environment lock; other operating systems/GPU installations should install a suitable official PyTorch build, then `pip install -e .` using `pyproject.toml`, and save their own freeze/hardware record. No CUDA/VRAM is assumed. Downloads require network access; the extractive demo itself does not need model weights. First-time baseline preparation requires the pinned segmentation tokenizer. Only locally generated trusted joblib checkpoints should be loaded.

```powershell
.venv\Scripts\python.exe -m legal_nlp evaluate --task classification --model tfidf
.venv\Scripts\python.exe -m legal_nlp evaluate --task classification --model legalbert
.venv\Scripts\python.exe -m legal_nlp evaluate --task summarization --model extractive
.venv\Scripts\python.exe -m legal_nlp evaluate --task summarization --model t5
powershell -ExecutionPolicy Bypass -File scripts/run_demo.ps1
```

Open http://localhost:8501 . Alternatively set `HF_HOME` above and run `.venv\Scripts\python.exe -m streamlit run app.py`. The offline launcher expects existing trained classifiers/T5 and the cached tokenizer. Before a fresh download/training session remove offline flags if set: `Remove-Item Env:HF_HUB_OFFLINE,Env:TRANSFORMERS_OFFLINE -ErrorAction SilentlyContinue`.

## Actual pilot results

Seed 42; CPU, 15.3 GiB system RAM, four PyTorch threads, no GPU. Same held-out data within each task. Classification: 40/10/10 contracts and 1,636/2,639/2,404 derived segments. Summarization: 64/12/20 pairs.

| Classifier | Macro P | Macro R | Macro F1 | Weighted F1 | Subset accuracy |
|---|---:|---:|---:|---:|---:|
| TF-IDF + logistic regression | .419 | .386 | .385 | .409 | .970 |
| Fine-tuned LEGAL-BERT small | .435 | .565 | .447 | .509 | .972 |

| Summarizer | ROUGE-1 F1 | ROUGE-2 F1 | ROUGE-L F1 |
|---|---:|---:|---:|
| TF-IDF / MMR extractive | .216 | .120 | .145 |
| Selected-input fine-tuned T5 small | .149 | .080 | .105 |

LEGAL-BERT trained for 723.75 s over three epochs; T5 152.02 s over one epoch (pipeline timing includes model initialization/preparation). Extractive summarization outperformed T5 on this pilot. Results are not full-corpus benchmarks or evidence of Indian contract accuracy. Of 2,404 test passages, 2,340 have no selected annotation; always predicting zero would score .973 subset accuracy, exceeding both classifiers, but macro F1 zero. Use macro/class-wise F1 rather than accuracy alone. T5 has 512 selected input / 128 generated token limits; all training references were shortened. Full references are used in ROUGE. ROUGE cannot certify legal faithfulness.

Classification test prediction timing: see metrics JSON (model loading excluded). Summary timing includes full-source selection plus generation, excludes model loading. Times are environment-dependent single-run observations. Per-label P/R/F1/support/AP and 2×2 TN/FP/FN/TP, full predictions and traces are available, not a misleading single-label confusion matrix.

## Checks

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\validate_project.py
```

Validation covers legal text preservation, offsets, splitting/duplicate quarantine, actual prepared-split disjointness, token bounds, ROUGE/multi-label calculations, DOCX/table extraction, scanned-PDF errors, checkpoint reload, four inference paths and Streamlit form processing. `artifacts/validation.json` records executed checks. A separate startup health check and rendered reports are recorded in `reports/QA.md`. Synthetic demo inputs are clearly marked and are not test evidence.

## Larger GPU or hosted-notebook run (not executed)

Use `config.full.yaml` and `prepare --full` to include all retained groups in separate output directories. A suitable GPU-enabled PyTorch install is required to use CUDA. `device: auto` selects CUDA only if available. Reduce `batch_size` to 1 and increase `accumulation_steps` if memory is insufficient; do not assume a particular GPU model or paid platform.

```powershell
.venv\Scripts\python.exe -m legal_nlp --config config.full.yaml prepare --full
.venv\Scripts\python.exe -m legal_nlp --config config.full.yaml baseline
.venv\Scripts\python.exe -m legal_nlp --config config.full.yaml train --task classification
.venv\Scripts\python.exe -m legal_nlp --config config.full.yaml train --task summarization
```

Evaluate with the same `--config config.full.yaml` before the subcommand. Run all four evaluation commands above. To display a full-run checkpoint in the demo, back up the pilot config and set `data_dir` / `output_dir` to the full paths; do not overwrite pilot evidence. A hosted notebook can execute the same CLI commands after placing this package in its working directory (`!python -m pip install -e .`); no notebook-specific dataset scraping is needed. Training checkpoints save weights/tokenizer; optimizer/scheduler state is not saved and CLI training starts from the pinned base model. Exact interrupted resume is not implemented.

## Troubleshooting and scope

- Missing checkpoint: run the corresponding training command, or use Extractive baseline for offline judgment summarization. No random classifier head is exposed as a trained model.
- Hugging Face failure: check network, remove offline flags, keep the pinned revision, set `HF_HOME` to this project. Windows symlink-cache warnings do not affect model calculations.
- Checksum/mismatched manifest error: keep original archives; regenerate preparation and retrain in a new output directory. Do not evaluate a checkpoint on a differently prepared split.
- Slow or out-of-memory: use batch size 1, four or fewer CPU threads, and a smaller pilot; record changed settings and regenerate results. Full data runs take substantially longer.
- Scanned PDF: OCR externally, verify the resulting text and upload searchable text. Mixed text/scanned PDFs may omit pages; warnings must be reviewed.
- Empty/unsupported files, non-UTF-8 TXT, invalid/encrypted PDFs and inputs exceeding 20 MB / 300,000 characters produce errors. English only; other languages are outside evaluation.
- DOCX/PDF headings/tables may lose visual reading structure. Always compare extracted text with the original.

Raw data and pretrained/fine-tuned weights are excluded from the ZIP to avoid bulky redistribution; they are present in this workspace. Reacquisition scripts and licenses/attribution are supplied. No credentials are included. The application processes locally, binds to localhost and does not save uploads. It is a teaching/research aid; labels do not assert legal validity or safety.
