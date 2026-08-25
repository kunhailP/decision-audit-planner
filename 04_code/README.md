# Code plan

상위 통제문서는 `CONTRACTS.md`, 잠정 설정은 `configs/research_v0.2.yaml`이다. 기존 파일명 계획은 구현 순서를 설명하지만, 실제 산출물은 contract의 row-level schema를 따라야 한다.

기존 코드를 그대로 복사하기 전에 새 설계의 추정량과 대응하는지 확인한다.

## 구현된 파이프라인 (2026-08-25)

```text
00_inventory.py          기존 artifact와 필드 점검 (--source 필수: /root/shift-study)
20_budget_curves.py      C1: k={5,10,20,50,100} 반복표집, --utility {set_f1,recall,ndcg}
30_summarize.py          C1 요약: success rate, budget gap, F1 그림 (row-level에서 재생성)
40_planner_replay.py     C2: sequential planner + 13개 development replay, F2
50_simulation.py         C2 coverage + C3 기제 simulation, F3
60_prospective_build.py  P4: target candidate 빌드 (원본 build_candidates.py 로직, CPU)
70_prospective_run.py    P4: prospective primary run (단 한 번, lock 준수)
tests/run_tests.py       unit / leakage / regeneration / statistical (21 tests)
```

candidate 복구(05)와 legacy 재현(10)은 스크립트 없이 완료됨:
`00_admin/EVIDENCE_RECOVERY_2026-08-25.md` (Kaggle 백업, byte-identical `make confirm`).

## 구현 불변조건

- 난수 seed는 명시적으로 저장한다.
- Python `hash()`를 seed에 사용하지 않는다.
- probe와 evaluation을 같은 query로 계산하지 않는다.
- target dataset은 LODO 학습에서 제외한다.
- 모든 headline number는 저장된 row-level 결과에서 재생성 가능해야 한다.
- 콘솔에만 존재하는 결과를 만들지 않는다.
- 기존 코드 수정본은 출처 commit 또는 파일 해시를 기록한다.
- dataset별 평균만 저장하지 않고 repeat-level 결과와 probe ids를 저장한다.

## 아직 구현하지 않는 것

- active learning
- PPI
- 새 retriever 학습
- 응용 분야별 annotation pipeline

(sequential stopping은 2026-08-25 `40_planner_replay.py`로 구현 완료 —
frozen v0.3 스펙, LOO cross-fitting.)
