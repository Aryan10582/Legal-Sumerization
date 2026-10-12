# Operational source record (not the journal bibliography)

Checked 12 October 2026. Journal citations are separately numbered in `research/bibliography-ieee.txt`; datasets, model cards, software and conference papers below are deliberately not disguised as journal references.

| Item | Primary record / interpretation |
|---|---|
| IN-Abs | https://zenodo.org/records/7152317 and https://github.com/Law-AI/summarization/tree/aacl/dataset ; 7,130 published pairs, CC BY 4.0 in Zenodo metadata. AACL 2022 original dataset paper is conference provenance. |
| CUAD | https://www.atticusprojectai.org/cuad and https://github.com/The-Atticus-Project/cuad ; expert-annotated SEC commercial contracts, 41 QA categories, CC BY 4.0. NeurIPS 2021 original dataset paper is conference provenance. |
| LEGAL-BERT SMALL | https://huggingface.co/nlpaueb/legal-bert-small-uncased ; 6-layer BERT encoder, 35,072,520 parameters with our eight-label head. Revision `0e23f7a9a39f59768ea7e09766d8ee308580fb17`. Original legal pretraining covers diverse UK/EU/US legal material; no Indian specialization claimed. Model card CC BY-SA 4.0; retain attribution and share-alike requirements for derivative weights. Original Chalkidis et al. EMNLP Findings 2020 model paper is conference provenance. |
| T5 SMALL | https://huggingface.co/google-t5/t5-small ; encoder-decoder, 60,506,624 parameters, generic text-to-text model. Revision `df1b051c49625cf57a3d0d8d3863ed4d13564fe4`. Apache 2.0 model license. Raffel et al., JMLR 2020, *Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer*, https://www.jmlr.org/papers/v21/20-074.html . Operational model paper; not added solely to fill the required legal-journal list. |
| Model API metadata | Exact revisions and card license fields cached in `research/legalbert-model.json` and `research/t5-model.json`. |
| ROUGE | Lin, ACL 2004 workshop, https://aclanthology.org/W04-1013/ ; implementation https://github.com/google-research/google-research/tree/master/rouge . `rouge-score` 0.1.2, Porter stemming, default lowercase alphanumeric tokenization, F1, document arithmetic mean, ROUGE-L (not Lsum), full references. |
| Transformers | https://huggingface.co/docs/transformers/index ; local installed 5.19.0 verified by execution. |
| PyTorch | https://pytorch.org/ ; installed CPU 2.14.1, actually executed. GPU instructions require selecting a build appropriate to the user's CUDA system. |
| Streamlit | Installed 1.65.0 and its bundled version-matched documentation inspected. https://docs.streamlit.io/ |
| Indian Kanoon | https://indiankanoon.org/ is a search/retrieval source, not assumed to provide a downloadable licensed judgment–summary supervision archive. Not scraped here. |
| NJDG | https://njdg.ecourts.gov.in/ is a judicial data portal. Access during verification was unavailable; a paired, annotated summarization download and reuse license were not established. Not used as a dataset. |
| Supplied IEEE body | https://attend.ieee.org/procomm-2024/wp-content/uploads/sites/580/2024/03/Full-Paper-template.docx ; actual DOCX downloaded and inspected. Hash and layout contract in `reports/artifact.md`. |

## Why these model changes are justified

The synopsis lists BERT/LEGAL-BERT, BART, PEGASUS and Longformer candidates. A BERT encoder supplies contextual representations and a classifier head; it is not a text generator. Longformer by itself is an encoder with sparse attention; accepting a longer sequence does not create a summarizer. A configured encoder-decoder such as LED is a different generative architecture. T5 is a genuine generator and its small model makes actual CPU fine-tuning practical. This project substitutes T5-small for larger BART/PEGASUS experiments and uses deterministic full-judgment selection before generation. It does not claim to have trained all synopsis candidates or to have solved information loss from long documents.

## Literature evidence limits

Twenty relevant journal articles were selected, 17 dated 2020 or later and three older foundations. All nineteen synopsis entries were audited individually. Crossref/publisher metadata distinguish online-first dates from final issue years. `research/indexing-evidence.json` records journal-level evidence. Eighteen final entries have publisher-stated Scopus/WoS journal coverage; the two Automation in Construction entries have institutional primary Scopus evidence, with direct source-list access blocked. Confirm current article/year coverage through the MIT library before claiming an authenticated database audit. Crossref registration alone is not proof of indexing. Public abstracts rather than complete subscription articles support some method summaries; no unobserved numeric claim is attributed to them.

Author spelling caveat for the original synopsis reference 17: Crossref gives “Sangchoconanta” / “Chaiurangsri”, while author-paper/other bibliographic records use “Sangchocanonta” / “Chairuangsri”. This is a source disagreement, not a certain correction. The final template's first-author-et-al. format avoids silently resolving it; see the full metadata record.
