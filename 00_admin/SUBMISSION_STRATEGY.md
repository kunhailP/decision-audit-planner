# Result-contingent submission strategy

이 문서는 저널 이름을 먼저 정하고 논문을 거기에 맞추는 계획이 아니다. 연구결과가 어느 수준의 주장을 감당하는지에 따라 **한 개의 archival route**를 선택하기 위한 기준이다.

## North-star bar

논문은 다음 질문을 견딜 수 있도록 만든다.

> 이 결과는 retrieval의 특정 pipeline을 재분석한 것인가, 아니면 ML 시스템이 분포 이동 후 인간 검증자료를 사용하는 방식을 바꾸는 일반적인 평가 방법인가?

후자를 설득할 수 있으면 ICML/NeurIPS/ICLR의 evaluation·human-in-the-loop·trustworthy ML 범위를 목표로 한다. retrieval 고유의 평가 기여가 중심이면 SIGIR full paper 또는 TOIS가 더 자연스럽다.

## Branch A — top ML conference

다음이 모두 성립할 때만 선택한다.

- decision-specific planner가 명확한 알고리즘으로 존재
- coverage 또는 ε-regret에 대한 이론적 정당화나 강한 calibration evidence
- 여러 policy family·metric·shift condition에서 일관된 가치
- 새로운 locked collection에서 prospective success
- 기존 sample-size, active evaluation, limited-label selection 대비 분명한 이득
- 8–9쪽 본문 안에서 하나의 강한 메시지로 압축 가능

이 경우의 주장은 “retrieval case study”가 아니라 **post-shift validation decision을 위한 일반적인 audit-planning principle**이다.

## Branch B — top IR route

방법의 가치가 retrieval evaluation과 qrels/judgment design에 강하게 묶여 있지만 증거가 깊을 때 선택한다.

- query와 pair-judgment cost를 실제로 측정
- incomplete judgments와 pool coverage를 직접 처리
- TREC 등 deeply judged collection에서 검증
- standard IR metric과 set-valued utility를 함께 분석
- strong IR baselines와 artifact audit를 완료

SIGIR은 간결한 flagship conference route, TOIS는 더 넓은 실험·분석을 담는 journal route로 본다.

## Branch C — TMLR

다음 경우에 강하고 정직한 선택이다.

- method와 실험은 기술적으로 완결됨
- decision-specific insight와 negative result가 유용함
- prospective validation과 재현성은 확보됨
- 다만 top conference가 요구할 broad significance, theory depth, cross-task breadth가 제한적임

TMLR의 공식 기준은 기술적 정확성과 관심 가능성을 중심으로 하지만, 기존 archival paper의 확장·중복 제출을 허용하지 않는다. 따라서 Branch A/B에서 **게재된 뒤** 같은 결과를 TMLR로 보내지 않는다. 상위 학회에서 거절된 뒤 내용과 주장에 맞춰 TMLR을 선택하는 것은 가능하지만, 동시 투고는 하지 않는다.

관련 정책:

- TMLR editorial policy: `https://jmlr.org/tmlr/editorial-policies.html`
- ICML 2026 call: `https://icml.cc/Conferences/2026/CallForPapers`

## Decision card

최종 결과가 나온 뒤 아래 항목을 한 페이지로 작성한다.

- 성립한 최고 claim level: C0–C4
- prospective endpoint 통과 여부
- 가장 강한 baseline 대비 효과와 비용
- method failure rate와 worst-case collection
- retrieval 밖에서의 타당성 증거
- theory/guarantee 수준
- artifact 재현 여부
- 추천 branch와 포기할 branch

venue는 이 카드가 작성되기 전에는 확정하지 않는다.
