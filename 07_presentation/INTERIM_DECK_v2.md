# 중간발표 구성안 v2 — 20장, "깊이" 중심 (2026-08-25)

전환: v1의 "신뢰성 전시" 프레임 → **"어디까지 파 내려갔는가"** 프레임.
규율 요소(사전등록·lock·byte-identical)는 각 한 줄로만 등장 — 깊이의 부산물로.
그림은 전용 슬라이드(full-bleed)로 분리: F1(9), F3(12), F2(16) + corner map(3).

## I. 도입 — 왜 나인가 (1–4)

1. **정직한 불확실성** — 90% CI → 실제 9%. 계보 두 편.
2. **Kaggle에서 터진 문제** — 422팀, 상위 ~10%, r ≈ −0.44 / 부호 33%.
   (+깊이 한 줄: "라벨 없는 신호 5종을 다 시험했고 전부 실패했다 — v0–v7")
3. **[그림] Corner map + threshold law** — 부호 일치 100%, ρ=0.995.
4. **질문의 전환** — 같은 10개 감사 query: 보정 충분(13/13) vs 선택 실패(0/4).
   "이 비대칭이 진짜인지, 왜 생기는지, 끝까지 들어가 봤습니다."

## II. 문제의 형식화 (5–7)

5. **두 결정, 두 비용 축** — recalibration vs selection; T(audited queries) ≠
   B(pair judgments). "10 labels"라는 말이 왜 틀렸는지 30초.
6. **Planner 인터페이스** — `결정, ε, α → act / collect-more / abstain`.
   인증서의 뼈대(비교·look 보정된 경계, Prop 1–2는 백업 슬라이드).
7. **검증 스택 한눈에** — 4층: budget curves(13개) / 통제 simulation /
   실데이터 replay / 잠근 새 collection 1회. (lock은 여기서 한 줄.)

## III. 깊이의 하강 (8–17) — 발표의 본체

8. **파 내려간 규모** — 13 collections, 33,234 query 해부, k 5단계 × 50반복
   × 3 utility, row-level 전부 보존. "여기서부터 보여드릴 모든 수치는 이
   원자료에서 재생성됩니다" 한 줄.
9. **[그림] F1 — budget curves.** 비대칭 실측: k=10에서 보정 5/13 vs 선택 3/13.
10. **1차 해부: 평균 뒤의 이질성** — 세 collection 사례:
    trec-covid(선택이 k=5에 끝남 — 정책 격차 큼) / scifact(k=100에도 미해결 —
    정책 근접) / quora(반대로 보정이 실패 — 비율 산포). "비대칭은 균질하지 않다."
11. **2차 해부: utility를 바꿔봤다 — 역전.** recall이면 선택 10/13 자명,
    보정 0/13 병목. 표 하나. **"비대칭은 결정의 이름이 아니라 기하가 만든다."**
12. **[그림] F3 — 통제 simulation으로 기제 분해.** budget = f(gap × menu × σ):
    gap 0.1→평균 T 17, gap→0이면 정직한 유보 55–99%.
13. **planner를 실제로 만들었다** — frozen 스펙, simulation 36 cell 전부
    wrong-cert ≤ α. (simulation이 recal 인증서의 look-보정 누락도 잡아냄 — 한 줄.)
14. **3차 해부: 첫 구현은 틀렸다.** 실데이터 replay에서 scifact
    wrong-cert 0.36 — 원인 추적: probe로 추정한 파라미터를 같은 probe로
    평가한 in-sample 낙관. "어디서 어떻게 틀렸는지까지 해부했습니다."
15. **수정: cross-fitting.** LOO 도입 → wrong-cert 0.098→0.052이면서
    **감사 비용도 감소** (평균 T 54→47). 편향 제거가 안전과 효율을 동시에.
16. **[그림] F2 — 13개 replay 최종.** 전체 wrong-cert 0.035; collection별로
    planner가 T=10~90을 스스로 조절, 안 되는 곳은 유보.
17. **외부 검증 1차 (P4) — 통과.** 개발에 안 쓴 collection
    (cqadupstack-android, 699 queries), 결과 보기 전 설정 고정(한 줄),
    단 한 번의 run. 숫자: wrong-cert **recal 0.00 / selection 0.08** ≤ α=0.1
    — 사전등록 기준 양쪽 통과. 보정의 56%는 정직한 유보(이 collection의 비율
    산포 큼) — "안 되는 곳에서 안 된다고 말하는 것"이 전이됨.

## IV. 경계와 다음 (18–19)

18. **확인된 것 / 검증 중인 것** — 2열 표. "일반적으로 작동한다"는 아직 말할
    수 없고, 말하지 않겠다는 것까지가 오늘의 결과.
19. **다음 깊이** — 빈 환경 재현 감사, 2차 외부 collection(BRIGHT),
    pair-비용 축의 실측. (투고 계획은 질문 나오면.)

## V. 마무리 (20)

20. **수렴** — 빈곤 지표 / 서베이 단위 / 검색 감사 3부작 →
    "shift 하의 정직한 추론". 수미상관: 다음 적용처는 정치 텍스트 측정.

## 백업 슬라이드 (질문 대비)

- B1. Proposition 1–2 전문 (union bound 증명 스케치)
- B2. 검증된 관련연구 비교표 (Sakai/Oosterhuis/Okanovic/BAI/PPI — 10편)
- B3. in-sample vs cross-fit collection별 전체 표
- B4. pilot v0–v7 실패 기록 (라벨 무료 신호 5종)
- B5. lock 문서·해시·재현 명령 (재현성 질문 시)

## Q&A 예상 (v1과 동일 + 추가)

- "깊이는 알겠는데 그래서 결론이 뭔가?" → "고정 k 경험칙은 존재할 수 없고
  (utility 역전이 증명), 결정별 인증서만이 답이다 — 그걸 만들었고 위험 통제가
  실측된다(0.035)."
- 나머지 5문항은 v1 참조.
