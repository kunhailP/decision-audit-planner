# Method specification v0.2

상태: **구현 전 설계안**  
목적: 논문을 retrospective budget study에서 deployable audit-planning method로 올린다.

## 1. Problem setup

목표 환경의 query 분포를 `P_T`라 하고, target query `q`에 대해 policy `m`이 만드는 결과의 bounded utility를 `u_m(q) ∈ [0,1]`라 한다. 기본 실험의 utility는 set-F1이며, standard IR metric은 sensitivity로 둔다.

정책의 target utility는 다음이다.

```text
μ_m = E_{q ~ P_T}[u_m(q)]
```

개발자는 target 전체의 relevance를 모르며, 무작위로 감사한 query 집합 `S_k`만 가진다. `k`는 audited query 수다. 실제 판단비용 `B`는 query–document pair judgment 수로 별도 기록한다.

## 2. Two decisions

### D1 — Recalibration

기존 adaptive rule은 query의 predicted relevant mass에 scalar `c`를 적용한다. 현재 파일럿의 target reference는 다음과 같은 관련문서 총량 비율의 중앙값이다.

```text
c_T = median_q [ nG(q) / sum_i p_i(q) ]
```

감사 표본으로 `ĉ_k`를 추정하고 policy `π(ĉ_k)`를 만든다. 중심 loss는 parameter error 자체가 아니라 downstream decision loss다.

```text
L_cal(k) = μ_{π(c_T)} - μ_{π(ĉ_k)}
```

`π(c_T)`는 full-target scalar reference이며 oracle retrieval이 아니다.

### D2 — Policy selection

candidate menu `M`에서 감사자료로 policy `m_hat`을 고른다.

```text
L_sel(k) = max_{m ∈ M} μ_m - μ_{m_hat}
```

성공은 exact-best selection이 아니라 사전에 정한 `ε_sel` 이하의 regret으로 정의한다.

## 3. Decision-Specific Audit Planner

### Inputs

- decision `d ∈ {recalibration, selection}`
- candidate policies 또는 calibration rule
- tolerance `ε_d`
- risk level `α`
- initial audit `k0`, batch size `b`, maximum budget `k_max`
- audited-query sampling design과 inclusion probability

### Outputs

- `ACT`: 현재 결정과 decision certificate
- `MORE`: 다음 batch의 추가 audit 요청
- `ABSTAIN`: `k_max`에서도 certificate를 만들 수 없음

### Sequential skeleton

```text
1. Draw k0 target queries using the frozen audit design.
2. Construct cross-fitted estimates and simultaneous uncertainty bounds.
3. Evaluate the decision-specific stopping condition.
4. If certified, return ACT.
5. If uncertified and k < k_max, request b additional audits and repeat.
6. Otherwise return ABSTAIN with the unresolved comparisons.
```

같은 audit 표본으로 decision을 만들고 그 decision의 위험을 낙관적으로 평가하지 않도록 cross-fitting 또는 명시적 sample splitting을 사용한다.

## 4. Stopping conditions

### 4.1 Recalibration certificate

감사자료로 `c_T`의 confidence set `C_k`를 만들고, `C_k` 안에서 가능한 calibration policy들의 target utility 차이에 대한 upper bound `U_cal(k)`를 계산한다.

```text
ACT if U_cal(k) <= ε_cal
```

`C_k`가 좁아도 cutoff가 불연속적으로 변해 utility가 불안정할 수 있으므로, parameter interval width만을 stopping rule로 쓰지 않는다. downstream utility stability가 중심이다.

### 4.2 Selection certificate

각 candidate `m`에 대해 다른 policy `j`가 얼마나 더 좋을 수 있는지 paired query difference의 simultaneous upper confidence bound를 계산한다.

```text
U_sel(m, k) = max_j UCB_α( μ_j - μ_m )
ACT with m_hat if U_sel(m_hat, k) <= ε_sel
```

어떤 policy도 조건을 만족하지 못하면 더 감사하고, `k_max`에서 여전히 실패하면 abstain한다.

### Guarantee claim boundary

simultaneous bounds가 명목 coverage를 만족하면 선택된 policy의 ε-regret certificate가 성립한다. 그러나 실제 논문에서 finite-sample guarantee를 주장하려면 bound construction의 가정, multiple-policy correction, sequential reuse를 모두 증명하거나 검증해야 한다. 그 전까지는 **empirically calibrated certificate**라고만 부른다.

## 5. Cost accounting

두 축을 동시에 기록한다.

- `T`: audited target query 수
- `B`: query–document pair judgment 수

각 audit action은 다음 필드를 가져야 한다.

```text
dataset, query_id, document_id, judgment, inclusion_probability,
annotator_or_source, judged_at, cost_seconds, batch_id
```

`nG(q)`를 알기 위해 complete judgment가 필요한 경우 그 비용을 숨기지 않는다. sparse qrels만 사용하면 `B`를 실제 인간 annotation cost로 해석하지 않는다.

## 6. Research questions

- **RQ1:** decision-specific planner는 fixed `k`보다 적은 평균 비용으로 calibration loss 기준을 만족하는가?
- **RQ2:** planner는 policy selection의 ε-regret와 잘못된 확신을 사전 risk 수준 안에서 통제하는가?
- **RQ3:** calibration과 selection의 stopping budget 차이는 policy gap, menu size, shift, metric에 의해 어떻게 달라지는가?
- **RQ4:** prospective target collection에서 개발 데이터로 고정한 planner의 coverage와 비용 이점이 유지되는가?

RQ3은 단순 subgroup 탐색이 아니라, 핵심 현상의 자명성을 제거하기 위한 mechanism study다.

## 7. Evaluation program

### Controlled simulation

독립적으로 조작할 축:

- policy menu size: 2, 3, 5, 10
- best–second-best utility gap
- query-level variance와 policy correlation
- shift strength와 type
- judgment missingness/coverage
- calibration sensitivity: 작은 `c` 변화가 cutoff에 미치는 영향

목적은 “selection이 원래 더 어렵다”를 재확인하는 것이 아니라, 어떤 요인이 budget gap을 만드는지 분해하는 것이다.

### Retrospective collections

기존 BEIR 13개는 method development, debugging, heterogeneity analysis에만 사용한다. confirmatory language를 사용하지 않는다.

### Prospective collections

최소 한 개의 새로운 collection을 다음 순서로 잠근다.

1. dataset version과 judgment regime 고정
2. retriever·candidate pool 고정
3. metric, tolerance, risk, maximum budget 고정
4. code hash와 analysis plan 등록
5. target labels 공개
6. 단 한 번의 primary analysis

collection 후보는 judgment depth, license, 재현 가능성, 기존 노출 여부를 조사한 뒤 `03_data/DATA_REGISTRY.yaml`에서 결정한다.

## 8. Baselines

- fixed audited-query budgets
- random audit without sequential stopping
- classical topic/sample-size planning adapted to the same loss
- standard limited-label policy selection baseline
- full-target scalar reference as a ceiling, not a deployable baseline
- optional stratified/active audit는 random core가 완성된 뒤 동일 `T`와 `B`에서만 비교

## 9. Primary endpoints

method freeze에서 정확한 수치를 고정한다. 현재 구조는 다음과 같다.

- calibration: `Pr(L_cal <= ε_cal)`, mean/worst-case loss, stopping budget
- selection: `Pr(L_sel <= ε_sel)`, regret distribution, wrong-confidence rate
- planner: coverage, average/median `T`, available 경우 `B`, abstention rate
- safety: `Pr(ACT and loss > ε)`

가장 중요한 endpoint는 단순 성능이 아니라 **잘못된 확신의 비율**이다.

## 10. Kill and downgrade criteria

- fixed budget과 비교해 비용 또는 safety 이득이 없으면 planner superiority claim을 폐기한다.
- nominal risk와 empirical wrong-confidence가 지속적으로 맞지 않으면 certificate 표현을 폐기한다.
- budget gap이 menu size와 policy gap으로 전부 설명되면 “decision-specific phenomenon” 주장을 축소한다.
- prospective target에서 실패하면 실패를 primary result로 보존하고 일반화 주장을 폐기한다.
- pair-level cost를 재구성하지 못하면 논문 전체를 audited-query budget으로 한정한다.
