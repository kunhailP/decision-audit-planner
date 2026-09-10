# TMLR submission checklist (OpenReview) — 2026-09-10

## Before upload
- [ ] `main.tex` compiles with `\usepackage{tmlr}` (anonymous); no author names, acknowledgements, or identifying URLs in the PDF.
- [ ] Code link: anonymised. Options: (a) Anonymous GitHub mirror of `nonneutral-judge-audit` (keep the real repo private during review),
      (b) zip of the release directory uploaded as supplementary material. Do not link `github.com/kunhailP/...` in the PDF.
- [ ] Remove `06_paper/tmlr_submission/preview/` and build logs from any uploaded archive (already git-ignored).
- [ ] Figures: F4 (gain vs ρ), F5 (ACT vs budget), F6 (mechanism map), F7 (J50) present at ≥150 dpi; Tables: J50, self-preference, pre-registered runs, locks, confirmatory.
- [ ] Reproducibility statement (Appendix C) mentions seeds, per-method random streams, position-ids fix, judge versions (Qwen3-8B, Qwen3-Reranker-0.6B, Mistral-7B-Instruct-v0.3), pool builders, and that all numbers regenerate from row-level files.
- [ ] Broader-impact statement: judges may be non-neutral toward policies built from their own family; the certificate does not depend on the judge; misuse risk is over-trusting an AI judge without human labels.
- [ ] Data licences: BEIR (dataset-specific), MS MARCO (non-commercial research), TREC DL/CAsT qrels (NIST), ANTIQUE (research). No redistribution of corpora in the release; only judged-pool CSVs.

## OpenReview fields
- Title: as in `main.tex`. Abstract: as in `main.tex`. Keywords: prediction-powered inference; active inference; LLM-as-a-judge; retrieval evaluation; policy certification; pre-registration.
- Certification request: **none at submission** (Featured/Outstanding are decided by the AEs/reviewers).
- Conflict-of-interest and reviewer suggestions per TMLR policy.

## After acceptance
- [ ] `\usepackage[accepted]{tmlr}`, author block, acknowledgements, real code link (make `nonneutral-judge-audit` public).
- [ ] Tag the release repository (`v1.0-tmlr`) and archive it (Zenodo DOI) for the camera-ready.
