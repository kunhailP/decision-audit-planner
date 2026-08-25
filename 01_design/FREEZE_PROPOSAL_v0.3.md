# Method Freeze Proposal v0.3 — 2026-08-25

상태: **비준됨 (2026-08-25, 사용자 위임에 의한 비준 — D-019,
PROSPECTIVE_LOCK_2026-08-25.md §0). 이후 변경 금지.** 이 문서는 development 데이터의 planner replay를
실행하기 **전에** 작성되었다. simulation은 interval method 선택에 사용할 수 있다
(`research_v0.2.yaml`: `interval_method: to_be_selected_after_simulation_not_target_results`).
Prospective(P4) 결과는 어떤 항목의 변경 근거도 될 수 없다.

## 1. 고정 제안값

| 항목 | 값 | 근거 |
|---|---|---|
| ε_cal (recalibration tolerance) | 0.005 (set-F1 utility 척도) | Block 1 사전등록 SUFFICIENCY 임계값 상속. 임의 신규값 도입 회피 |
| ε_sel (selection ε-regret) | 0.01 (set-F1 utility 척도) | Block 1 사전등록 SAFETY 임계값 상속 |
| α (wrong-certificate risk) | 0.10 | 감사 예산 연구의 관례적 수준; 시뮬레이션에서 명목 통제 검증 |
| k₀ (initial audit) | 10 | legacy probe 크기와 연속성; C1에서 보정은 이 수준에서 대체로 충분 |
| batch b | 20 | C1 곡선에서 선택 성공률이 유의미하게 움직이는 최소 단위 |
| k_max | min(100, ⌊n/2⌋) | grid 상한; 평가군 확보를 위한 n/2 규칙 유지 |
| looks | T ∈ {10, 30, 50, 70, 90} (cap 도달 시 조기 종료) | 최대 5회 |
| policy menu | {ad_probe, glob_probe, trunc} | D-계열 결정: 결과를 보기 전 고정 (legacy 그대로) |
| primary metric | set-F1 | 기존 고정; recall·nDCG는 sensitivity로 병행 |

## 2. Interval method 제안

**Bonferroni-corrected paired bootstrap** (per-look α' = α / (looks × comparisons)).

- **Selection certificate**: 후보 m̂ = argmax LCB. 각 경쟁 정책 j≠m̂에 대해
  probe query-level paired difference (u_j − u_m̂)의 bootstrap UCB_{α'}를 계산.
  `U_sel = max_j UCB(μ_j − μ_m̂)`. **ACT iff U_sel ≤ ε_sel.**
  comparisons = |menu| − 1, looks = 5 → α' = α/10.
- **Recalibration certificate**: probe bootstrap으로 ĉ의 (α'/2, 1−α'/2) 신뢰구간
  [c_lo, c_hi]를 얻고 (α' = α/looks — **look 보정 필수**; 보정 없는 버전은
  simulation에서 s=1.0 cell의 wrong-cert 0.115 > α로 관측되어 기각, 2026-08-25),
  probe query들에서 gate(c)의 utility가 이 구간 위에서
  움직이는 폭 `U_cal = max_{c∈{c_lo,c_hi}} |u_probe(c) − u_probe(ĉ)|`을 계산.
  **ACT iff U_cal ≤ ε_cal.** (parameter interval이 아니라 downstream utility
  stability 기준 — METHOD_SPEC v0.2 원칙)
- 선택 이유: (a) union bound라 optional stopping 하에서도 보수적으로 타당,
  (b) 구현이 단순해 감사 가능, (c) confidence-sequence류(EB-CS)는 표본
  50–100에서 과도하게 넓어 abstain을 남발함 — simulation에서 비교 후 확정.
- **주장 한계**: 논문에서는 "empirically calibrated certificate"로 부른다.
  finite-sample guarantee는 bootstrap 타당성 가정 하의 근사임을 명시 (METHOD_SPEC 경계 준수).

## 3. Planner 출력

`ACT(decision, certificate)` / `MORE(next batch)` / `ABSTAIN(k_max 도달, 미해결 비교 기록)`.
Abstain은 실패가 아니라 정직한 출력이다 (README 원칙).

## 4. 비용 회계

일차 축 T = audited queries. B는 `pair_pool_budget`(probe pool 크기 합)으로
기록하되 pooled qrels 하의 프록시로만 보고한다 (D-005). 인건비 환산 주장 금지.

## 5. 변경 통제

이 값들은 development replay 결과를 본 뒤 바꿀 수 없다. 바꿔야 한다면
`DEVIATIONS` 기록 + 이유 + 영향 분석을 남기고, prospective 전에만 허용된다.
