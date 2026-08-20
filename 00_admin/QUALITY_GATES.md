# Reviewer-grade quality gates

각 게이트는 “작업했다”가 아니라 아래 증거가 파일로 존재할 때만 통과한다.

## Q0 — Question ownership

- 한 문장 문제정의가 retrieval을 넘어 이해 가능하다.
- 가장 가까운 선행연구 다섯 편과의 차이가 주장 단위로 설명된다.
- 기존 연구 두 개를 병치한 것 이상의 method contribution이 있다.

**Fail if:** 핵심 결과가 “selection이 calibration보다 어려웠다”라는 관찰에 그친다.

## Q1 — Formal specification

- target quantity, sampling unit, decision loss, tolerance, risk가 수식으로 고정되어 있다.
- query budget과 pair-judgment budget이 분리되어 있다.
- `abstain`과 `collect more`의 조건이 구현 가능하다.
- finite-sample guarantee를 주장할 경우 그 가정과 검증범위가 적혀 있다.

**Fail if:** full target 결과를 본 뒤에만 필요한 budget을 알 수 있다.

## Q2 — Identification and leakage

- development와 prospective target이 완전히 분리되어 있다.
- target label이 calibration model, threshold, stopping hyperparameter에 누출되지 않는다.
- qrels hole과 judged-pool coverage가 측정·보고된다.
- full-target reference가 실무에서 무엇의 ceiling인지 정확히 정의된다.

**Fail if:** 기존 BEIR 13개 중 일부를 새 confirmatory set이라고 부른다.

## Q3 — Baselines and mechanisms

- fixed budget, standard power/sample-size rule, random audit와 비교한다.
- 관련 label-efficient selection 또는 IR evaluation baseline과 비교한다.
- menu size와 true policy gap을 독립적으로 조작한다.
- method의 각 구성요소에 대한 ablation이 있다.

**Fail if:** 우리 방법만 다른 tolerance나 더 많은 판단을 사용한다.

## Q4 — Statistical validity

- 사전 고정한 primary endpoint가 하나 있다.
- dataset/query/repeat 구조에 맞는 uncertainty를 보고한다.
- selection은 accuracy뿐 아니라 ε-regret과 catastrophic failure를 보고한다.
- planner는 coverage, average budget, abstention rate를 함께 보고한다.
- 평균뿐 아니라 collection별 결과와 worst-case를 공개한다.

**Fail if:** n=4 dataset bootstrap을 일반 모집단 신뢰구간으로 해석한다.

## Q5 — External validity

- 적어도 하나의 새, locked collection에서 prospective validation을 한다.
- standard ranking metric과 set-valued retrieval metric을 모두 점검한다.
- 결과가 실패한 collection도 제외하지 않는다.
- 어떤 shift와 judgment regime까지 일반화하는지 경계를 명시한다.

**Fail if:** development 결과를 확인한 뒤 holdout 정의를 바꾼다.

## Q6 — Reproducibility

- 데이터와 artifact에 provenance, version, checksum이 있다.
- 모든 headline table/figure는 row-level 결과에서 재생성된다.
- seed, environment, command, runtime, hardware 요구가 기록된다.
- 빠른 smoke test와 핵심 통계 단위테스트가 있다.
- 장기 실행은 작은 fixture와 precomputed artifact로 검증 가능하다.

**Fail if:** 결과가 콘솔, notebook state 또는 특정 로컬 경로에만 존재한다.

## Q7 — Paper integrity

- abstract의 각 문장이 claim–evidence matrix의 행과 연결된다.
- novelty, limitation, negative result를 같은 기준으로 보고한다.
- “oracle”, “labels”, “holdout”, “significant”를 정의 없이 사용하지 않는다.
- figure caption만 읽어도 단위·분모·오차막대·반복수가 드러난다.

**Fail if:** 발표용 스토리가 결과의 확증수준보다 강하다.

## Venue release rule

- **Top-route eligible:** Q0–Q7 모두 통과하고, C2–C4 claim이 실제로 성립
- **TMLR-route eligible:** Q1–Q7 통과, 방법은 유용하지만 C4의 범용성 또는 broad significance가 제한적
- **Not submission-ready:** Q1, Q2, Q4, Q5, Q6 중 하나라도 실패
