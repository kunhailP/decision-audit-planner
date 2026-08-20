# DXW presentation outline v0.2

발표는 논문보다 앞서갈 수 없다. 발표 시점의 claim level을 첫 장 하단에 `C0/C1/C2...`로 표시한다.

## Ten-slide structure

1. **Deployment problem:** 새 환경에서 얼마나 검증해야 하는가?
2. **Hidden ambiguity:** 같은 labels라도 calibration과 selection은 다른 결정을 만든다.
3. **Audit of our prior study:** 10 labels가 아니라 10 audited queries였다.
4. **Pilot anomaly:** calibration은 복원됐지만 3-way selection은 실패했다.
5. **Why curves are insufficient:** full target을 봐야 필요한 k를 아는 방법은 배치에 쓸 수 없다.
6. **Method:** Decision-Specific Audit Planner의 input/output.
7. **Evidence contract:** fixed-budget, risk–cost, mechanism, prospective validation.
8. **Available result:** 발표일까지 실제로 통과한 claim만 제시.
9. **Failure conditions:** qrels holes, policy gap, menu size, missing candidate artifact.
10. **Conclusion:** 결정·tolerance·risk를 말하지 않은 label budget은 의미가 불완전하다.

## Conference honesty rule

- planner 구현 전에는 “we propose and validate”가 아니라 “we formulate and are testing”이라고 말한다.
- prospective evaluation 전에는 “generalizes”라고 말하지 않는다.
- 누락된 candidate artifact와 재생성 자원 제약을 숨기지 않는다.
- 정치학·로비·법학을 억지 동기로 넣지 않는다.
