# Audits for What? Decision-Specific Planning of Human Audit Budgets for Retrieval Under Distribution Shift

Draft v0.3 — 2026-08-25. Target: TMLR. 상태: development 증거까지 반영,
prospective(C4) 섹션은 protocol만. 모든 수치는 `05_results/` row-level
artifact에서 재생성 가능.

## Abstract (draft)

Retrieval pipelines deployed under distribution shift require human audits of
the target domain before their outputs can be trusted. We show that the
question "how many audits are enough?" has no single answer: on the same
audited sample, **recalibrating** a fixed retrieval rule and **selecting**
among candidate policies demand systematically different evidence. Reanalyzing
13 BEIR collections with a pooled LODO candidate pipeline, we find that ~10
audited queries typically suffice to calibrate a scalar correction to within
0.005 set-F1 of its full-target reference, while certifying an ε-regret
(ε=0.01) policy selection can require 50–100 audits or remain impossible —
and the driver is not the decision's name but the gap structure of the policy
menu. We formalize this as a **Decision-Specific Audit Planner** that takes a
decision, a tolerance and a risk level, and sequentially outputs
*act / collect-more-audits / abstain* with an empirically calibrated
certificate. In controlled simulation the planner's wrong-certificate rate
stays below the nominal α across a gap × menu × noise grid, and its stopping
budget scales with the identified mechanism. Replaying the planner on the 13
development collections yields an overall wrong-certificate rate of 0.035
(nominal α=0.1) while adapting its budget from 10 to 90 audits per collection;
we further show that naive in-sample certificates are anticonservative (up to
36% wrong-certificate rate on one collection) and that leave-one-out
cross-fitting restores validity while *reducing* the audit budget. A utility
ablation reverses the asymmetry's direction (under recall, selection is
near-free and recalibration is the bottleneck), pinning the phenomenon to the
decision × utility × menu geometry rather than the decision's name. We release row-level artifacts sufficient to
regenerate every number, and pre-register a prospective validation protocol on
a collection never touched during development.

## 1. Contributions (claim ladder)

- **C0 (corrective)**: the prior study's "k=10 labels" are 10 *audited
  queries*; its per-query artifact is dataset-level. We restore the missing
  candidate-level artifacts with provenance and reproduce the legacy results
  byte-identically. [DONE: EVIDENCE_RECOVERY_2026-08-25]
- **C1 (diagnostic)**: on the same audit sample, recalibration and selection
  have systematically different budget requirements (F1). Development-data
  finding; heterogeneity is real and mechanistic, not nominal.
- **C2 (method)**: a sequential planner with decision-specific certificates;
  validity requires cross-fitting (new empirical observation on why).
- **C3 (mechanism)**: budget differences are explained by menu size × policy
  gap × per-query variance (F3), not by the decision label.
- **C4 (generalization, first prospective evidence)**: on a collection never
  touched during development (cqadupstack-android; rule-selected and locked
  before download, lock sha256 7a00b578…), the frozen planner **passed the
  pre-registered criterion for both decisions**: wrong-certificate rate 0.00
  (recalibration) and 0.08 (selection) vs nominal α = 0.1 (50 repeats,
  MC SE ≈ 0.042). One external collection; a second (BRIGHT) is contracted
  for revision.

## 2. Setup

Policies (frozen menu, from the legacy study): `ad_probe` (expected-F1 gate
with probe-calibrated scalar ĉ), `glob_probe` (probe-tuned global threshold),
`trunc` (learned truncation transferred via LODO). Reference: `ad_c`, the
*full-target scalar reference* (not an oracle policy). Utility: set-F1
(primary); recall and binary nDCG as sensitivity. Cost axes: T = audited
queries (primary), B = pair-judgment pool size (reported as a proxy only;
pooled qrels prevent honest per-pair cost claims).

Decisions:
- **Recalibration**: choose ĉ; loss = |mean-utility(gate(ĉ)) −
  mean-utility(gate(c*))| on unaudited queries; tolerance ε_cal = 0.005.
- **Selection**: pick m̂ from the menu; loss = regret vs the best menu policy
  on unaudited queries; tolerance ε_sel = 0.01.

## 3. The decision asymmetry (C1, development data)

Fixed-budget curves over k ∈ {5,10,20,50,100}, 50 repeats, probe/eval disjoint
(F1_budget_curves.png):

- Mean calibration loss at k=5 is already ≤~0.006 on 10/13 collections; mean
  selection regret at the same k is 0.02–0.06.
- Success-rate framing (rate ≥ 0.9): recalibration 5/13 at k=10; selection
  3/13 at k=10, 10/13 only at k=100.
- Heterogeneity (→C3): trec-covid certifies selection at k=5 (huge gap);
  scifact/fiqa/climate-fever never reach 0.9 by k=100 (near-tied menus);
  quora is a *recalibration* failure case (dispersed nG/Σp ratios) — the
  asymmetry is mechanistic, not a property of the decision's name.

## 4. The planner (C2)

Frozen spec (FREEZE_PROPOSAL_v0.3): looks T ∈ {10,30,50,70,90} (≤ n/2),
α=0.1, Bonferroni-corrected paired-bootstrap certificates; outputs act /
collect-more / abstain. Recalibration certificate = utility-scale stability of
the gate over a look-corrected bootstrap CI for c. Selection certificate =
max-UCB of competitor advantages over the LCB-chosen candidate.

### 4.1 Validity statement

We state precisely what the certificates guarantee and what is empirical.

**Proposition 1 (selection certificate validity under exact bounds).**
*Fix looks t = 1..L and a menu of M policies with population mean utilities
μ_1..μ_M on the target query distribution. Suppose that at every look t and
for every competitor j ≠ m̂_t, the quantity U_{t,j} used by the procedure is a
valid level-(1−α′) upper confidence bound for μ_j − μ_{m̂_t}, with
α′ = α / (L(M−1)). Then the probability that the planner ever ACTs on a policy
whose true regret exceeds ε_sel is at most α.*

*Proof.* If the planner ACTs at look t on m̂_t with true regret > ε_sel, let
j\* = argmax_j μ_j. Then μ_{j\*} − μ_{m̂_t} > ε_sel ≥ U_{t,j\*}, i.e. the UCB
for comparison (t, j\*) failed to cover. By a union bound over the L(M−1)
comparisons, the probability of any UCB failure is at most L(M−1)·α′ = α. ∎

**Proposition 2 (recalibration certificate validity).** *Suppose at each look
the interval C_t is a valid level-(1−α/L) confidence set for the target scalar
c_T, and let U_cal(t) = max_{c∈C_t} |u(c) − u(ĉ_t)| where u is the population
utility of the gate as a function of the scalar. If the planner ACTs when
U_cal(t) ≤ ε_cal, then P(ACT with |u(ĉ_t) − u(c_T)| > ε_cal) ≤ α.*

*Proof.* On the event c_T ∈ C_t (which fails with probability ≤ α/L per look),
|u(ĉ_t) − u(c_T)| ≤ max_{c∈C_t} |u(c) − u(ĉ_t)| = U_cal(t) ≤ ε_cal. Union
bound over looks. ∎

**What is empirical.** Two steps are approximations that we validate rather
than prove: (i) bootstrap quantiles are only asymptotically valid UCBs/CIs
(standard bootstrap consistency for smooth functionals; sampling without
replacement makes the i.i.d.-based bootstrap conservative if anything);
(ii) in Proposition 2 the population utility u(·) is estimated on the audited
sample. For (i)–(ii) we rely on the 36-cell simulation and the development
replay, which show wrong-certificate rates at or below α at the audit sizes
used. Hence "empirically calibrated certificates." Cross-fitting (below)
is what makes the per-query utilities entering Proposition 1 approximately
unbiased for deployment behavior; without it the UCB premise is violated in
practice and the guarantee visibly fails.

**Cross-fitting is load-bearing.** With in-sample probe utilities
(parameters ĉ, τ̂ estimated and evaluated on the same probe), the selection
certificate is anticonservative: on scifact the wrong-certificate rate reaches
0.36 vs nominal α=0.1 (ablation preserved in
`05_results/planner_replay_insample_ablation/`). Leave-one-out cross-fitting
of per-query policy utilities restores per-collection validity:
[PENDING: cross-fit table].

## 5. Simulation validation (C2 coverage, C3 mechanism)

Synthetic DGP, 36 selection cells (gap × M × σ, 200 reps each), 400-draw
bootstrap (F3_mechanism_map.png):

- **Risk control**: wrong-certificate rate ≤ α in all 36 cells (max 0.09).
- **Mechanism**: mean stopping budget falls from ~84 (gap ≤ 0.01) to ~17–36
  (gap = 0.1); abstention rises to 0.55–0.99 as gap → 0 and with menu size
  M: 2→5. Selection difficulty is gap × M × σ, confirming C3.
- **Recalibration arm**: budget scales with ratio dispersion s (mean T 26 at
  s=0.3 vs 89 at s=1.0) and is independent of the menu — the two decisions
  live on different budget axes by construction.
- The simulation also *selected the interval method*: an uncorrected recal CI
  under-covers at high dispersion (wrong-cert 0.115 > α); Bonferroni look
  correction brings all cells to ≤ 0.01. Both runs recorded.

## 6. Development replay (C2 on real collections)

Replaying the frozen planner over the 13 development collections (50 repeats
each; F2_planner_frontier.png):

- **Risk**: overall wrong-certificate rate 0.035 (recalibration 0.017,
  selection 0.052) vs nominal α = 0.1. Per collection × decision, the only
  cell above α is scifact selection at 0.14 (MC SE ≈ 0.05 at 50 repeats);
  climate-fever sits at exactly 0.10.
- **Adaptivity**: the planner certifies selection at T=10 with zero wrong
  certificates on trec-covid (huge gap), spends T≈45–65 on mid-gap
  collections, and abstains rather than certify on near-tied or dispersed
  cases (quora recalibration act rate 0.06; fever recalibration 0.16) —
  matching the C1 curves cell for cell.
- **Cross-fitting is both safer and cheaper**: vs the in-sample ablation,
  selection wrong-cert fell 0.098 → 0.052 while act rate rose 0.57 → 0.71 and
  mean audited queries fell 54.4 → 47.1. Removing the in-sample optimism
  improves the candidate choice as well as the certificate.

## 7. Sensitivity

Rerunning the identical protocol under different per-query utilities
(thresholds kept at the same numeric values on each utility's own scale —
a documented caveat):

| utility | cal ≥0.9 @ k=10 | sel ≥0.9 @ k=10 | sel ≥0.9 @ k=100 |
|---|---|---|---|
| set-F1 (primary) | 5/13 | 3/13 | 10/13 |
| binary nDCG | 5/13 | 3/13 | 9/13 |
| recall | 0/13 | **10/13** | 12/13 |

Under nDCG the asymmetry mirrors set-F1. Under recall it **reverses**:
selection becomes near-trivial (mean regret 0.002 at every k) because recall
is monotone in set size, collapsing the menu's gap structure, while scalar
recalibration becomes the hard decision. This is direct evidence for the
mechanism claim: budget requirements attach to the decision × utility × menu
geometry, not to the decision's name — and it is why a planner that computes
certificates beats any fixed-k rule of thumb. Qrels-coverage sensitivity:
deep-judged Tier-A collections vs relevance-only qrels are reported
separately; pair-cost claims are restricted to pool-size proxies.

## 8. Related work (positioning — all citations verified 2026-08-25)

Topic-set size design (Sakai, IRJ 2016; 2018 book) plans a *fixed* topic
budget a priori for generic significance testing; we plan budgets per
downstream decision, sequentially, with abstention. Guiver, Mizzaro &
Robertson (TOIS 2009) show retrospectively that a few good topics predict
full-collection outcomes but give no online procedure. Li & Kanoulas
(CIKM 2017) actively sample judgments for unbiased *metric estimation*; our
core is decision-specific stopping, not sampling innovation. The closest
neighbor is Oosterhuis et al. (KDD 2024), which builds reliable CIs for IR
metrics from limited human labels via prediction-powered inference and
conformal risk control — but those intervals are decision-agnostic and
computed at a fixed budget; they neither plan the budget against a target
decision nor emit act/collect-more/abstain certificates under shift.
Okanovic et al. (AISTATS 2025) select classifiers with few target labels —
the selection arm alone, on i.i.d. labels; LARMOR (Khramtsova et al., SIGIR
2024) ranks retrievers with zero labels but no statistical guarantee; Maekawa
et al. (NAACL 2024) analyze when retrieval helps offline. Best-arm
identification (Jamieson & Nowak 2014; Kaufmann, Cappé & Garivier, JMLR 2016)
supplies the fixed-confidence stopping machinery, but assumes independent
per-pull rewards and pure selection — retrieval audits have query-clustered
outcomes revealed jointly for all policies, pooled-judgment costs, and a
recalibration arm that BAI does not model. PPI (Angelopoulos et al., Science
2023) and conformal risk control / selective prediction (Angelopoulos et al.,
ICLR 2024; Geifman & El-Yaniv, NeurIPS 2017) certify risks at fixed samples
for fixed models; we scope abstention as a planner output, not a framework
claim. (Full table: 02_literature/references_verified_2026-08-25.md; rule —
no unverified citation enters the bibliography.)

## 9. Prospective validation (C4, primary run)

Target: cqadupstack-android (699 eligible queries) — never used in any prior
analysis, selected by a pre-committed rule (alphabetically first subforum) and
locked, together with every planner hyperparameter and the success criterion,
**before the data were downloaded** (lock sha256 7a00b578…). Training
(probability model, τ transfer, truncation regressor) used only the 13
development collections; the target contributed nothing to any fitting step.
Single primary run, 50 repeat draws:

| decision | act | abstain | mean T | wrong-cert | criterion (≤ α=0.1) |
|---|---|---|---|---|---|
| recalibration | 0.44 | 0.56 | 76.0 | **0.00** | PASS |
| selection | 0.80 | 0.20 | 48.8 | **0.08** | PASS |

The planner transferred: certificates stayed valid on a foreign collection,
and where evidence was insufficient it abstained rather than certify — 56% of
recalibration repeats, consistent with this collection's dispersed nG/Σp
ratios (low-nG duplicate-question qrels; the regime the pilot identified as
the "hurt corner"). Selection predominantly certified `ad_probe` (46/50).
We claim transfer for this one collection under the pre-registered criterion;
broader generality awaits the contracted second run (BRIGHT).

## 10. Limitations

All 13 development collections were exposed during development (D-007): every
Section-3–6 claim is retrospective/diagnostic. C4 evidence is one prospective
collection. nG requires complete judgment of a query's pool; our pair-budget
axis is a pooled-qrels proxy. Certificates are empirically calibrated
(bootstrap validity assumed), not finite-sample proven beyond Propositions
1–2's premises.

## Reproducibility statement

Single-command regeneration per stage: `20_budget_curves.py` (row-level
parquet incl. probe query ids and seeds), `30_summarize.py`, `50_simulation.py`,
`40_planner_replay.py`, `tests/run_tests.py` (unit / leakage / regeneration /
statistical). Candidate artifacts restored from public backup with checksums
and byte-identical legacy reproduction (EVIDENCE_RECOVERY_2026-08-25).
