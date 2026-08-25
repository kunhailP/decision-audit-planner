# 현재 상태와 다음 게이트

업데이트: 2026-08-25 (E02 복구 + G2 개발 증거 — `EVIDENCE_RECOVERY_2026-08-25.md`)

## 2026-08-25 진행 (G2 개발 트랙)

- [x] P2 budget curves: k∈{5,10,20,50,100}×50회, row-level 보존 (`05_results/budget_curves/`), F1 그림
- [x] Freeze proposal v0.3 작성 (`01_design/FREEZE_PROPOSAL_v0.3.md`) — **사용자 비준 대기**
- [x] C3 simulation: 36 cell 전부 wrong-cert ≤ α; recal 인증서 look-보정 결함 발견·수정 (`05_results/simulation/`)
- [x] Sequential planner + 13개 replay: 전체 wrong-cert 0.035; **in-sample 인증서 anticonservative 발견(scifact 0.36) → LOO cross-fitting으로 해결** (`05_results/planner_replay/`, ablation 보존)
- [x] M7 지표 민감도: recall에서 비대칭 방향 역전 확인 — C3 기제 강화 (`05_results/budget_curves_recall|_ndcg/`)
- [x] 테스트 스위트 21개 all green (`04_code/tests/run_tests.py`) — legacy 재현·leakage·재생성 포함
- [x] 논문 초안 v0.3 (`06_paper/DRAFT_v0.3.md`), prospective 프로토콜 v0.1 (`03_data/PROSPECTIVE_PROTOCOL_v0.1.md`)
- [x] Freeze 비준 (D-019, 사용자 위임) + prospective lock (cqadupstack-android, 다운로드 전 커밋)
- [x] **P4 primary run 통과** — wrong-cert recal 0.00 / selection 0.08 ≤ α=0.1 (50 reps, `05_results/prospective_android/`)
- [ ] Kaggle v3 백업, GitHub push(토큰 대기), Pod-A(G5 clean-room), Pod-B(BRIGHT)

## North-star update

- [x] 연구 허브 v0.2 구조 생성
- [x] 과학적 설계 기준을 top ML evaluation / SIGIR full-paper 수준으로 상향
- [x] retrospective budget curve와 deployable method를 구분
- [x] Decision-Specific Audit Planner의 v0.2 interface 작성
- [x] claim–evidence matrix와 reviewer-grade quality gates 작성
- [ ] tolerance, risk, sequential interval method를 simulation 전에 고정
- [x] candidate artifact 복구 또는 재생성 — 2026-08-25 Kaggle 백업에서 복구, provenance 검증 및 byte-identical 재현 완료

candidate-level artifact 생성은 연구자가 별도 Pod에서 진행한다. 따라서 이것은 로컬 작업 전체를 멈추는 blocker가 아니라 **Pod evidence dependency**다. 반환 전에는 C1 이상의 실증 claim을 갱신하지 않되, 로컬에서는 method freeze·문헌 audit·fixture/test 구현을 병렬 진행한다.

## Dual-track execution

- [x] Local–Pod 책임 경계 작성
- [x] Pod P0–P4 실행 단계 정의
- [x] Pod return manifest template 작성
- [ ] P0/P1 입력 bundle의 code/config hash 고정
- [ ] Pod P1 반환 artifact 검증
- [ ] v0.2 planner용 P2/P3 runner 전달

## 완료

- [x] 기존 DXW 폴더와 shift-study의 논리적 충돌 확인
- [x] 새 컨퍼런스 프로젝트 폴더 분리
- [x] 핵심 결정을 recalibration과 selection으로 축소
- [x] “labels”와 “audited queries”의 단위 구분
- [x] 1세대 정치학 프로젝트 종결, `_legacy/`로 분리 (D-018)

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
- [x] 누락된 `runs/candidates/`의 원본 보관 위치 확인 — git에 커밋된 적 없음(.gitignore), Kaggle `kunhail/shift-study-artifacts`에서 13개 전체 복구 (2026-08-25)
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
