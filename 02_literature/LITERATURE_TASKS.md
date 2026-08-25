# 선행연구 조사 범위

목적은 논문 수를 늘리는 것이 아니라, 아래 세 주장에 최근접한 연구가 이미 있는지를 확인하는 것이다.

## Track A — validation under domain shift

- information retrieval과 domain adaptation에서 target-domain validation을 어떻게 요구하는가
- domain shift를 accuracy drop이 아니라 validation cost로 정의한 연구가 있는가
- retrieval evaluation에서 인간 검증의 단위를 query와 pair judgment 중 무엇으로 보고하는가

## Track B — limited-label recalibration and model selection

- 소량 target label을 이용한 scalar recalibration
- 소량 label을 이용한 model/policy selection
- 동일 표본이 estimation과 selection에서 다른 요구량을 가진다는 연구

## Track C — audit-budget design

- IR evaluation에서 query와 query-document pair 판단 비용의 구분
- incomplete qrels 아래 evaluation bias
- deep 대 shallow judging은 core가 성립한 뒤 확장 필요성을 판단할 때만 조사

## 문헌별 기록 항목

각 문헌은 다음 다섯 가지만 기록한다.

1. 정확한 연구질문
2. label 또는 judgment의 실제 단위
3. 내리는 결정: estimation, calibration, selection 중 무엇인지
4. distribution shift가 설계에 실제로 들어가는 방식
5. 우리 주장과 겹치는 부분 및 남는 차이

기존 `../../_legacy/DXW_2026_paper/02_선행연구`의 문헌은 자동으로 승계하지 않는다. 새 논문의 질문을 직접 지지하는 문헌만 검증 후 가져온다.
