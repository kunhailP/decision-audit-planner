# Conference Design v0.1

> **Legacy design:** fixed-budget DXW 진단연구의 기록이다. 현재 flagship 설계는 `METHOD_SPEC_v0.2.md`를 따른다.

날짜: 2026-08-20  
상태: G1 코드 대조 전 잠정 고정

## 1. 연구문제

retrieval pipeline을 새로운 target dataset에 적용할 때 개발자는 소량의 query audit를 사용할 수 있다. 그러나 같은 audit budget이 고정된 policy의 성능을 보정하는 데 충분하다고 해서, 여러 policy 중 하나를 선택하는 데도 충분하다는 보장은 없다.

> **중심 질문:** 분포이동 상황에서 인간 검증 예산의 필요량은 그 검증자료로 내리려는 결정에 따라 달라지는가?

## 2. 잠정 제목

**Audits for What? Decision-Specific Validation Budgets for Retrieval under Distribution Shift**

## 3. 논문의 가장 작은 기여

이 논문은 동일한 target audit 표본을 두 가지 용도에 사용하고, 각 용도가 요구하는 최소 예산을 같은 척도로 비교한다.

1. **Recalibration:** 고정된 adaptive policy의 scalar correction을 추정한다.
2. **Selection:** 세 policy 가운데 target 성능이 가장 좋은 policy를 선택한다.

새로운 거대 모델이나 일반적인 uncertainty framework를 제안하지 않는다. 기여는 **검증 예산의 충분성이 decision-specific하다는 사실을 측정 가능한 budget curve로 바꾸는 것**이다.

## 4. 연구질문

### RQ1 — Recalibration budget

고정된 policy의 target-domain scalar correction을 full-target reference에 근접하게 복원하려면 audited target query가 몇 개 필요한가?

### RQ2 — Selection budget

동일한 target audit로 세 policy 가운데 near-best policy를 선택하려면 audited target query가 몇 개 필요한가?

### RQ3 — Heterogeneity, exploratory

RQ1과 RQ2의 예산 차이는 dataset, shift 크기, policy 간 성능격차에 따라 어떻게 달라지는가?

RQ3은 설명적·탐색적 분석이며 새로운 일반법칙으로 주장하지 않는다.

## 5. 데이터와 policy

### 데이터

- 기존 BEIR 13개 target dataset
- 기존 BEIR qrels와 candidate/policy pipeline. 단, 현재 저장된 Block 1 결과는 dataset-level aggregate뿐이며 candidate artifact 복구가 필요하다.
- 각 dataset을 target으로 두는 LODO 구조를 사용하되, 모든 dataset이 이미 노출되었으므로 전체 분석을 재분석으로 표현한다.

### policy menu

기존 Block 1과의 연결을 위해 다음 세 policy를 1차 menu로 고정한다.

- `ad_probe`: target probe로 scalar correction한 adaptive gate
- `glob_probe`: target probe로 조정한 global-threshold policy
- `trunc`: 다른 dataset에서 학습된 target-label-free truncation policy

`ad_c`는 비교 menu가 아니라 **full-target scalar reference**다. 이것을 oracle retrieval 또는 oracle policy라고 부르지 않는다.

## 6. Audit protocol

### 표본 단위

- target dataset에서 audited query를 단순 무작위 추출한다.
- probe query는 같은 반복의 evaluation set에서 제외한다.
- 모든 dataset에 적용하는 core 예산 격자: `k ∈ {5, 10, 20}`.
- 충분한 query가 있는 dataset에서만 표시하는 확장 격자: `k ∈ {50, 100}`.
- 반복 수 잠정값: dataset과 k 조합당 500회. 계산비용 확인 후 늘릴 수 있다.

### 비용 표현

- 주 분석의 x축: audited target queries.
- 보조 보고: candidate artifact와 judgment protocol이 복구된 경우에만 각 k가 요구하는 query-document pair 판단 수의 분포.
- sparse qrels만으로 실제 annotation cost를 복원할 수 없으면 pair-level budget 비교를 논문 주장에 포함하지 않는다.

이 버전에서는 deep/shallow/active sampling을 비교하지 않는다.

## 7. 결과와 성공 기준

### 7.1 Recalibration

각 반복에서 `ad_probe(k)`와 full-target scalar reference `ad_c`의 evaluation-set 성능 차이를 계산한다.

잠정 성공 사건:

```text
abs(F1(ad_probe(k)) - F1(ad_c)) <= 0.005
```

dataset별로 이 사건의 반복표집 성공률을 계산한다.

### 7.2 Selection

probe에서 `ad_probe`, `glob_probe`, `trunc` 중 하나를 선택하고, probe를 제외한 evaluation set에서 regret을 계산한다.

```text
regret(k) = max_m F1(m) - F1(selected_k)
```

잠정 성공 사건:

```text
regret(k) <= 0.01
```

### 7.3 Decision-specific minimum budget

결정 `d`의 최소 예산을 다음처럼 정의한다.

```text
B*_d = 가장 작은 k such that Pr(success_d at k) >= 0.90
```

핵심 비교는 `B*_recalibration`과 `B*_selection`이다. 각 dataset에 적용된 격자 안에서 0.90에 도달하지 못하면 우측 검열된 값으로 보고하며 외삽하지 않는다.

## 8. 검증할 중심 명제

> **H1:** recalibration에 필요한 target audit budget은 policy selection에 필요한 budget보다 작다.

이는 결과가 아니라 검증 대상이다. 데이터셋 과반에서 차이가 없거나 방향이 반대라면 decision-specific asymmetry 주장을 기각한다.

## 9. 분석

### 주 분석

- dataset × k별 recalibration success rate
- dataset × k별 selection success rate
- dataset × k별 mean/median regret
- 두 결정의 `B*` 비교
- 전체 평균과 dataset별 결과를 동시에 보고

### 안정성 평가

- 반복표집 Monte Carlo 오차
- dataset 수준 이질성
- k 격자와 성공 임계값에 대한 민감도
- set-F1 주 분석, nDCG@10은 계산 가능할 때만 보조 분석

bootstrap과 interval은 결과의 안정성을 평가하는 도구이며 별도의 방법론적 기여로 주장하지 않는다.

## 10. 반드시 피할 해석

- query 열 개를 label 열 개로 표현하지 않는다.
- full-target scalar correction을 완전한 oracle retrieval이라고 표현하지 않는다.
- query-level algebraic identity를 경험적 발견이라고 표현하지 않는다.
- 기존 untouched-4 결과를 독립 확증이라고 표현하지 않는다.
- 전체 13개에서는 null인 결과를 4개 dataset 결과만으로 일반화하지 않는다.
- qrels hole을 무시한 실제 annotation-cost 주장을 하지 않는다.

## 11. 핵심 그림

컨퍼런스 버전의 필수 그림은 세 개뿐이다.

1. k에 따른 recalibration 성공률 곡선
2. k에 따른 selection 성공률과 regret 곡선
3. dataset별 `B*_recalibration` 대 `B*_selection` 비교

## 12. core 이후에만 검토할 확장

- deep 대 shallow audit
- disagreement-based active audit
- prediction-powered evaluation
- abstention 또는 sequential stopping
- 새로운 retrieval benchmark에서의 prospective validation

이 항목들은 G4까지 core 결과가 성립한 뒤 별도 amendment로만 추가한다.
