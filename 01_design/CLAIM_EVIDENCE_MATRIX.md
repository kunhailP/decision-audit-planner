# Claim–evidence matrix

이 파일은 프로젝트의 중심 통제표다. 모든 실험, 표, 그림, 초록 문장은 아래 claim 중 하나를 지지하거나 반박해야 한다.

## Claim ladder

### C0 — Corrective claim

**Claim:** 기존 `k=10`은 10 labels가 아니라 10 audited queries이며, calibration과 selection 결과는 서로 다른 decision loss로 해석해야 한다.

- 필요한 증거: 기존 코드 line audit, artifact schema, 수치 재현
- 상태: 부분 충족
- 논문 가치: 파일럿 교정. 단독 publishable contribution 아님

### C1 — Empirical diagnostic

**Claim:** 동일한 target audit 표본의 sufficiency는 calibration과 policy selection에서 체계적으로 다르다.

- 필요한 증거: dataset × k × repeat row-level curves
- 필수 통제: menu size, policy gap, query variance, metric
- 상태: 미검증
- 실패 시: decision asymmetry 주장을 폐기하고 조건부 결과만 보고

### C2 — Method claim

**Claim:** Decision-Specific Audit Planner는 tolerance와 risk를 입력받아 act, collect-more, abstain을 결정한다.

- 필요한 증거: 완전한 algorithm, unit test, simulation coverage, baseline comparison
- primary endpoint: wrong-confidence rate와 평균 audit cost
- 상태: 설계안만 존재
- 실패 시: methodology paper가 아니라 retrospective study로 강등

### C3 — Mechanism claim

**Claim:** 필요한 budget 차이는 decision 이름 자체가 아니라 menu size, policy gap, outcome variance, calibration sensitivity의 조합으로 설명할 수 있다.

- 필요한 증거: controlled simulation과 collection-level heterogeneity
- 상태: 미검증
- 논문 역할: 자명한 결과라는 심사 비판을 해소

### C4 — Generalization claim

**Claim:** 개발에 쓰지 않은 target collection에서도 planner가 사전 고정한 risk/tolerance 기준을 유의미한 비용으로 만족한다.

- 필요한 증거: prospective locked evaluation
- 상태: 미검증
- 실패 시: top-route 포기, TMLR도 일반화 문장을 축소

## Evidence registry

| Evidence ID | Artifact | Supports | Status | Leakage risk | Required action |
|---|---|---|---|---|---|
| E00 | original source at commit `ef825e1` | C0 | available | low | immutable hash record |
| E01 | `block1_confirm/per_query.csv` | C0 only | available, misnamed | high for new claims | do not use for curves |
| E02 | candidate-level inputs | C1–C3 | missing | unknown | recover or regenerate |
| E03 | repeated audit outcomes | C1–C3 | missing | controllable | build v0.2 runner |
| E04 | controlled simulation | C2–C3 | missing | low | freeze DGP grid |
| E05 | prospective target | C4 | not selected | must remain locked | data registry decision |
| E06 | clean-room artifact replay | C0–C4 | missing | low | artifact audit at G5 |

## Figure contract

- **F1:** fixed-budget calibration vs selection success curves — C1
- **F2:** planner risk–cost frontier and abstention — C2
- **F3:** controlled menu-gap mechanism map — C3
- **F4:** prospective expected vs observed certificate performance — C4
- **F5:** failure taxonomy by collection and judgment coverage — limitations

F1만 완성된 논문은 top-route가 아니다. C2와 C4가 없으면 방법론 flagship claim을 쓰지 않는다.

## Abstract release rule

초록에 들어갈 수 있는 동사는 claim level에 따라 제한한다.

- C0: `revisit`, `correct`, `reframe`
- C1: `find`, `document`, `show in the studied collections`
- C2: `propose`, `evaluate`
- C3: `attribute`, `explain` — 통제결과가 있을 때만
- C4: `generalizes`, `maintains` — prospective endpoint가 통과할 때만
