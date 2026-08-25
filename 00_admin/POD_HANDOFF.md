# Local–Pod execution contract

기준일: 2026-08-20  
목적: 연구판단과 대규모 계산을 분리하되, Pod 결과가 로컬 연구설계를 바꾸거나 추적 불가능한 산출물이 되지 않도록 한다.

## 1. Responsibility split

### Local research hub

로컬은 연구의 source of truth다.

- 연구질문, estimand, decision loss
- tolerance, risk, stopping rule의 freeze
- 문헌 검증과 novelty 판정
- dataset role과 prospective protocol
- output schema와 validation test
- 결과 해석, 논문, 발표, 심사 대응
- Pod에 전달할 code/config commit 고정

### Compute Pod

Pod는 계산 실행환경이다.

- raw dataset 다운로드와 version 고정
- corpus embedding과 candidate artifact 생성
- GPU/장기 반복실험 실행
- runtime, hardware, package version 기록
- row-level 결과와 checksum 생성
- 실패 로그와 partial output 보존
- 반환 bundle 작성

Pod에서는 결과를 보고 RQ, metric, tolerance, split, policy menu를 임의로 바꾸지 않는다. 변경이 필요하면 실행을 중단하고 로컬 `DECISIONS.md`에 amendment를 먼저 남긴다.

## 2. Local → Pod handoff

Pod 실행 전에 다음을 하나의 입력 bundle로 고정한다.

```text
code_commit.txt
PROJECT.yaml
config_frozen.yaml
DATA_REGISTRY.yaml
candidate_schema.md
expected_outputs.md
environment specification
run command
```

필수 식별자:

- hub Git commit
- source `shift-study` commit
- dataset version/hash
- model name/revision
- policy menu
- seed derivation rule
- experiment ID

## 3. Pod → Local return bundle

Pod는 raw dataset 전체를 로컬로 복사할 필요가 없다. 다음의 검증 가능한 산출물만 반환한다.

```text
return_manifest.json
logs/
configs/
checksums.sha256
candidates/ or an immutable remote locator
audit_events.parquet
decision_trace.parquet
per_repeat.parquet
summary.parquet
environment.txt
hardware.json
deviations.md
```

candidate가 너무 크면 content-addressed remote location과 작은 sample fixture를 반환한다. headline 결과를 검증하는 row-level artifact는 반드시 로컬 또는 영구 저장소에서 접근 가능해야 한다.

## 4. Acceptance checks

로컬은 반환 bundle을 받으면 결과를 읽기 전에 다음을 검사한다.

1. input code/config hash 일치
2. dataset/model revision 일치
3. 모든 필수 파일 존재
4. checksum 통과
5. schema와 row count 검증
6. probe/audit–evaluation leakage 없음
7. seed와 repeat ID 유일성
8. summary가 row-level 결과에서 재생성되는지 확인

하나라도 실패하면 해당 run은 headline evidence가 아니라 `quarantined run`으로 분류한다.

## 5. Execution sequence

### Pod Run P0 — environment smoke test

- 작은 dataset 또는 fixture 한 개
- candidate 생성부터 summary까지 end-to-end 실행
- 목적: 환경과 schema 검증

### Pod Run P1 — legacy reproduction

- 기존 `k=10` pipeline 재생성
- 기존 headline numbers와 차이 확인
- 목적: C0 종료와 candidate provenance 확보

### Pod Run P2 — retrospective fixed-budget study

- BEIR development collections
- dataset × budget × repeat row-level output
- 목적: C1과 mechanism 설계의 입력

### Pod Run P3 — planner development

- simulation과 retrospective data
- interval/stopping method 비교
- 목적: C2–C3 방법 선택

### Pod Run P4 — prospective run

- 로컬에서 config와 code를 freeze한 후 실행
- target label을 여는 단 한 번의 primary run
- 목적: C4 판정

P0–P3는 수정·재실행 가능하지만 모두 기록한다. P4의 primary result는 실패해도 덮어쓰지 않는다.

## 6. Immediate next handoff

현재 Pod에 바로 전달할 것은 full flagship run이 아니다. 먼저 P0/P1용으로 다음만 고정한다.

- original source commit `ef825e1d35d58d178c50054122ccc9e9ab54012c`
- 기존 13개 dataset과 candidate schema
- `k=10` reproduction command
- candidate/data/model manifest
- row-level output 보존 요구

P1 결과가 기존 수치를 재현하는지 확인한 뒤 v0.2 planner runner를 Pod에 전달한다.

---

# AMENDMENT v2 — 2026-08-25 (D-019 이후)

P0–P3와 P4 primary(cqadupstack-android, CPU)는 **로컬에서 완료**되었다
(`EVIDENCE_RECOVERY_2026-08-25.md`, `05_results/`). 이에 따라 Pod의 남은
계약을 다음 두 가지로 재정의한다.

## Pod-A — G5 Clean-room artifact audit (필수, 제출 전)

- 입력: `09_artifact/` 재현 번들만 (Kaggle v3 백업의 사본). 로컬 hub 접근 금지.
- 실행: 빈 환경에서 문서화된 단일 명령 경로로 headline 수치·그림(F1–F3,
  prospective headline) 전부 재생성.
- 반환: 재생성물 + 원본과의 diff 보고 + 환경 기록. diff가 0이 아니면
  quarantine 후 로컬에서 원인 조사.

## Pod-B — BRIGHT secondary prospective (선택, 리비전 대비)

- 조건: PROSPECTIVE_PROTOCOL_v0.1 옵션 B. **실행 전에 android와 동일한
  lock 문서를 새로 커밋**해야 한다 (subset 선택 규칙 포함).
- GPU로 BRIGHT candidate 빌드(원본 파이프라인) 후 `70_prospective_run.py`
  로직 그대로 1회 primary run. 결과는 성패 무관 보고.
- 이 실행은 android P4 결과에 어떤 영향도 주지 않는다 (별도 collection의
  독립 검증일 뿐).
