# Code and artifact contracts

코드는 논문 뒤에 붙는 부록이 아니라 claim을 만드는 측정장치다. 아래 schema와 실행계약을 충족하지 않는 결과는 headline evidence로 사용하지 않는다.

## Pipeline stages

```text
source data
  -> candidate construction
  -> immutable candidate manifest
  -> audit simulation / sequential planner
  -> row-level decision outcomes
  -> locked summaries
  -> paper tables and figures
```

## Immutable inputs

각 candidate collection은 다음을 가진다.

- data version과 source URL
- source file checksum
- retrieval/model identifier와 revision
- query/document identifier
- score, rank, judgment status, relevance grade
- candidate-generation config
- 생성 코드 commit과 timestamp

원본 artifact는 결과 코드가 덮어쓰지 않는다.

## Required row-level outputs

### `audit_events.parquet`

한 행은 query–document 판단 하나다.

```text
collection, query_id, document_id, batch_id, repeat_id,
inclusion_probability, judgment, judgment_source, cost_seconds, seed
```

### `decision_trace.parquet`

한 행은 sequential step 하나다.

```text
collection, repeat_id, decision, audited_queries, pair_judgments,
candidate_policy, estimate, lower, upper, epsilon, alpha,
action, selected_policy, unresolved_comparison, seed
```

### `per_repeat.parquet`

한 행은 collection × repeat × decision의 최종 결과다.

```text
collection, repeat_id, decision, action, final_T, final_B,
selected_policy, reference_policy, loss, success, wrong_confidence,
abstained, probe_query_ids, evaluation_query_ids, seed
```

### `summary.parquet`

row-level 결과에서만 만든다. 수동 입력 숫자를 허용하지 않는다.

## Split invariants

- probe/audit query와 evaluation query는 같은 repeat에서 겹치지 않는다.
- prospective target label은 model fitting, tolerance choice, stopping-rule tuning에 사용하지 않는다.
- policy menu는 target 결과를 보기 전에 고정한다.
- Python `hash()`는 seed 생성에 사용하지 않는다.
- dataset별 평균만 저장하지 않는다.

## Tests

### Unit

- regret의 부호와 범위
- simultaneous comparison에서 자기비교 제외
- stopping condition boundary (`<= ε`)
- abstain at `k_max`
- deterministic seed derivation
- query/pair budget accounting

### Statistical

- known synthetic DGP에서 nominal coverage
- null policy gap에서 wrong-confidence control
- large-gap setting에서 stopping budget 감소
- menu size 증가에 따른 correction 작동

### Leakage

- audit/evaluation ID intersection이 비어 있음
- target label access가 freeze 이후 평가 stage에만 존재
- prospective config hash mismatch 시 실행 중단

### Reproduction

- tiny fixture로 2분 이내 smoke test
- precomputed small artifact에서 headline statistic 재현
- clean environment에서 paper figures 생성

## Failure behavior

입력 누락, schema mismatch, checksum mismatch가 있으면 빈 결과를 저장하지 말고 non-zero exit로 중단한다. 실패 원인은 run manifest에 남긴다.

## Pod boundary

대규모 실행의 입력·반환계약은 `../00_admin/POD_HANDOFF.md`를 따른다. Pod 반환물은 `../09_artifact/pod_return_manifest.template.json` 형식의 manifest를 가져야 하며, 로컬 검증을 통과하기 전에는 결과 폴더로 승격하지 않는다.
