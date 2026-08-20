# Related-work map

목표는 참고문헌의 수가 아니라 **가장 가까운 연구가 이미 해결한 입력–결정–보증–비용**을 분리하는 것이다. 정확한 서지정보와 인용문은 원문 검증 후 bibliography에만 추가한다.

## Required neighborhoods

| Neighborhood | Prior work asks | Their decision | Cost unit | What must remain ours |
|---|---|---|---|---|
| IR topic-set/sample-size design | 몇 개 topic이면 비교·검정이 안정적인가 | estimation/testing | topics | 하나의 generic k가 아니라 downstream decision별 sequential certificate |
| Low-cost IR evaluation | 적은 relevance judgment로 metric/system ranking을 추정할 수 있는가 | estimation/ranking | query–doc judgments | post-shift calibration과 policy selection을 같은 planner interface로 다룸 |
| Active sampling for IR | 어떤 documents/topics를 먼저 판단할 것인가 | efficient estimation | judgments | core는 sampling innovation보다 decision-specific stopping에 둠 |
| Limited-label model selection | 적은 target label로 near-best model을 고를 수 있는가 | selection | labeled examples | recalibration과 selection certificate의 차이 및 retrieval audit 비용 |
| Calibration under shift | target label로 calibration을 복구하는가 | parameter/performance calibration | labels | downstream retrieval-set utility와 stopping cost |
| Sequential best-arm/selection | 언제 충분한 증거로 후보를 선택할 수 있는가 | selection/stopping | samples | correlated per-query policy outcomes와 audit/judgment structure |
| Risk control/selective prediction | 실패 위험이 크면 유보할 수 있는가 | act/abstain | calibration samples | abstention을 retrieval audit planning에 결합하되 신규성 과장 금지 |
| Incomplete qrels / judgment holes | missing judgments가 평가를 얼마나 왜곡하는가 | evaluation validity | pooled judgments | planner의 certificate가 judgment process에 반응하는 실패조건 |

## Five-field extraction template

각 논문은 아래 항목으로 한 행만 만든다.

1. exact problem and estimand
2. decision made with the labels
3. true annotation/sample unit
4. guarantee or empirical success criterion
5. overlap and remaining gap

## Novelty tests

문헌 조사 뒤 다음 질문에 `yes`로 답하지 못하면 C2를 수정한다.

- 기존 topic-size planning에 loss만 바꿔 끼운 것 이상인가?
- 기존 limited-label selection method와 비교했을 때 calibration arm이 실질적 통찰을 주는가?
- sequential stopping/abstention이 단순 신뢰구간 종료규칙 이상으로 retrieval-specific 문제를 해결하는가?
- two-axis cost `T`와 `B`를 실제로 측정하거나, 측정 불가능성을 정직하게 제한했는가?
- incomplete qrels 아래 certificate가 실패하는 방식을 새롭게 진단하는가?

## Verification status

- Sakai topic-set/power line: exact papers to verify
- Guiver–Mizzaro–Robertson small-topic prediction line: exact paper to verify
- Li–Kanoulas active sampling line: exact paper to verify
- Oosterhuis et al. reliable IR confidence intervals line: exact paper to verify
- Okanovic et al. limited-label model selection line: exact paper to verify
- Adaptive-k and dynamic cutoff line: verified candidate, direct method overlap audit required

검증되지 않은 제목·연도·결론은 논문 원고에 쓰지 않는다.
