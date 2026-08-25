# PROSPECTIVE LOCK — 2026-08-25 (P4 primary run pre-registration)

이 문서는 **target collection의 어떤 파일도 다운로드·열람하기 전에** 작성·저장되었다.
이후 이 문서의 어떤 항목도 변경할 수 없다. Primary run은 단 한 번이며, 실패해도
덮어쓰지 않고 논문의 결과로 보고한다 (POD_HANDOFF P4 규칙).

## 0. Freeze 비준

FREEZE_PROPOSAL_v0.3은 2026-08-25 사용자 위임("가장 좋은 연구를 만들어라")에
따라 **비준됨**으로 기록한다 (DECISIONS.md D-019). 값: ε_cal=0.005, ε_sel=0.01,
α=0.1, looks {10,30,50,70,90}∩[≤n/2], Bonferroni-corrected paired bootstrap
(selection: α/(looks×(M−1)), recal: α/looks), selection 인증서는 LOO
cross-fitting (`40_planner_replay.py` 구현 그대로).

## 1. Target collection (규칙 기반 선택 — 결과를 보고 고른 것이 아님)

- **BEIR `cqadupstack`의 subforum 중 알파벳 순 첫 번째 = `android`.**
- 선택 이유(사전 명시): (a) 개발에 사용된 13개 collection에 포함된 적 없음,
  (b) 원본 candidate 파이프라인(BM25+3 dense, 동일 feature/schema)을 CPU로
  재현 가능한 corpus 규모, (c) BEIR 표준 배포판으로 버전 고정 가능.
- 대안(TREC-DL run-set, BRIGHT)은 PROSPECTIVE_PROTOCOL_v0.1에 기록된 대로
  secondary 후보로 남긴다.
- 예상 특성(문헌 지식, 데이터 미열람): relevance-only qrels, 낮은 nG —
  "hurt corner" 영역. 이는 난이도가 높은 정직한 테스트이며, abstain 다수가
  나와도 그것이 planner의 올바른 행동일 수 있다.

## 2. Candidate 구성 (원본 파이프라인 고정)

- 소스: shift-study `src/build_candidates.py` + `common.py`
  (commit ef825e1d) 로직 그대로. 변경은 **CPU 실행을 위한 device 인자와
  batch 크기뿐** (수치 영향 없음; deviation으로 기록).
- 시스템: bm25s BM25 + {all-MiniLM-L6-v2, all-mpnet-base-v2,
  msmarco-MiniLM-L6-cos-v5}, K0=10, M=30, 동일 feature
  (score_norm, rank, consensus, lexoverlap).
- qrels는 다운로드 번들에 포함되어 있으나, qrels 접근은 (a) candidate 라벨
  기록(감사자 대역), (b) 사후 평가 두 지점뿐이다. 어떤 튜닝·선택에도
  사용하지 않는다 (leakage 테스트로 검증).

## 3. 모델 학습 (target 정보 무접촉)

- 확률 모델: 13개 development collection 전체 pool로 학습
  (CalibratedClassifierCV(LogisticRegression, sigmoid, cv=3), StandardScaler,
  MAX_TRAIN=400,000, rng seed 0 — `20_budget_curves.py`와 동일).
- glob threshold τ와 trunc 회귀도 13개 development pool에서만 학습.
- target(android)은 어떤 학습·튜닝에도 사용되지 않는다 (LODO의 극한 형태 =
  완전 외부 전이).

## 4. Primary run 설계

- Planner: `40_planner_replay.py`의 frozen 로직 (cross-fit selection,
  look-corrected recal), repeats=50, seed = 5_000_000 + 1000*rep +
  crc32("planner|android") % 100000 (기존 규칙 그대로).
- 두 decision (recalibration, selection) 각각 act/more/abstain + 최종 T,
  true loss는 최종 audit 집합의 여집합에서 평가.
- 참고용 fixed-k budget curve (k grid, 50 reps)도 함께 저장하되 primary
  판정에는 사용하지 않는다.

## 5. 성공 판정 (사전 등록)

- **Primary criterion**: decision별 wrong-certificate rate ≤ α=0.1
  (50회 반복, MC SE≈0.043 — 명목과의 비교는 이 오차를 명시하고 보고).
- Secondary (기술 통계로 보고): act rate, mean T, abstain rate, fixed-k 대비
  비용. **act rate가 낮은 것(다수 abstain)은 실패가 아니다** — 인증 불가능한
  환경에서 인증서를 남발하지 않는 것이 planner의 목적이다.
- 실패 시(wrong-cert > α): 그대로 보고하고 원인 분석은 별도 replication
  섹션에서만 수행한다.

## 6. 실행 환경

- Linux CPU, Python 3.11.10, sklearn 1.9.0, numpy 2.1.2 (scipy 1.17.1 편차
  기존 기록), torch CPU + sentence-transformers (버전은 실행 로그에 기록).
- 이 lock 문서의 sha256은 실행 로그에 기록한다.
