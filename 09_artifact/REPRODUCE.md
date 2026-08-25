# Reproduction bundle (G5 clean-room contract) — 2026-08-25

빈 환경에서 이 저장소 + Kaggle 백업만으로 모든 headline을 재생성한다.

## 입력

1. 이 hub 저장소 (git bundle 또는 GitHub clone)
2. Kaggle `kunhail/shift-study-artifacts` **v3**:
   - `runs-block1closed-20260703/runs/candidates/` → `shift-study/runs/candidates/` (13개 개발 collection)
   - `prospective/cqadupstack-android{,_meta}.csv` → 같은 폴더 (P4 target; 재빌드 생략 시)
3. Python 3.11, `pip install scikit-learn==1.9.0 numpy==2.1.2 scipy pandas pyarrow matplotlib`
   (P4 candidate 재빌드까지 하려면 + `torch(cpu) sentence-transformers beir bm25s`)

## Tier 1 — row-level에서 요약·그림 재생성 (~1분)

```bash
python3 04_code/30_summarize.py          # C1 요약 + F1
python3 04_code/tests/run_tests.py       # 21개 검증 (재생성 일치 포함)
```

## Tier 2 — 전체 재계산 (~1–2시간, CPU)

```bash
python3 04_code/20_budget_curves.py --source <shift-study>            # C1
python3 04_code/20_budget_curves.py --source <shift-study> --utility recall
python3 04_code/20_budget_curves.py --source <shift-study> --utility ndcg
python3 04_code/30_summarize.py
python3 04_code/50_simulation.py                                       # C2/C3
python3 04_code/40_planner_replay.py                                   # C2 replay
python3 04_code/70_prospective_run.py                                  # P4 (주의: primary 규약)
python3 04_code/tests/run_tests.py
```

모든 seed가 결정적이므로 Tier 2 산출물은 저장본과 일치해야 한다. 불일치 시
diff를 보고하고 quarantine (POD_HANDOFF Amendment v2, Pod-A).

## Tier 3 — P4 candidate까지 원천 재빌드 (~1시간 추가)

```bash
# BEIR cqadupstack.zip (sha256 6072f7d3...) → data/cqadupstack-android
python3 04_code/60_prospective_build.py cqadupstack-android
```

임베딩 부동소수 연산 순서 차이로 CSV가 미세하게 다를 수 있다(환경 기록 필수);
이 경우 Tier 2 결과의 방향적 일치(사전등록 기준 판정 동일)를 보고한다.
