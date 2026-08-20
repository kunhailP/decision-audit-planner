# Results contract v0.2

결과는 `01_design/CLAIM_EVIDENCE_MATRIX.md`의 claim을 판정하기 위해서만 생성한다.

## Required row-level artifacts

- `audit_events.parquet`
- `decision_trace.parquet`
- `per_repeat.parquet`
- `summary.parquet`
- `deviations.md`
- `run_manifest.json`

정확한 schema는 `04_code/CONTRACTS.md`가 기준이다.

## Required figures

- `fig1_fixed_budget_curves.*`: calibration과 selection의 fixed-budget success/regret
- `fig2_planner_risk_cost.*`: planner의 wrong-confidence–cost–abstention frontier
- `fig3_mechanism_map.*`: menu size × policy gap × variance에 따른 budget
- `fig4_prospective_validation.*`: expected certificate와 observed loss
- `fig5_failure_taxonomy.*`: collection/judgment regime별 실패조건

## Headline restrictions

- C1 이전에는 전체 평균으로 현상을 선언하지 않는다.
- C2 이전에는 method, planner superiority, certificate라는 표현을 결과 문장에 쓰지 않는다.
- C4 이전에는 generalizes, robust across domains라는 표현을 쓰지 않는다.
- success에 도달하지 못한 budget은 외삽하지 않는다.
- ACT 뒤 loss가 tolerance를 넘은 `wrong-confidence`를 숨기지 않는다.
- abstention을 failure에서 제외하지 않고 별도 결과로 보고한다.

## Current status

`artifact_inventory.json`은 기존 증거의 부재를 기록한 inventory다. 새 method 결과가 아니다. candidate-level inputs가 복구되기 전까지 이 폴더에 headline figure를 만들지 않는다.
