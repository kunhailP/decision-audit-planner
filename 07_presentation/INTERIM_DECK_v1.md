# 중간발표 구성안 v1 — 15장 (2026-08-25)

원칙: 슬라이드마다 "숫자 한 방" 하나. claim ceiling 준수 (retrospective
diagnostic + method proposal; "일반적으로 작동한다" 금지). 어휘: 슬라이드
1–2 "불확실성" → 3부터 "감사(audit)". D-005: 항상 "감사된 query" (labels 아님).

## I. 도입 — 왜 내가 이 문제인가 (1–4)

1. **정직한 불확실성** — "환경이 바뀌어도 무너지지 않는 불확실성을 연구합니다."
   숫자: 빈곤 지표 90% CI → 실제 커버리지 **9%**. 계보: poverty-shift-inference,
   Wrong Unit of Uncertainty (PA 투고 준비).
2. **실전에서 터진 문제 (2026-05 Kaggle)** — 스위스 법률 IR, 422팀, 상위 ~10%.
   숫자: 학습 이득 vs LB 이득 **r ≈ −0.44, 부호 일치 33%**. 산점도 1장.
3. **우연이 아니라 법칙** — threshold law `p_add > tp₀/(n₀+nG)`, corner map.
   숫자: **부호 일치 100%** (32,089 queries), Spearman 0.995. 사전등록 재현.
4. **질문의 전환** — "감사가 얼마나 필요한가?"는 결정에 따라 다르다.
   숫자: 같은 k=10이 보정엔 충분(13/13), 선택엔 부족(SAFETY 0/4).
   → "오늘은 확인된 것과 검증 중인 것의 경계를 그대로 보여드립니다."

## II. 문제 정의와 연구 설계 (5–8)

5. **두 개의 결정, 하나의 표본** — recalibration(스칼라 보정) vs policy
   selection(3개 중 선택). 용어 교정: "10 labels"가 아니라 "10 audited
   queries" — 비용 축 T(query)와 B(pair judgment)의 구분.
6. **주장 사다리와 게이트** — C0(교정)→C1(진단)→C2(방법)→C3(기제)→C4(일반화).
   개발 13개는 retrospective(D-007), 확증은 잠근 새 collection에서 단 한 번.
   사전등록·row-level artifact·append-only 규율 소개.
7. **방법: Decision-Specific Audit Planner** — 인터페이스 한 줄:
   `입력: 결정, 허용오차 ε, 위험 α → 출력: act / collect-more / abstain`.
   인증서 = look·비교 보정된 bootstrap 경계 (Proposition 1–2, union bound).
   **abstain은 실패가 아니라 정직한 출력.**
8. **실험 설계** — (a) k∈{5..100}×50회 budget curve (probe/eval 분리, LODO),
   (b) 통제 simulation (gap×menu×noise 36 cell), (c) 13개 replay,
   (d) **prospective lock: 데이터 다운로드 전에 커밋** (sha256 제시).

## III. 진행 결과 (9–12)

9. **C1 — 결정 비대칭 실측** (그림 F1). 숫자: 성공률≥0.9 도달이 k=10에서
   보정 5/13 vs 선택 3/13; 선택은 k=100에도 10/13.
10. **C3 — 기제: 결정의 이름이 아니라 기하다** (그림 F3 + utility 표).
    숫자: **recall로 바꾸면 비대칭이 역전** (선택 10/13 자명, 보정 0/13).
    trec-covid(gap 큼) k=5에 선택 확정 vs scifact(근접 메뉴) k=100에도 미해결.
    → 고정 k 경험칙이 불가능한 이유 = planner가 필요한 이유.
11. **C2 — planner 검증** (그림 F2). 숫자: simulation 36 cell 전부
    wrong-certificate ≤ α=0.1; 13개 replay 전체 **0.035**.
    교훈 한 컷: in-sample 인증서는 위험 (scifact 0.36) → LOO cross-fitting으로
    안전+효율 동시 개선 (T 54→47). "우리 스스로의 결함을 잡아 고친 기록."
12. **C4 — prospective 1차 (진행 중/결과)** — cqadupstack-android,
    규칙 기반 선택(알파벳 첫 subforum), lock 후 단 한 번의 primary run.
    [P4 결과 나오면 사전등록 기준 판정 그대로; 안 나왔으면 "실행 중" 상태로.]

## IV. 경계와 로드맵 (13–14)

13. **확인된 것 vs 검증 중인 것** — 2열 표.
    확인: H1 법칙, probe 충분성(보정), C1 비대칭(개발 데이터), planner 위험
    통제(개발+simulation), byte-identical 재현성.
    검증 중: C4 일반화(prospective), pair-비용 축, 표준 IR 지표 전반.
    금지 주장 명시: "일반적으로 작동한다" (아직) 안 함.
14. **로드맵** — clean-room 재현 감사(G5) → 2차 prospective(BRIGHT) →
    투고. (venue명은 슬라이드에 쓰지 않고 질문 나오면 답변.)

## V. 마무리 (15)

15. **연구 프로그램의 수렴** — 3부작 지도: 빈곤 지표(모집단 이전) / 서베이
    (단위 교정) / 검색 감사(결정별 인증서) → "shift 하의 정직한 추론".
    수미상관: "이 planner의 다음 적용처는 제가 출발한 곳 — 새 코퍼스에서의
    정치 텍스트 측정 검증입니다." (novelty 주장은 ML 평가 방법론에 한정)

## 예상 질문 대비 (Q&A)

- **"라벨을 그냥 더 모으면 되지 않나?"** → 비용 축이 두 개(T, B)이고 실무 예산
  은 유한; 핵심은 '몇 개'가 아니라 '언제 멈추고 언제 유보하는가'의 인증서.
- **"Sakai topic-set design과 뭐가 다른가?"** → 그건 고정 예산의 사전 설계;
  우리는 결정별·순차적·abstain 포함. (verified 비교표 있음)
- **"abstain이 나오면 실무자는 뭘 하나?"** → 더 감사하거나, 결정을 바꾸거나
  (메뉴 축소), 배포를 보류 — 잘못된 확신으로 배포하는 것보다 싸다.
- **"13개가 이미 노출됐는데 믿을 수 있나?"** → 그래서 development라 부르고,
  확증은 lock된 새 collection의 단 한 번 run으로만 (lock 해시 제시).
- **"정치학과 무슨 상관인가?"** → 동기이자 다음 적용처; 기여 자체는 일반
  평가 방법론 (슬라이드 1, 15).
