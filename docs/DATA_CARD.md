# Data and task contract

These are two independent supervised tasks in one interface. No judgment is treated as a contract and no shared score combines the two tasks. Only summarization is evaluated on Indian documents. Clause classification is an English CUAD benchmark; transfer to Indian contracts is unverified.

## IN-Abs

Original release: Shukla et al., *Legal Case Document Summarization: Extractive and Abstractive Methods and their Evaluation* (AACL 2022, conference; operational provenance only). Authors' repository: https://github.com/Law-AI/summarization/tree/aacl/dataset . Archive: https://zenodo.org/records/7152317 , DOI 10.5281/zenodo.7152317. Access is public, no scraping/login. Zenodo API identifies CC BY 4.0; preserve author attribution and release metadata. English Indian Supreme Court judgments and corresponding abstractive headnotes collected from LII of India. Existing summaries are references, not new annotations made by this project.

Published 7,130 pairs: 7,030 train, 100 test. Actual ZIP contains two empty training pairs (299.txt and 4799.txt), leaving 7,128 usable pairs. Duplicate grouping removes 27 exact duplicates and links two near-duplicate pairs. Retained pool: 5,949 train / 1,050 validation / 100 official test. The executed pilot uses 64 / 12 / 20 pairs, selected deterministically with seed 42. Official test is never used for model/threshold selection. Full data preparation and training are available but not executed as a full experiment.

## CUAD v1

Original source: The Atticus Project, https://www.atticusprojectai.org/cuad ; repository https://github.com/The-Atticus-Project/cuad at commit `67faa0e6023b04fcaae6cc09497ab00e5d63a2a2`. Public ZIP `data.zip`, CC BY 4.0. English commercial contracts from SEC/EDGAR filings, with expert-supervised annotations. These are **not an Indian contract corpus**. Published 510 contracts, 41 annotation categories, over 13,000 annotations. Actual full JSON has 510 contracts, official 408 train / 102 test. `train_separate_questions.json` repeats contexts by question: treating its entries as independent contracts would leak data. We reconstruct documents from `CUADv1.json` and identify official test titles from `test.json`.

Original format is SQuAD-like question answering: `data -> paragraphs -> context / qas -> answers`, with character `answer_start` and answer text. It is not a pre-existing sentence classification dataset. Every answer offset was checked against the untouched context: zero invalid offsets. Contexts are not whitespace-normalized before mapping spans.

The implemented schema is **multi-label**, eight fixed categories in this order:

| Category | Operational meaning (paraphrased from CUAD definitions) |
|---|---|
| Governing Law | Law/jurisdiction designated to govern the agreement |
| Non-Compete | Restriction on competing with a party or conducting competing activities |
| Exclusivity | Exclusive dealing or exclusive relationship obligations |
| Anti-Assignment | Restriction or required consent for assignment of rights/obligations |
| Termination For Convenience | Termination without cause, commonly subject to notice |
| Cap On Liability | Ceiling on a party's liability under the agreement |
| Audit Rights | Right to inspect/audit records, accounts or compliance |
| Post-Termination Services | Continuing services or transition assistance after termination |

An overlapping passage may have several labels. Labels locate clause types, not enforceability, unlawfulness, risk severity or legal advice. Full original definitions are in `research/cuad-label-definitions.csv`. Categories omitted from the 41-label source remain outside this experiment's scope.

Split documents before creating passages. Line-aware sentence/word segmentation uses at most 100 whitespace words, recursively split to at most 256 LEGAL-BERT tokens, preserving offsets. A segment is positive for a category if it overlaps any verified source answer span by at least one character. This weak conversion can label partial clauses and does not recover exact answer boundaries. A zero vector means no selected annotation, not verified legal neutrality. BCE-with-logits and eight sigmoid outputs match this schema. TF-IDF uses eight one-vs-rest logistic regressions.

One exact duplicate and one near-duplicate link yield a retained pool of 345 train / 61 validation / 102 test contracts. Pilot: 40 / 10 / 10 contracts, yielding 1,636 / 2,639 / 2,404 segments. Training negatives are capped at three per positive segment; validation/test preserve all remaining segments. Exact repeated cross-split segment strings are quarantined from train (1,412) then validation (331), with test priority. The same held-out segments are evaluated by both classifiers. Label support and identifiers are recorded in the preparation JSON and manifests.

## Leakage controls and remaining limits

Normalized SHA-256 identifies exact document duplicates. An approximate bottom-64 sketch of five-word shingles (candidate search via eight minima, Jaccard threshold 0.9) groups likely near duplicates before splitting. This is not an exhaustive plagiarism or semantic-overlap detector. Keep one representative per duplicate group, prioritize official test and quarantine any training group intersecting official test. Validation is 15% of the remaining official training groups before pilot selection. Group IDs, exact normalized text and document IDs are disjoint; classification also excludes exact repeated segment text across partitions. Train sampling uses no test scores.

Selector sees all judgment units and reports retained spans/coverage. It does not send all content to T5: input limit 512 tokens; targets 128 tokens. All 64 training and all 12 validation targets exceeded 128 tokens and were explicitly shortened for training. ROUGE uses full, unshortened test references. Mean selected training character coverage is only 16.0%; omissions are a central limitation. The short-output cap is a deliberate CPU pilot constraint, not full-document comprehension.

Input formats: UTF-8 TXT, DOCX paragraph/table text, searchable PDF. No OCR is installed; scanned pages produce a clear warning/error, and mixed PDFs may have missing pages. Names, dates, amounts, negation and citations are retained; no stemming/stopword deletion is applied to model inputs. PDF layout order and table extraction can remain imperfect.

Archive sizes, URLs, MD5 and SHA-256 are in `data/raw/downloads.json`. Raw data, caches and weights are excluded from the delivery ZIP; acquisition is reproducible. Data are available locally in the workspace, not uploaded to an external service by the demo.
