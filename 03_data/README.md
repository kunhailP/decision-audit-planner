# Data registry

machine-readable 상태와 prospective selection requirements는 `DATA_REGISTRY.yaml`이 기준이다.

이 폴더에는 원자료를 바로 복사하지 않는다. G1에서 필요한 artifact를 확인한 후 manifest와 해시를 먼저 만든다.

## 1차 출처

- 작업본: `/Users/baggeon-u/Documents/Codex/2026-08-20/new-chat/work/shift-study`
- 핵심 기존 산출물: `runs/block1_confirm/per_query.csv`, `agg.json`, `config.json`
- 핵심 기존 코드: `src/block1_confirm.py`, `src/common.py`

주의: `block1_confirm/per_query.csv`는 파일명과 달리 query-level이 아니라 dataset-level 13행 요약이다. 새 분석의 직접 입력으로 사용할 수 없다.

## G1에서 확인할 필드

- dataset
- query identifier
- probe/evaluation membership
- policy별 per-query outcome
- correction estimate에 사용된 값
- source/target fold membership
- random seed와 repeat identifier

현재 위 필드를 모두 가진 artifact는 발견되지 않았다. 특히 `runs/candidates/`는 저장소에서 제외되어 있다.

## 데이터 원칙

- 원자료는 수정하지 않는다.
- 변환 결과는 생성 스크립트와 함께 저장한다.
- probe query는 같은 반복의 평가에서 제외한다.
- target dataset을 사용하는 모든 학습·튜닝 경로를 기록한다.
- sparse qrels가 unjudged document를 nonrelevant로 취급하는지 명시한다.
- audited query 수와 pair judgment 수를 혼용하지 않는다.

## 이 논문에서 하지 않는 것

- 정치학·로비 데이터 수집
- LLM annotation pipeline 생성
- 법학 또는 제도 텍스트 데이터 결합
- 실제 pair-level annotation cost의 근거 없는 환산
