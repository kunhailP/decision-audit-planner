# 2027 논문 설계 v0.1 — Auditing Deployment Decisions Under Non-Neutral AI Judges

상태: **설계 초안 (2026-09-10), 프로토타입 시뮬레이션 1건 첨부**
목적: 현재 planner를 "인간 감사 + 편향 가능한 AI 판정자" 시대의 배포 인증 문제로
재정의하여, 2027년 기준 선제적인 TMLR 논문으로 만든다.

## 0. 한 문장 명제

> AI 판정자가 후보 정책에 대해 중립적이지 않을 때, 배포 결정을 안전하게 인증하는 데
> 필요한 인간 감사량은 판정자의 전체 정확도가 아니라 **결정 관련 구간에서의 정책 상관
> 오류**로 결정된다. 우리는 이를 측정·통제하는 순차 감사 planner를 제안한다.

기존 초안의 "recalibration vs selection" 비교는 보조 결과로 내리고, 위 명제를 중심에 둔다.

## 1. 왜 2027년에 선제적인가

- 2024–2026 PPI 계열(Oosterhuis KDD'24, Chatzi NeurIPS'24, Gligorić–Zrnic–Candès'24,
  Kilian NeurIPS'25, Sfyraki–Wang ICLR'26)은 판정자를 **고정된 예측기**로 두고
  편향을 rectifier로 보정한다. 판정자 오류가 *어느 후보를 평가하느냐에 따라 달라지는*
  경우의 비용·위험은 다루지 않는다.
- IR 평가 문헌(Balog et al. 2025 "Rankers, Judges, and Assistants")은 LLM judge가
  LLM 기반 ranker를 체계적으로 선호함을 실증했다. 2027년의 검색·RAG 파이프라인은
  후보(reranker, LLM cutoff)와 판정자가 같은 모델군에서 나온다. 즉 **비중립 판정자가
  기본값**이 된다.
- 이 저장소만의 구조: 후보 정책이 같은 순위 pool을 공유하고 절단 위치만 다르다.
  따라서 결정에 영향을 주는 판정은 두 절단점 사이의 **불일치 구간**에 국소화된다.
  비중립성이 정확히 이 구간에 집중될 때 무슨 일이 생기는지 형식화할 수 있다.

## 2. 문제 설정

- 목표 분포 `P_T`의 query `q`, 공유 pool의 문서 순위, 정책 `m ∈ M`은 절단 `k_m(q)`.
- 참 관련성 `r(q,d)`, 참 utility `u_m(q)`, AI 판정 `r̂(q,d)`, 예측 utility `û_m(q)`.
- 인간 감사: query 단위 완전 판정(현재) 또는 pair 단위(확장).
- 결정: `m̂` 선택 후 `L = max_j μ_j − μ_m̂ ≤ ε` 인증 / MORE / ABSTAIN.
- 위험: `P(ACT ∧ L > ε) ≤ α` (모든 look에서, anytime-valid).

### 판정자 비중립성의 정의

정책 쌍 `(j, m)`에 대해 paired 예측 오차 `η_{jm}(q) = (u_j − u_m)(q) − (û_j − û_m)(q)`.

- **중립**: `η_{jm}`가 불일치 구간 `Δ_{jm}(q) = R_j(q) △ R_m(q)`의 소속과 독립.
- **비중립(정책 상관)**: `E[η_{jm} | d ∈ Δ_{jm}] ≠ 0` 또는 그 분산이 구간에 집중.

핵심 양: **결정 관련 일치도** `ρ_{jm} = corr(u_j − u_m, û_j − û_m)`.
PPI++ paired 인증서의 유효표본 이득은 `1/(1 − ρ_{jm}²)`이며, 전체 판정 정확도와는
분리된다. (프로토타입: 정확도 0.95→0.94에서 ρ 0.82→0.52.)

## 3. 방법: 세 층의 인증서

1. **Paired PPI++ 선택 인증서.** 현재 bootstrap한 `T×M` utility 행렬을
   paired difference의 PPI++ 추정(λ 조정)으로 교체. 판정자 편향은 rectifier가
   보정하므로 유효성은 유지되고, 비용은 `ρ`로 결정된다. anytime-valid 버전은
   Kilian et al.의 confidence sequence를 paired 차이에 적용.
2. **판정자 중립성 진단(neutrality audit).** 소량 인간 감사로 `η_{jm}`의
   구간 조건부 평균·분산을 추정하고, `ρ̂_{jm}`의 하한을 계산한다. 이 값이 낮으면
   planner는 "이 판정자로는 인간 단독보다 싸게 인증할 수 없다"고 **사전에** 알린다.
   판정자 채택 여부 자체가 인증 대상이 된다.
3. **구간 국소 감사(pair-level).** 인간 판정을 query 전체가 아니라 불일치 구간의
   문서에 배분. utility가 구간만으로 결정되는 경우(precision 계열, 고정 `nG`
   가정하의 recall)에는 pair 비용이 정확히 계산되고, set-F1처럼 `nG`가 필요한
   경우에는 `nG`의 PPI 보정 비용이 추가된다. 이 차이 자체가 결과다(기존 "recall에서
   난이도 역전" 관찰과 연결).

## 4. 정리 후보

- **정리 A (비용 분리).** 중립 판정자 하에서 paired PPI 인증서의 기대 정지 시점은
  `ρ_{jm}`와 격차 `μ_j − μ_m`만의 함수이며, 전체 정확도 `acc`는 `ρ`를 통해서만
  들어간다. 비중립 판정자에서는 같은 `acc`로 `ρ`가 임의로 낮아질 수 있다(구성적 반례).
- **정리 B (유효성 보존).** rectifier가 인간 감사에서 추정되는 한, 비중립성은
  `P(ACT ∧ L>ε)`를 높이지 않는다. 반면 rectifier 없는 판정자 단독 결정은
  편향 방향이 격차와 반대일 때 확률 1로 잘못 인증한다(프로토타입에서 관측).
- **정리 C (국소화).** utility가 구간 가법적이면 pair 단위 감사로 query 단위 감사와
  같은 인증서를 `|Δ_{jm}|/|pool|` 비율의 판정 비용으로 얻는다.

## 5. 프로토타입 결과 (04_code/proto/80_judge_bias_sim.py, 2026-09-10)

정책 A=고정 cutoff 8, B=F1-최적 cutoff와 잡음 cutoff의 혼합. 판정자는 무작위
오류율 `e`에 더해 "B만 가져오는 문서"를 확률 `bias`로 관련으로 오판(정책 상관 편향).
α=0.1, ε=0.01, look {10,…,250}, 200회.

### 격차 +0.011 (B가 근소하게 우세, ε 경계)

| e | bias | 전체 정확도 | ρ | 인간 단독 T | PPI T | PPI 잘못된 인증 |
|---|---|---|---|---|---|---|
| 0.05 | 0.0 | 0.950 | 0.82 | 144 | **53** | 0.09 |
| 0.05 | 0.3 | 0.938 | 0.52 | 146 | 106 | 0.06 |
| 0.05 | 0.6 | 0.925 | 0.28 | 141 | 123 | 0.08 |
| 0.15 | 0.0 | 0.850 | 0.43 | 131 | 108 | 0.10 |

전체 정확도가 1–2.5점 떨어지는 정책 상관 편향만으로 PPI 절감(63%)이 거의 사라진다.

### 격차 −0.017 (A가 우세, 판정자는 B 편애)

| e | bias | 판정자 단독 잘못된 인증 | 인간 단독 | PPI |
|---|---|---|---|---|
| 0.05 | 0.0 | 0.00 | 0.04 (T 89) | 0.03 (T 30) |
| 0.05 | 0.3 | **1.00** | 0.03 (T 81) | 0.06 (T 71) |
| 0.15 | 0.3 | **1.00** | 0.03 (T 90) | 0.05 (T 81) |

판정자 단독은 정확도 0.94에서도 100% 잘못 배포한다. rectifier가 있는 두 방법은
α 이내를 유지한다. (T=10 look의 정규근사 때문에 일부 셀이 0.10–0.125로 경계에
걸린다 — 본 실험에서는 t-분포 또는 confidence sequence로 교체.)

## 6. 실험 프로그램

1. **검색 스택 현대화 (필수 선행).** Qwen3-Embedding 0.6B(+4B Pod) 및 reranker로
   후보 pool 재구성. 기존 pool 유지. 13개 + android에서 격차 구조 재측정.
   결과가 어느 쪽이든 보고.
2. **판정자 오류 측정 testbed.** BEIR sparse qrels는 판정자 "오류"와 qrels 구멍을
   구분 못 한다. 깊게 판정된 TREC DL 2019–2021(+ LLMJudge/TREC RAG 2024의 인간·합성
   qrels 병행 자료)을 primary로. LLM judge 2–3종(서로 다른 모델군) 준비.
3. **비중립성 실측.** reranker 정책이 메뉴에 있을 때 judge의 `η` 구간 조건부 편향을
   실측. 같은 모델군 judge vs 다른 모델군 judge 비교.
4. **인증서 비교.** 인간 단독(현 planner, 결함 수정본) / paired PPI++ / anytime PPI /
   Oosterhuis PPI·CRC 고정예산 / Chatzi rank-set / confidence-driven sampling /
   SELECT-LLM 휴리스틱. 지표: 잘못된 인증률, ACT율, 인간 query 수, pair 수, 판정자
   추론비용.
5. **국소 감사.** utility 3종(precision@cut, recall, set-F1)에서 pair 국소화의
   비용·유효성. 정리 C의 조건이 실제로 갈리는지.
6. **Prospective lock.** 새 collection 1개 + 새 judge 1개를 잠그고 단일 primary run.

## 7. Kill / downgrade 기준

- 현대 pool에서 정책 간 격차가 모두 `≫ ε`이면(선택이 자명) 메뉴를 reranker 변형으로
  확장하되, 그래도 자명하면 "선택 인증은 현대 검색에서 불필요"를 결과로 보고.
- 실측 `ρ`가 judge 모델군과 무관하게 높으면 비중립성 명제를 축소하고 PPI 적용
  논문으로 내린다.
- 국소 감사가 어떤 utility에서도 비용을 줄이지 못하면 정리 C를 삭제.

## 8. 기존 결함 수정(선행 조건, 변경 없음)

40_planner_replay.py 보정 인증서의 끝점 검사, LOO bootstrap의 유효성, 50_simulation.py의
look별 재표집, 70_prospective_run.py의 구간 보고. 판정자를 도입해도 그대로 남는다.

## 9. 착수 기록 (2026-09-10, branch `2027-nonneutral-judge`)

### 9.1 확인된 사실 (합성 자료, `04_code/lib/certificates.py` self-test)

- **끝점 검사 결함 재현**: 단일 query 예에서 끝점 spread 0.000, breakpoint 전수 검사 spread 0.167.
  v0.4 보정 인증서는 구간 안의 모든 gate breakpoint를 검사한다(`recal_spread`).
- **후보 선택의 winner's curse**: 후보를 같은 자료에서 고르고 M−1개 비교만 보정하면
  정확한 t-구간을 써도 look당 위험이 0.049 (예산 0.020). 모든 순서쌍 M(M−1)을 동시
  보정하면 0.014. v0.3의 Proposition 1은 "후보가 고정"일 때만 성립했다.
- PPI++ paired UCB도 같은 동시 보정 아래 0.006으로 유효.

### 9.2 P4 prospective 결과의 구간 (`71_prospective_report.py`, 재실행 없음)

| decision | ACT | wrong | wrong rate [CP 95%] | wrong given ACT [CP 95%] |
|---|---|---|---|---|
| recalibration | 22/50 | 0 | 0.00 [0.000, 0.071] | 0.00 [0.000, 0.154] |
| selection | 40/50 | 4 | 0.08 [0.022, 0.192] | 0.10 [0.028, 0.237] |

### 9.3 진행 중인 실험 (이 환경: RTX 3090, 256 CPU)

- `61_build_pool.py`: nfcorpus / scifact / arguana / cqadupstack-android에 대해 legacy·modern
  두 stack의 후보 pool + Qwen3-Reranker P(yes) judge proxy.
- `62_pool_compare.py`: go/no-go #1 — 현대 stack에서 격차 구조 생존 여부.
- `63_planner_v2.py`: loo_boot(v0.3) / split_t / split_ppi 인증서 비교 + judge 진단
  (전체 정확도, ρ, 불일치 구간 안팎 오류율).
- `64_trecdl_pool.py`: TREC DL 2019/2020 완전 판정 pool (go/no-go #2 testbed).

### 9.4 Go/no-go #1 결과 — 현대 stack에서 결정 구조 생존 (`05_results/pool_compare/`)

LODO(3개로 학습, 1개 평가), 50회 반복, set-F1, ε_cal=0.005, ε_sel=0.01.
modern = legacy에서 msmarco-MiniLM을 Qwen3-Embedding-0.6B로 교체(4-feature 분류기는 동일).

| collection | stack | pool recall | best F1 | best policy | 1–2위 격차 | cal ok@10 | sel ok@10 | sel ok@50 |
|---|---|---|---|---|---|---|---|---|
| android | legacy | 0.852 | 0.315 | ad_probe | 0.008 | 0.52 | 0.88 | 0.94 |
| android | modern | 0.865 | 0.356 | glob_probe | 0.023 | 0.26 | 0.86 | 0.84 |
| scifact | legacy | 0.963 | 0.497 | glob_probe | 0.027 | 0.30 | 0.80 | 0.84 |
| scifact | modern | 0.957 | 0.525 | glob_probe | 0.029 | 0.32 | 0.82 | 0.96 |
| nfcorpus | legacy | 0.308 | 0.148 | ad_probe | 0.001 | 1.00 | 0.76 | 0.98 |
| nfcorpus | modern | 0.321 | 0.159 | ad_probe | 0.003 | 0.88 | 0.84 | 0.88 |
| arguana | legacy | 0.986 | 0.163 | glob_probe | 0.041 | 0.30 | 0.90 | 1.00 |
| arguana | modern | 0.992 | 0.166 | glob_probe | 0.043 | 0.30 | 0.84 | 1.00 |

판정: **GO.** 검색 성능은 오르지만(android F1 0.315→0.356) 정책 간 격차는 여전히 ε 규모
(0.003–0.043)이고, android에서는 최적 정책 자체가 ad_probe→glob_probe로 바뀐다.
즉 강한 검색기에서도 "어떤 절단 규칙을 배포할지"는 감사가 필요한 결정으로 남는다.
보정 결정은 modern에서 오히려 어려워지는 경향(android cal ok@10 0.52→0.26).
한계: 4-feature 분류기가 그대로라 Qwen3 신호는 pool 구성에만 들어갔다. qwen3e_cos를
feature로 넣은 "fully modern" 변형은 후속.

### 9.5 Planner v2 결과 — 인증서 변형 비교 (`05_results/planner_v2/`, 50회, α=0.1)

방법: `loo_boot`(v0.3 그대로), `loo_sim`(LOO + 모든 순서쌍 동시보정), `split_t`(학습/검증 분리 + t),
`split_ppi`(split_t + Qwen3-Reranker judge PPI++), 보정은 `recal_ep`(v0.3 끝점), `recal_bp`(breakpoint 전수),
`recal_bpx`(breakpoint + 정확 median 구간), `recal_bpxu`(+ uniform bootstrap 상한).

**선택 결정 (ACT율 / 잘못된 인증률)**

| stack | collection | loo_boot | loo_sim | split_t | split_ppi |
|---|---|---|---|---|---|
| legacy | android | 0.54 / 0.08 | 0.46 / 0.04 | 0.10 / 0.00 | 0.14 / 0.00 |
| legacy | scifact | 0.74 / 0.08 | 0.70 / 0.06 | 0.12 / 0.00 | 0.14 / 0.02 |
| legacy | nfcorpus | 0.78 / 0.00 | 0.62 / 0.00 | 0.24 / 0.02 | 0.38 / 0.02 |
| legacy | arguana | 0.96 / 0.04 | 0.94 / 0.02 | 0.34 / 0.02 | 0.28 / 0.02 |
| modern | android | 0.72 / **0.12** | 0.62 / 0.08 | 0.12 / 0.02 | 0.12 / 0.02 |
| modern | scifact | 0.88 / **0.12** | 0.80 / 0.10 | 0.24 / 0.00 | 0.24 / 0.04 |
| modern | nfcorpus | 0.88 / 0.04 | 0.72 / 0.02 | 0.26 / 0.02 | 0.30 / 0.02 |
| modern | arguana | 0.88 / 0.04 | 0.82 / 0.04 | 0.28 / 0.00 | 0.32 / 0.00 |

- v0.3 인증서(`loo_boot`)는 modern stack의 두 collection에서 α를 넘는다(0.12, MC SE 0.04).
  동시보정(`loo_sim`)이 이를 낮추지만 LOO 의존성은 남는다.
- 유효한 split 인증서는 ACT율이 0.10–0.38로 떨어진다. **v0.3의 효율 일부는 유효성 위반에서 온 것.**
  이것이 "자료 재사용을 허용하면서 유효한 인증서"가 필요한 실증적 이유다.
- PPI의 이득은 미미하다. 판정자(reranker≥0.5)의 paired-difference ρ가 0.04–0.27에 불과.

**보정 결정 (ACT율 / 잘못된 인증률)**

| stack | collection | recal_ep (v0.3) | recal_bp | recal_bpx | recal_bpxu |
|---|---|---|---|---|---|
| legacy | android | 0.30 / 0.00 | 0.12 / 0.00 | 0.06 / 0.00 | 0.00 / – |
| legacy | nfcorpus | 0.92 / 0.00 | 0.70 / 0.00 | 0.62 / 0.00 | 0.00 / – |
| modern | arguana | 0.32 / **0.14** | 0.30 / **0.14** | 0.20 / 0.08 | 0.14 / 0.08 |
| modern | nfcorpus | 0.80 / 0.00 | 0.48 / 0.00 | 0.44 / 0.00 | 0.00 / – |

- 끝점 검사는 ACT율을 2–5배 부풀린다(android 0.30 vs 0.06). v0.3 P4의 recal ACT 0.44도 같은 이유로 과대.
- bootstrap median 구간은 T=10에서 실패(arguana modern 오류 0.14 → 정확 구간으로 0.08).
- 표본 utility 곡선의 불확실성까지 상한(`bpxu`)에 넣으면 ε_cal=0.005는 90건 안에서 거의 인증 불가.
  → ε_cal 재설정 또는 보정을 보조 결과로 내리는 결정이 필요.

**판정자 진단 (pair 정확도 / 결정 구간 안 오류율 / 밖 오류율)**

| collection | legacy | modern |
|---|---|---|
| scifact | 0.91 / 0.27 / 0.09 | 0.90 / 0.28 / 0.10 |
| arguana | 0.82 / 0.30 / 0.17 | 0.82 / 0.30 / 0.17 |
| android | 0.61 / 0.70 / 0.38 | 0.56 / 0.75 / 0.43 |
| nfcorpus | 0.87 / 0.15 / 0.13 | 0.86 / 0.15 / 0.14 |

**판정자 오류는 정책 불일치 구간에 2–3배 집중된다.** 이것이 §2 명제의 첫 실데이터 증거다.
단, BEIR qrels 구멍이 "오류"에 섞여 있으므로 TREC DL 완전 판정 pool에서 재측정해야 한다(진행 중).
android에서는 reranker 판정자가 사실상 무작위(0.56–0.61): 중복 질문 관련성은 passage 관련성과 다른 과제.

주의: 방법 변형을 추가하면 rng 소비 순서가 바뀌어 `loo_boot` 수치가 run 간 ±0.04 흔들린다.
최종 실험에서는 방법별 독립 rng stream을 써야 한다.

### 9.6 Go/no-go #2 — TREC DL 완전 판정 pool에서의 판정자 진단 (`05_results/planner_v2/trecdl`, `05_results/ppi_gain`)

pool = NIST 판정 passage 전체(dl2019 43 query·9,260 pair, dl2020 54 query·11,386 pair), relevant = grade≥2,
판정자 = Qwen3-Reranker-0.6B P(yes)≥0.5 (pair 정확도 0.70 / 0.66). 정책 파라미터는 다른 해에서 학습(LODO).

| collection | 정책 쌍 | ρ | 구간 안 오류 | 구간 밖 오류 | ESS 이득 (T=10) | 이론 1/(1−ρ²) |
|---|---|---|---|---|---|---|
| dl2019 | glob vs trunc | 0.70 | 0.33 | 0.29 | 1.76 | 1.94 |
| dl2019 | glob vs ad | 0.44 | 0.32 | 0.30 | 1.31 | 1.23 |
| dl2019 | trunc vs ad | 0.68 | 0.35 | 0.29 | 1.68 | 1.85 |
| dl2020 | glob vs trunc | 0.27 | 0.52 | 0.24 | 1.18 | 1.08 |
| dl2020 | glob vs ad | **0.01** | **0.62** | 0.27 | **1.08** | 1.00 |
| dl2020 | trunc vs ad | 0.63 | 0.42 | 0.32 | 1.75 | 1.66 |

- **같은 판정자, 같은 collection 안에서** 정책 쌍에 따라 PPI 이득이 1.0배에서 1.75배까지 갈린다.
  갈리는 기준은 전체 정확도가 아니라 해당 쌍의 불일치 구간에 오류가 집중되는지다
  (dl2020 glob vs ad: 구간 안 0.62 vs 밖 0.27 → ρ≈0 → 이득 없음).
- dl2019는 구간 안팎 오류가 비슷하고(0.32 vs 0.30) ρ 0.44–0.70으로 이득이 난다.
  정확도는 dl2019 0.70, dl2020 0.66으로 거의 같다. → 정리 A의 실데이터 지지.
- BEIR(qrels 구멍)에서는 같은 판정자의 ρ가 ≤0.27이었다. 구멍이 "오류"로 계산되어 ρ를 눌렀다는 해석과
  일치하며, 완전 판정 pool이 왜 필요한지 보여준다.
- 한계: query 43·54개라 ρ의 SE ≈ 0.12–0.15. 순차 인증서 비교는 T=10 한 look만 가능해 무의미.
  ESS 이득이 T 증가와 함께 줄어드는 것은 N이 작아 Var(d̂)/N 항이 남기 때문(실배포 N≫T에서는 이론값에 접근).
- 진행 중: Qwen3-8B UMBRELA 프롬프트 LLM 판정으로 같은 표를 재계산(`66_llm_judge.py`).

### 9.7 F4 — PPI 이득은 ρ가 결정하고 정확도는 무관 (`05_results/ppi_gain/F4_gain_vs_rho_rr.png`)

legacy·modern BEIR pool(각 4 collection × 3 쌍) + TREC DL(2 × 3 쌍) = 30개 (pool, 정책 쌍) 점,
같은 판정자(Qwen3-Reranker), T=10, 300–500회 무작위 감사 추출.

| 점 집합 | n | corr(이득, ρ) | corr(이득, 전체 정확도) |
|---|---|---|---|
| legacy | 12 | 0.85 | 0.74 |
| modern | 12 | 0.90 | 0.50 |
| trecdl | 6 | 0.95 | 0.44 |
| 전체 | 30 | **0.94** | **−0.07** |

점들은 이론 곡선 1/(1−ρ²)를 따른다. 전체 정확도는 pool을 섞으면 이득과 무관해진다(−0.07).
이것이 논문의 첫 번째 그림 후보다. 주의: T=10에서 λ를 표본 내에서 추정해 ρ≈0 근처 점이 곡선 위로
약간 뜬다(경미한 낙관). 본 실험에서는 λ를 cross-fit하거나 고정 λ 스케줄을 쓴다.

### 9.8 LLM 판정자(Qwen3-8B, UMBRELA 프롬프트) vs reranker 판정자 — TREC DL

| collection | 정책 쌍 | reranker ρ → LLM ρ | reranker 구간 안/밖 → LLM 구간 안/밖 | ESS 이득 T=10 (rr → LLM) |
|---|---|---|---|---|
| dl2019 | glob vs trunc | 0.70 → 0.88 | 0.33/0.29 → 0.27/0.25 | 1.76 → 2.64 |
| dl2019 | glob vs ad | 0.44 → 0.57 | 0.32/0.30 → 0.28/0.25 | 1.31 → 1.47 |
| dl2019 | trunc vs ad | 0.68 → 0.87 | 0.35/0.29 → 0.28/0.25 | 1.68 → 2.45 |
| dl2020 | glob vs trunc | 0.27 → 0.56 | 0.52/0.24 → 0.31/0.19 | 1.18 → 1.50 |
| dl2020 | glob vs ad | 0.01 → 0.48 | 0.62/0.27 → 0.35/0.20 | 1.08 → 1.37 |
| dl2020 | trunc vs ad | 0.63 → 0.76 | 0.42/0.32 → 0.27/0.22 | 1.75 → 2.19 |

pair 정확도는 0.70/0.66 → 0.75/0.77로 5–10점 오르는데, 이득의 변화는 쌍마다 다르다.
LLM 판정자가 이득을 만드는 경로는 **구간 안 오류의 집중을 푸는 것**이다
(dl2020 glob vs ad: 구간 안/밖 비 2.3배 → 1.75배, ρ 0.01 → 0.48).
즉 "더 정확한 판정자"가 아니라 "결정 구간에서 덜 편향된 판정자"가 감사비용을 줄인다.
F4 갱신본(`F4_gain_vs_rho.png`): 36점에서 corr(이득, ρ)=0.91, corr(이득, 정확도)=−0.07.
ESS 이득이 이론값(최대 4.5)에 못 미치는 것은 N=43·54의 Var(d̂)/N 항 때문이다.

### 9.9 착수 단계 종합 판정

- Go/no-go #1 (현대 stack에서 구조 생존): **통과**.
- Go/no-go #2 (판정자 오류의 결정 구간 집중과 ρ 의존): **통과** — 완전 판정 pool에서 확인,
  판정자 두 종(reranker, 8B LLM)에서 일관.
- Go/no-go #3 (실측 오류로 감사 절감 차이가 유의): **부분 통과** — ESS 이득 1.0–2.6배가 ρ로 설명됨.
  순차 인증서 수준의 절감은 query가 더 많은 완전 판정 collection(TREC DL 2021–2023, LLMJudge)이 필요.
→ 본격 착수 결정에 필요한 증거는 갖춰졌다. 다음은 ρ 하한을 소량 감사로 추정하는
  중립성 진단(§3.2)의 이론과 구현, 방법별 독립 rng·cross-fit λ로 재현 규율 확정,
  그리고 query가 많은 완전 판정 collection 확보.

## 10. 2단계 착수 기록 (2026-09-10, 이어서)

### 10.1 재현 규율 적용 후의 정직한 F4 (cross-fit λ, 방법별 독립 rng)

§9.7의 F4는 λ를 표본 내에서 추정한 값이었다. λ를 cross-fit(두 반쪽 교차)하고 다시 계산하면:

| T | 점 수 | corr(이득, ρ) | corr(이득, 정확도) | 평균 이득 | 최대 이득 |
|---|---|---|---|---|---|
| 10 | 36 | 0.73 | −0.02 | 1.01 | 2.17 |
| 30 | 36 | 0.70 | 0.03 | 0.99 | 1.28 |
| 90 | 24 | 0.43 | 0.12 | 0.99 | 1.03 |

- **메커니즘은 유지**(ρ만이 이득을 설명, 정확도는 무관)되지만 **실현 이득의 크기는 작아진다.**
  ρ ≥ 0.75인 LLM 판정자 쌍에서만 1.3–2.2배(dl2019 glob vs trunc, trunc vs ad), 나머지는 ≈1.0.
- 이득이 T와 함께 줄어드는 것은 N=43–54에서 Var(d̂)/N 항이 지배하기 때문. 실배포(N ≫ T)에서는
  이론값 1/(1−ρ²)에 접근하며, 이 점은 query 400개인 dbpedia-entity 완전 판정 pool에서 확인한다(진행 중).
- 결론: reranker 판정자(ρ ≤ 0.3)는 실용 이득이 없다. 8B LLM 판정자는 일부 결정에서만 이득이 있고,
  어느 결정인지는 ρ가 말해준다. → 판정자 중립성 진단이 방법의 핵심 구성요소가 된다.

### 10.2 중립성 진단 (`lib/neutrality.py`, `70_neutrality_eval.py`)

- Fisher-z ρ 하한은 정규 자료에서 명목 coverage(miss 0.10–0.11)이나, set-F1 차이처럼 0이 많은
  skewed 자료에서는 miss 0.12–0.15로 부족. bootstrap 백분위 하한은 n0=30에서 0.07–0.10으로 유효하고
  n0=10에서는 ρ=0일 때 0.14로 부족 → **pilot은 최소 20–30 query**를 권고.
- dl1920(97 query, BEIR 학습): reranker 판정자에 대해 진단은 3–8%만 "judge 사용"을 권고(정답: 이득 없음),
  LLM 판정자(ρ 0.41–0.48, 이론 이득 1.2–1.3)에는 25–41% 권고. 예산 투영은 N=97에서 PPI가 인간 단독보다
  오히려 길게 나오는데(비 1.04–1.46), 이는 Var(d̂)/N 항과 cross-fit λ의 잡음 때문이며 N이 큰 pool에서 재평가.
- bootstrap 하한을 dl1920 실자료에 적용: gain_lcb의 coverage 0.78–0.99 (reranker 0.89–0.99, LLM 0.78–0.89).
  N=97에서 n0=20–30은 모집단의 20–30%라 유한모집단 효과가 크다. N이 큰 pool에서 재평가하고,
  필요하면 BCa 또는 순열 기반 하한으로 교체한다. reranker 판정자에 대한 "사용 권고" 0–3%는 정답과 일치.
