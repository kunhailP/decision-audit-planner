# Utility sensitivity (M7) — recall / ndcg RUN NOTES (2026-08-25)

동일 프로토콜을 `--utility recall`과 `--utility ndcg`로 재실행
(`budget_curves_recall/`, `budget_curves_ndcg/`). 임계값은 각 utility 척도에서
같은 수치(ε_cal=0.005, ε_sel=0.01)를 사용 — 척도 간 직접 비교는 정성적임을 명시.

## 핵심 결과 (성공률 ≥0.9 도달 collection 수)

| utility | cal@k=10 | sel@k=10 | sel@k=100 |
|---|---|---|---|
| set_f1 | 5/13 | 3/13 | 10/13 |
| ndcg   | 5/13 | 3/13 |  9/13 |
| recall | 0/13 | 10/13 | 12/13 |

**비대칭의 방향이 utility에 따라 뒤집힌다**: recall은 집합 크기에 단조라
메뉴의 gap 구조가 붕괴 → selection 자명(평균 regret ~0.002), 대신 scalar
recalibration이 병목(0/13). C3 기제 주장(예산은 decision×utility×menu 기하가
결정)의 직접 증거이자, 고정 k 경험칙 대신 인증서 기반 planner가 필요한 이유.
