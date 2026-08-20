# Flagship paper outline v0.2

잠정 제목:

> **Audits for What? Decision-Specific Validation after Distribution Shift**

제목에 `retrieval`을 넣을지는 C4의 일반화 범위를 본 뒤 결정한다.

## 1. Introduction

- 배치 후 target labels는 하나의 generic validation set으로 취급된다.
- 그러나 estimation/recalibration과 policy selection은 서로 다른 loss와 evidence requirement를 가진다.
- 기존 파일럿에서 작은 audited-query set은 scalar recalibration을 복원했지만 policy selection에는 실패했다.
- 이 결과는 결론이 아니라 decision-specific audit planner의 출발점이다.

Contributions는 C2–C4 통과 여부에 따라 최대 세 개만 쓴다.

1. decision-specific audit planning formulation
2. sequential act/more/abstain procedure와 risk–cost evaluation
3. controlled mechanism study와 prospective retrieval validation

## 2. Related work

- target validation and calibration under shift
- sample/topic-size planning in IR
- low-cost and active IR evaluation
- limited-label model selection
- sequential risk control and selective decisions

각 절은 `02_literature/RELATED_WORK_MATRIX.md`의 input–decision–cost–guarantee 차이로 끝낸다.

## 3. Problem formulation

- target query distribution와 policy utility
- audited query `T`와 pair judgment `B`
- recalibration loss와 selection ε-regret
- risk, tolerance, wrong-confidence
- full-target scalar reference의 제한

## 4. Decision-Specific Audit Planner

- algorithm interface
- cross-fitting/sample-splitting
- recalibration stability certificate
- simultaneous policy-comparison certificate
- sequential stopping과 abstention
- guarantee 또는 empirical calibration의 정확한 경계

## 5. Experimental design

- controlled simulation
- legacy BEIR retrospective development
- baselines와 ablations
- locked prospective collection
- metrics, endpoints, statistical protocol

## 6. Results

### 6.1 Retrospective diagnosis

기존 `k=10` 해석 교정과 fixed-budget curves.

### 6.2 Risk–cost performance

planner가 fixed budget 대비 wrong-confidence와 audit cost를 어떻게 바꾸는가.

### 6.3 Mechanisms

menu size, policy gap, variance, shift, judgment coverage의 영향.

### 6.4 Prospective validation

사전 고정한 endpoint를 그대로 보고하며 실패 시에도 섹션을 유지한다.

## 7. Limitations and failure boundaries

- complete judgment assumption과 qrels holes
- retrieval-specific scalar calibration
- prospective collection 수
- pair cost의 실제 인건비 대응 한계
- sequential interval assumptions

## 8. Conclusion

핵심 메시지는 “selection은 더 어렵다”가 아니다.

> target validation budget은 label 수만으로 충분성을 말할 수 없으며, 그 자료로 내릴 결정·허용손실·위험수준과 함께 계획되어야 한다.
