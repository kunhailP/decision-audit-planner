# Planner replay — RUN NOTES (2026-08-25)

## 설정

- Runner: `04_code/40_planner_replay.py` (FREEZE_PROPOSAL_v0.3 스펙:
  looks {10,30,50,70,90}∩[≤n/2], α=0.1, Bonferroni-corrected paired bootstrap,
  act/collect-more/abstain, 50 repeats × 13 collections)
- 진짜 손실은 **최종 audit 집합의 여집합**(한 번도 감사되지 않은 query)에서 평가.
- Selection 인증서는 **LOO cross-fitting** (METHOD_SPEC v0.2 요구사항).

## 결과 요약

- 전체 wrong-certificate율 0.035 (recal 0.017, selection 0.052) — 명목 α=0.1 이하.
- collection×decision 셀 중 α 초과는 scifact selection 0.14 하나
  (50회 반복 MC SE≈0.05 — 명목과 통계적으로 구분 안 됨), climate-fever 0.10 경계.
- 적응성: trec-covid selection은 T=10에서 act 100%/wrong 0 (gap 큼);
  quora recal은 act 0.06 (ratio 산포 큼 → 정직한 abstain); C1 곡선과 셀 단위 일치.

## In-sample ablation (보존: `../planner_replay_insample_ablation/`)

1차 구현은 probe에서 추정한 (ĉ, τ̂)를 같은 probe로 평가 → selection 인증서가
anticonservative: scifact wrong-cert 0.36, scidocs 0.16, hotpotqa 0.14.
LOO cross-fitting 도입 후: selection wrong-cert 0.098→0.052, act율 0.57→0.71,
평균 T 54.4→47.1. **편향 제거가 안전성과 효율을 동시에 개선** — 논문 §4의
핵심 방법론적 관찰. METHOD_SPEC이 요구한 cross-fitting의 필요성이 실증됨.

## 해석 경계

- 13개 collection은 development 노출분 — retrospective 증거 (D-007).
- 인증서는 empirically calibrated (bootstrap 타당성 가정), finite-sample 증명 아님.
