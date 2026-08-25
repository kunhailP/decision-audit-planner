# Budget-curve retrospective study — RUN NOTES (2026-08-25)

## 실행 요약

- Runner: `04_code/20_budget_curves.py` (LODO·정책·선택규칙은 shift-study
  `block1_confirm.py`(commit ef825e1d)과 동일한 수학; k만 grid화, row-level 저장)
- 입력: 2026-08-25 Kaggle 백업에서 복구한 `runs/candidates/` 13개
  (`00_admin/EVIDENCE_RECOVERY_2026-08-25.md`)
- Grid: k ∈ {5,10,20,50,100} (core {5,10,20}), repeats=50,
  n_probe = min(k, n_queries/2) — clipped 여부 row에 기록
- Seed: k=10은 legacy 공식 재사용(Block 1 draw와 동일), 그 외 k는 분리된
  crc32 기반 범위. Python hash() 미사용.
- 임계값(**provisional**, Block 1 사전등록 상속, v0.2 freeze 전):
  recalibration 성공 = per-repeat |mean_ev(ad_probe) − mean_ev(ad_c)| ≤ 0.005,
  selection 성공 = per-repeat regret(select3) ≤ 0.01
- 산출물: `per_repeat.parquet`(probe qids 포함), `decision_trace.parquet`,
  `summary_by_collection_k.csv`, `budget_gap_by_collection.csv`,
  `c1_summary.json`, `F1_budget_curves.png` — 모든 요약은 row-level에서 재생성.

## C1 진단 (13개 development collection, retrospective — D-007에 따라 확증 아님)

손실 크기 기준으로 비대칭이 뚜렷하다: k=5에서 이미 평균 calibration loss는
10/13 collection에서 ~0.006 이하지만, 평균 selection regret은 0.02–0.06대다.
k=10 기준 성공률 ≥0.9 도달: recalibration 5/13, selection 3/13;
k=100에서 selection 10/13.

**단, per-repeat 성공률 곡선은 균질하지 않다 — 이 이질성이 C3의 직접 입력이다:**

- **선택이 자명한 경우**: trec-covid는 정책 간 격차가 커서(ad_probe ≫ 나머지)
  k=5에서도 regret=0. → 선택 난이도의 원인은 "결정 종류" 자체가 아니라
  **정책 격차(gap)**임을 시사 (M4 대응).
- **선택이 끝까지 어려운 경우**: scifact·fiqa·climate-fever는 k=100에서도
  성공률 <0.9 — 정책들이 근접해 있어 probe가 순위를 분해하지 못함.
- **보정이 어려운 예외**: quora(cal 성공률 k=100에서도 <0.9)와 dbpedia(50 필요).
  quora는 c_star 자체의 산포가 커서 scalar 보정의 한계 사례 — failure taxonomy
  (F5) 후보.
- untouched-4(red)는 selection에서 일관되게 느리게 수렴 (nq·hotpotqa k*≈100,
  fever 50, climate-fever 미도달).

## 해석의 경계 (금지 주장 준수)

- 13개 모두 개발에 노출된 collection이므로 이것은 **retrospective diagnostic**
  이다. C1의 확증은 prospective locked collection(P4/G4) 이후에만 주장한다.
- pair-level 비용은 `pair_pool_budget`(probe pool 크기 합)으로만 기록했으며
  이는 pooled qrels 하의 프록시다. 인건비 환산 주장 금지 (D-005/M3).
- 임계값 ε는 freeze 전이므로, 논문 수치는 freeze된 ε로 재생성해야 한다
  (row-level 보존으로 재계산 비용 0).
