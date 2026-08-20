# Reviewer Report v0.1

대상: **Audits for What? Decision-Specific Validation Budgets for Retrieval under Distribution Shift**  
기준일: 2026-08-20  
판정: **현 상태 Reject — 핵심 설계 보완 후 재심사 가능**

## 1. 심사자 요약

이 논문은 target-domain query audit를 두 가지 결정, 즉 고정 policy의 recalibration과 여러 policy 중 selection에 사용했을 때 필요한 audit budget이 다를 수 있다는 문제를 제기한다. 질문은 실용적이고 명료하며, 기존 shift-study에서 발견된 긍정·부정 결과를 정직하게 재구성하려는 태도는 장점이다.

그러나 현재 설계만으로는 독립적인 **방법론 논문**이라고 보기 어렵다. 지금 있는 것은 흥미로운 진단 가설과 재분석 계획이다. 기존 IR 문헌은 이미 topic-set size, 적은 topic으로 system ranking을 예측하는 방법, active sampling, 소량의 신뢰 가능한 relevance judgment를 이용한 IR evaluation, 제한된 label 아래 model selection을 다룬다. 따라서 “보정보다 선택에 label이 더 필요하다”는 관찰만으로는 novelty가 충분하지 않다.

또한 현재 budget의 단위는 label이나 query-document judgment가 아니라 **완전히 audit된 query**다. query마다 필요한 판단 수가 다른 상황에서 이를 인간 검증비용으로 해석하면 cost claim이 성립하지 않는다. 기존 candidate artifact가 누락되어 새 결과를 재생성할 수 없다는 점도 현 단계에서는 치명적이다.

## 2. 장점

1. **질문이 실무적이다.** target-domain 평가자는 실제로 적은 audit로 무엇을 할 수 있는지 알아야 한다.
2. **두 결정을 구분한다.** performance correction과 policy selection을 같은 문제로 취급하지 않는 관점은 유용하다.
3. **부정 결과를 살린다.** k=10에서 selection이 실패한 결과를 숨기지 않고 중심 문제로 전환한다.
4. **범위가 통제되었다.** 정치학 적용, abstention, PPI, active sampling을 core에서 제거한 것은 적절하다.
5. **재현성 규율의 기반이 있다.** LODO, probe/evaluation 분리, 결정로그, 고정 seed 관행은 살릴 가치가 있다.

## 3. Major concerns

### M1. 새 기여가 기존 문헌과 아직 분리되지 않는다 — 치명적

IR은 이미 다음 문제를 다뤘다.

- Sakai의 topic-set size design은 원하는 power 또는 CI width에 필요한 topic 수를 설계한다.
- Guiver, Mizzaro, Robertson은 적은 topic으로 system effectiveness/ranking을 예측하는 문제를 다룬다.
- Li와 Kanoulas는 relevance judgment 비용을 줄이기 위한 active sampling을 제안한다.
- Oosterhuis 등은 소량의 신뢰 가능한 relevance annotation으로 IR metric의 신뢰구간을 구성한다.
- Okanovic 등은 제한된 target labels로 near-best model을 선택한다.

현재 원고가 이들과 다른 점은 “recalibration과 selection을 한 budget 축에서 비교한다”는 것이다. 그러나 이것이 단순한 기존 두 문제의 병치인지, 새로운 평가 원리인지 아직 입증되지 않았다.

**필수 수정:** 논문의 기여를 다음 중 하나로 결정해야 한다.

- **경험적 진단 논문:** 같은 audit budget의 충분성이 결정별로 다르다는 현상과 조건을 체계적으로 밝힌다.
- **방법론 논문:** 사용자가 decision, tolerance, policy menu를 입력하면 필요한 audit budget을 산출하는 재사용 가능한 절차를 제안한다.

두 번째를 선택한다면 기존 power/topic-size 방법보다 무엇이 달라지는지 수식과 실험으로 보여야 한다.

### M2. 현재는 method가 아니라 retrospective budget curve다 — 치명적

full target qrels를 사용해 사후적으로 k별 성공률을 그리는 것만으로는, 새 target에 배치하려는 사용자가 필요한 k를 사전에 정할 수 없다.

**필수 수정:** 최소한 다음 interface를 가진 audit-planning protocol이 필요하다.

```text
입력: decision d, candidate policies, target tolerance, pilot audit
출력: recommended k 또는 현재 자료로 결정 불가
```

새로운 복잡한 uncertainty theory를 만들 필요는 없다. 기존 power/resampling 도구를 decision-specific loss에 맞게 형식화하고, 독립 target에서 권고 k의 성공률을 검증하면 된다.

### M3. audited query는 인간 판단 비용이 아니다 — 치명적

현재 k는 query 수다. 그러나 query 하나를 완전히 audit하는 데 필요한 document judgment 수는 query와 dataset마다 다르다. 특히 `c_hat` 계산에는 각 query의 `nG`가 필요하며, 이는 실제 배치 상황에서 exhaustive 또는 충분히 깊은 relevance assessment 없이 알기 어렵다.

**필수 수정:** 둘 중 하나를 선택해야 한다.

1. 논문 전체를 **topic/query budget**으로 제한하고 인간 annotation-cost 주장을 제거한다.
2. 명시적 candidate pool과 judgment protocol을 정의하고 pair-level cost를 계산한다.

현재 일정과 자료를 고려하면 1번이 core에 적합하다. 2번은 별도 확장이다.

### M4. recalibration과 3-way selection의 난이도가 구조적으로 다르다 — 치명적

scalar 하나를 보정하는 문제와 세 policy 중 최고를 고르는 문제를 비교하면 selection이 더 어려운 것은 자연스럽다. 현재 결과만으로는 “결정의 종류” 때문인지, policy menu 크기나 policy 간 작은 성능격차 때문인지 분리되지 않는다.

**필수 수정:** 최소한 다음 두 sensitivity가 필요하다.

- menu size 2 대 3
- true policy gap이 큰 dataset/cell 대 작은 dataset/cell

가능하면 동일한 per-query outcome matrix에서 gap과 menu size를 통제한 simulation을 추가한다. 이것이 없으면 논문의 핵심 결론은 자명한 관찰로 평가될 수 있다.

### M5. qrels hole과 `nG`의 의미가 성능·비용 해석을 오염한다 — 중요

BEIR dataset의 qrels coverage는 균일하지 않다. unjudged document를 nonrelevant로 처리하면 adaptive set-F1과 scalar correction이 실제 relevance가 아니라 judgment process에 반응할 수 있다.

**필수 수정:** judgment coverage가 높은 collection을 primary analysis로 두고, sparse-qrels collection은 sensitivity로 분리하거나 hole-aware 결과를 병기해야 한다. dataset별 judged fraction과 candidate-pool recall을 보고해야 한다.

### M6. 독립 검증이 없다 — 중요

13개 dataset 모두 이전 분석에서 노출되었고, 기존 untouched-4도 다른 fold의 training data로 서로 사용되었다. 따라서 새 논문의 독립 confirmatory evidence가 아니다.

**필수 수정:** 분석 코드와 모든 임계값을 고정한 뒤 최소 하나의 새로운 retrieval collection 또는 공개 run set에 prospective validation을 수행해야 한다. 그렇지 않으면 논문 전체를 명시적으로 exploratory/reanalysis로 제한해야 한다.

### M7. set-F1 하나로는 일반적인 IR evaluation 기여가 약하다 — 중요

variable-size result set에는 set-F1이 의미가 있지만, IR 독자는 nDCG, AP, Recall, Precision 등과의 관계를 요구할 것이다. decision-specific budget gap이 set-F1의 특수성인지도 확인해야 한다.

**필수 수정:** set-F1을 primary로 유지하되 적어도 하나의 표준 ranking metric과 하나의 retrieval-coverage metric을 sensitivity로 포함한다. metric에 따라 decision budget이 달라지는 경우 그것이 결과다.

### M8. 현재 artifact로 핵심 결과를 재현할 수 없다 — 치명적

`block1_confirm/per_query.csv`는 실제로 dataset-level 13행이며 repeat/query identifier가 없다. runner가 요구하는 `runs/candidates/`도 공개·로컬 작업본에 없다.

**필수 수정:** candidate artifact를 복구 또는 재생성하고 다음을 공개해야 한다.

- manifest와 checksum
- repeat-level output
- probe query identifiers
- source/target fold 기록
- headline figure를 처음부터 생성하는 단일 명령

## 4. Minor concerns

- `ad_c`는 oracle이 아니라 full-target scalar reference로 일관되게 명명해야 한다.
- k=50·100은 작은 dataset에 적용할 수 없으므로 공통 grid와 extended grid를 구분해야 한다.
- 500회 반복의 Monte Carlo 오차를 보고해야 한다.
- dataset 13개를 임의의 모집단 표본처럼 bootstrap하여 일반화하지 않아야 한다.
- “distribution shift”를 사용하려면 shift의 조작적 지표 또는 source-target 구조를 명시해야 한다.
- selection menu가 현존 세 policy에만 맞춰진 임의적 구성이 아닌지 설명해야 한다.

## 5. 게재 가능한 최소 패키지

다음 여덟 조건을 모두 만족하면 IR evaluation journal에 제출할 만한 논문이 된다.

1. 재현 가능한 candidate/repeat-level artifact
2. decision-specific estimand와 loss의 명시
3. query budget과 pair-judgment cost의 엄격한 구분
4. Sakai·Guiver·Li/Kanoulas·Oosterhuis·Okanovic과의 직접 비교
5. menu size와 policy gap sensitivity
6. qrels coverage 및 metric sensitivity
7. 최소 하나의 prospective external validation
8. 사용자가 실행할 수 있는 audit-planning protocol 또는, 더 좁은 empirical-diagnostic claim

## 6. 저널 전략

### 1순위 적합 — Information Retrieval Research Journal (IRRJ)

현재 아이디어와 가장 직접적으로 맞는다. IRRJ는 새로운 evaluation approach, reproducibility study, 기존 기법의 강·약점을 밝히는 연구를 명시적으로 받고, 주관적 significance보다 technical correctness를 강조한다. normal paper는 약 20페이지이며 code/data 공개를 강하게 권장한다. Diamond OA라 저자 APC가 없다.

**제출 조건:** 위 최소 패키지 1–7을 충족하고, 기여를 empirical evaluation protocol로 정직하게 제한하면 된다.

**단점:** 2025년에 시작한 신생 저널이므로 학계의 장기적 평판과 색인은 성숙 중이다.

### 1순위 야심 목표 — Transactions on Machine Learning Research (TMLR)

TMLR은 주장의 정확하고 설득력 있는 증거와 일부 독자의 관심을 핵심 기준으로 삼고, 기여의 규모가 크지 않아도 이를 충족하면 받아들일 수 있다고 명시한다. 강한 재현성과 정직한 negative result에 유리하다.

**제출 조건:** retrieval-specific 세 policy의 사례를 넘어 decision-specific audit planning이 다른 model-selection/evaluation 문제에도 적용된다는 일반성을 보여야 한다. 현재 BEIR 재분석만으로는 독자 범위가 너무 좁을 수 있다.

### Stretch — ACM Transactions on Information Systems (TOIS)

주제 적합성은 매우 높다. IR evaluation methodology 자체가 범위에 들어간다. 그러나 “예산 곡선을 그렸다”는 정도로는 부족하다.

**제출 조건:** 재사용 가능한 방법, 명확한 formalization, 표준 IR metrics, 여러 judgment regimes, prospective validation, 완전한 artifact가 필요하다. 가능하면 사용자가 pilot에서 k를 계획하는 algorithm까지 있어야 한다.

### 조건부 — Information Processing & Management (IPM)

IPM은 computing과 information science의 교차점에서 original research와 research methods article을 받는다. 공식 안내는 methods manuscript에 novel method의 적용을 요구한다.

**제출 조건:** 단순 empirical finding이 아니라 실제로 새로운 audit-planning method를 제시하고, retrieval 이외에도 유용한 information-processing implication을 보여야 한다.

### 현재 비추천 — JASIST

JASIST는 정보·시스템·사용자의 연결과 연구의 use 맥락을 강조한다. 방법론 혁신도 unique하고 significant하며 기존 방법으로 얻지 못하는 insight를 산출해야 한다. 현재의 BEIR-only policy comparison은 너무 좁고 사용자 연구가 없다.

### fallback — Discover Computing

과거 Information Retrieval Journal은 현재 Discover Computing으로 바뀌어 매우 넓은 computer-science journal이 되었다. Methodology article은 demonstrable advance와 충분한 검증을 요구한다. 게재 가능성은 있을 수 있지만, 현재 연구의 IR 정체성을 가장 잘 살리는 1차 목표는 아니다.

## 7. 추천 투고 순서

### 경로 A — 방법을 크게 늘리지 않을 때

1. DXW 발표에서 empirical diagnostic으로 검증
2. artifact와 prospective dataset 보완
3. IRRJ normal paper 제출

### 경로 B — 진짜 audit-planning method까지 만들 때

1. decision-specific budget estimator/protocol 개발
2. BEIR + prospective collection에서 검증
3. TMLR 제출
4. IR theory와 evaluation 범위를 더 확장할 수 있으면 TOIS를 stretch target으로 검토

## 8. 최종 심사 판정

현재 논문은 질문은 잡혔지만 방법론은 아직 완성되지 않았다. 가장 중요한 다음 단계는 실험을 많이 추가하는 것이 아니라 다음 한 문장을 참으로 만드는 것이다.

> 이 논문은 새로운 target dataset에서 사용자가 내리려는 결정에 맞춰 필요한 query-audit budget을 계획할 수 있는 재현 가능한 절차를 제공한다.

이 문장을 충족하면 방법론 논문이다. 충족하지 못하면 정직하고 유용한 empirical IR evaluation study로 제출하는 것이 맞다.

## 9. 주요 출처

- Tetsuya Sakai, Topic set size design: https://doi.org/10.1007/s10791-015-9273-z
- Guiver, Mizzaro & Robertson, A Few Good Topics: https://doi.org/10.1145/1629096.1629099
- Li & Kanoulas, Active Sampling for Large-scale IR Evaluation: https://arxiv.org/abs/1709.01709
- Oosterhuis et al., Reliable Confidence Intervals for IR Evaluation: https://doi.org/10.1145/3637528.3671883
- Okanovic et al., Model Selection with Limited Labels: https://proceedings.mlr.press/v258/okanovic25a.html
- IRRJ submission criteria: https://irrj.org/about/submissions
- TMLR editorial criteria: https://www.jmlr.org/tmlr/editorial-policies.html
- ACM TOIS: https://dl.acm.org/journal/tois
- IPM author guide: https://www.sciencedirect.com/journal/information-processing-and-management/publish/guide-for-authors
- JASIST author guidelines: https://asistdl.onlinelibrary.wiley.com/hub/journal/23301643/homepage/forauthors
- Discover Computing methodology criteria: https://link.springer.com/journal/10791/submission-guidelines
