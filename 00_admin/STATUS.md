# 현재 상태와 다음 게이트

업데이트: 2026-08-20

## North-star update

- [x] 연구 허브 v0.2 구조 생성
- [x] 과학적 설계 기준을 top ML evaluation / SIGIR full-paper 수준으로 상향
- [x] retrospective budget curve와 deployable method를 구분
- [x] Decision-Specific Audit Planner의 v0.2 interface 작성
- [x] claim–evidence matrix와 reviewer-grade quality gates 작성
- [ ] tolerance, risk, sequential interval method를 simulation 전에 고정
- [ ] candidate artifact 복구 또는 재생성

현재 blocker는 문헌이나 문장력이 아니라 **candidate-level artifact 부재**다. 이 blocker가 해결되기 전에는 C1 이상의 실증 claim을 갱신하지 않는다.

## 완료

- [x] 기존 DXW 폴더와 shift-study의 논리적 충돌 확인
- [x] 새 컨퍼런스 프로젝트 폴더 분리
- [x] 핵심 결정을 recalibration과 selection으로 축소
- [x] “labels”와 “audited queries”의 단위 구분

## G0 Scope freeze

- [x] 잠정 RQ 작성
- [x] 잠정 성공 기준 작성
- [x] 기존 코드가 각 성공 기준을 정확히 계산하는지 1차 대조
- [ ] 최종 성능지표를 set-F1 하나로 둘지 nDCG@10을 보조로 둘지 확정

## 다음 — G1 Evidence audit

- [x] 기존 `per_query.csv`가 실제로는 dataset-level 13행임을 확인
- [x] probe query와 evaluation query가 코드에서 분리됨을 확인
- [x] LODO에서 현재 target dataset이 classifier·truncation 학습에서 제외됨을 확인
- [x] `ad_c`가 target의 모든 query로 계산한 scalar `c_star`를 사용함을 확인
- [x] candidate artifact와 pair-cost 정보가 현재 작업본에 없음을 확인
- [ ] 누락된 `runs/candidates/`의 원본 보관 위치 확인 또는 재생성 비용 산정
- [ ] 모든 기존 headline 수치를 새 용어로 다시 계산

## 확인된 제약

- 기존 runner는 `K_PROBE=10`, `REPEATS=20`으로 고정되어 있다.
- 13개 dataset 공통 budget은 query 수 때문에 `{5,10,20}`까지만 안전하다.
- k=50 이상은 충분한 query가 있는 dataset에 한정한 확장 분석이어야 한다.
- 기존 qrels만으로 실제 query-document pair annotation cost를 주장할 수 없다.

## 저널 심사 게이트

- [ ] 기존 topic-set size·active sampling·limited-label model selection과의 차이를 직접 입증
- [ ] retrospective curve를 넘는 audit-planning protocol 여부 결정
- [ ] menu size와 true policy gap sensitivity 추가
- [ ] qrels coverage와 표준 IR metric sensitivity 추가
- [ ] 새로운 retrieval collection에서 prospective validation
- [ ] 완전한 artifact 공개

현 상태의 심사 판정은 `Reject — major redesign 후 재심사 가능`이다. 상세 판정은 `08_review/REVIEWER_REPORT_v0.1.md`에 있다.

## 중단 조건

다음 중 하나가 확인되면 곧바로 새 실험을 돌리지 않고 설계를 수정한다.

- 기존 per-query 산출물만으로 k별 budget curve를 재구성할 수 없음
- probe와 evaluation이 분리되지 않음
- target 정보가 LODO 학습 또는 policy tuning에 누출됨
- full-target reference가 논문에서 주장하려는 실무 기준과 대응하지 않음
