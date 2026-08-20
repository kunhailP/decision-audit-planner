# 결정 로그

## D-001 — 새 작업 폴더를 분리한다

- 날짜: 2026-08-20
- 결정: 기존 `DXW_2026_paper`는 보존하고, 컨퍼런스용 retrieval shift-study를 별도 폴더에서 진행한다.
- 이유: 서로 다른 연구질문과 응용이 한 폴더에서 경쟁하고 있었다.

## D-002 — 논문의 중심은 decision-specific budget이다

- 결정: “라벨이 몇 개 필요한가”가 아니라 “어떤 결정에 라벨이 필요한가”를 묻는다.
- 중심 비교: 성능 보정 대 3-way 정책 선택.

## D-003 — 핵심 결정은 두 개만 둔다

- 포함: recalibration, model/policy selection.
- 제외: abstention을 독립 RQ나 새 방법론으로 만들지 않는다.
- 비고: 판단 유보는 필요할 경우 결과 해석 또는 후속연구에서 다룬다.

## D-004 — audit 방식 비교를 1차 범위에서 뺀다

- 1차 분석은 target query의 단순 무작위 audit만 사용한다.
- deep/shallow/active/PPI 비교는 core result가 성립한 뒤의 확장으로만 검토한다.

## D-005 — 비용 단위를 바로잡는다

- 1차 표본 단위: audited target query.
- 비용 보고 단위: audited query 수. query-document pair 판단 수는 명시적 judgment protocol을 복원한 경우에만 별도로 보고한다.
- 금지 표현: query 열 개를 “10 labels”라고 부르지 않는다.

## D-006 — 불확실성은 평가 도구이지 논문의 정체성이 아니다

- 반복표집, bootstrap, interval은 결과의 안정성을 평가하는 데 사용한다.
- 새로운 uncertainty-inference framework를 논문의 전면에 세우지 않는다.

## D-007 — 기존 BEIR 결과는 탐색적 재분석이다

- 13개 데이터셋 모두 이미 분석 과정에서 노출되었다.
- 기존 untouched-4를 새 논문의 독립 confirmatory holdout이라고 부르지 않는다.
- 새로운 외부 데이터가 추가되기 전까지 주장은 재분석 범위로 제한한다.

## D-008 — 응용 분야를 논문에서 제외한다

- 이 논문은 BEIR 기반 retrieval evaluation에 한정한다.
- 정치학·로비·법학 적용은 동기, 실증 사례, 후속 확장 목록에 포함하지 않는다.
- 새로운 external dataset은 독립 검증이 꼭 필요할 때만 방법론적 benchmark로 검토한다.

## D-009 — 기존 결론을 전제로 분석하지 않는다

- `k=10`에서 recalibration이 충분하고 selection이 부족하다는 결과는 출발 가설이다.
- 새 반복실험에서 뒤집히거나 특정 데이터셋에만 성립하면 그대로 보고한다.

## D-010 — 제목에서도 labels와 audits를 구분한다

- 잠정 제목은 `Audits for What?`을 사용한다.
- 이유: 현재 핵심 예산 단위는 개별 label 수가 아니라 audited target query 수다.
- pair-level judgment protocol을 실제로 구현한 경우에만 `Labels for What?`을 다시 검토한다.

## D-011 — method와 diagnostic study를 구분한다

- retrospective budget curve만 제시하면 empirical IR evaluation study로 부른다.
- methodology paper로 부르려면 pilot 정보에서 decision-specific audit budget을 권고하는 재사용 가능한 절차가 있어야 한다.
- 새로운 uncertainty theory는 요구하지 않지만, 입력·출력·실패조건이 명확한 audit-planning protocol은 요구한다.

## D-012 — 저널 목표는 완성 수준에 따라 정한다

상태: **D-013에 의해 대체됨. 과거 판단 보존용.**

- lean empirical protocol 완성: IRRJ 우선 검토.
- 일반화 가능한 audit-planning method 완성: TMLR 우선 검토.
- formalization·표준 metrics·prospective validation·완전한 artifact까지 갖춘 경우에만 ACM TOIS를 stretch target으로 검토.

## D-013 — 과학적 설계 기준을 상위권으로 올린다

- 날짜: 2026-08-20
- 설계 기준: ICML/NeurIPS/ICLR evaluation paper 또는 SIGIR full paper 수준.
- TMLR은 낮춘 설계의 목표가 아니라, 상위 기준으로 완성한 결과의 범용성·기여 수준에 따라 선택할 수 있는 강한 publication branch다.
- 이 결정은 D-012의 IRRJ/TMLR/TOIS 선형 ladder를 대체한다.

## D-014 — retrospective curve를 method로 부르지 않는다

- 최종 기여는 `Decision-Specific Audit Planner`다.
- 입력은 decision, policy menu, tolerance, risk, pilot audit이다.
- 출력은 act, collect more audits, abstain과 decision certificate다.
- full-target label을 본 뒤 budget을 설명하는 곡선만 있으면 diagnostic study로 강등한다.

## D-015 — abstention의 역할을 제한한다

- abstention을 세 번째 거대한 RQ나 연구정체성으로 만들지 않는다.
- evidence가 tolerance/risk 기준을 만족하지 못할 때 planner가 반드시 제공해야 하는 출력으로만 포함한다.

## D-016 — 연구 허브를 flagship 중심으로 운영한다

- `DXW_2026_shift_audit`을 유일한 활성 flagship 폴더로 지정한다.
- 과거 정치·법학 프로젝트는 legacy/source material이며 현재 논문의 동기나 novelty로 자동 승계하지 않는다.
- 새 작업은 claim–evidence matrix에 연결된 경우에만 core에 포함한다.
