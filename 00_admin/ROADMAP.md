# Research roadmap

기준일: 2026-08-20  
원칙: 발표 일정이 논문의 논리를 결정하지 않는다. DXW에서는 현재 게이트까지의 완결된 증거만 발표한다.

## Track A — DXW conference package

DXW 발표의 목적은 완성되지 않은 flagship claim을 과장하는 것이 아니라, 기존 연구의 해석을 교정하고 새 방법의 필요성과 파일럿 결과를 명확히 보여주는 것이다.

### Minimum defensible package

- 기존 `k=10` 결과와 산출물의 정확한 재현
- “10 labels”가 아니라 “10 audited queries”라는 비용 단위 교정
- recalibration과 selection의 estimand·loss 차이 명시
- 최소 한 개의 재구성된 dataset에서 `k`별 반복표집 곡선
- method v0.2의 입력·출력·유보 조건
- 확인된 실패조건과 아직 답하지 못한 질문

### Conference claim ceiling

새로운 locked collection이 없으면 “일반적으로 작동한다”거나 “필요 예산을 정확히 권고한다”고 주장하지 않는다. 이 경우 발표는 **retrospective diagnostic + method proposal**이다.

## Track B — flagship paper

대규모 계산은 `POD_HANDOFF.md`에 따라 별도 Pod에서 실행한다. 로컬은 연구설계와 source of truth를 유지하고, Pod는 고정된 입력을 실행해 검증 가능한 artifact를 반환한다.

### Phase 1: Evidence recovery

- candidate artifact를 백업에서 찾거나 원 pipeline으로 재생성
- source commit, dataset version, retrieval model, checksum 기록
- query/pair-level schema 검증
- 기존 headline number를 row-level artifact에서 재생성

실행 주체: Pod P0–P1. 로컬은 반환 bundle의 hash, schema, leakage를 검증한다.

### Phase 2: Method implementation

- fixed-budget retrospective curve
- sequential decision-specific planner
- simultaneous comparison for multiple policies
- `act / more audits / abstain` 출력
- coverage와 ε-regret을 검증하는 simulation

구현·작은 fixture는 로컬, GPU/대규모 simulation은 Pod P3에서 수행한다.

### Phase 3: Development study

- 기존 13개 collection은 전부 development/retrospective로 사용
- menu size, policy gap, metric, shift, judgment coverage sensitivity
- method와 baseline을 동일한 audit cost에서 비교
- failure taxonomy 작성

### Phase 4: Prospective validation

- 새 collection과 split을 결과 전에 고정
- planner hyperparameter, tolerance, stopping rule을 고정
- holdout label을 한 번만 열어 최종 평가
- 수정이 필요하면 첫 결과를 보존하고 별도 replication으로 기록

### Phase 5: Artifact and submission

- 빈 환경에서 단일 실행경로로 표·그림 재생성
- 모든 주장–증거 연결 확인
- 독립적인 red-team review 두 차례
- `SUBMISSION_STRATEGY.md`의 branch 기준으로 venue 선택

## Research maturity milestones

- **M1 — Correct:** 기존 결과와 비용 단위를 정확하게 설명한다.
- **M2 — Reproducible:** 제3자가 같은 row-level 결과를 만든다.
- **M3 — Methodological:** 새 target에서 사용할 수 있는 planner를 제공한다.
- **M4 — Explanatory:** 언제·왜 decision budgets가 달라지는지 통제 실험으로 설명한다.
- **M5 — Prospective:** 개발에 쓰지 않은 collection에서 사전 고정된 성공 기준을 만족한다.
- **M6 — General:** retrieval 한 설정을 넘어 metric·policy family가 바뀌어도 원리가 유지되는 범위를 밝힌다.

TMLR-ready의 최소선은 M1–M5다. 상위 ML/IR venue를 설득하려면 M6 또는 이에 준하는 이론적·실증적 깊이가 필요하다.
