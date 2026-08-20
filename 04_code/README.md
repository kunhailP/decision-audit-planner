# Code plan

상위 통제문서는 `CONTRACTS.md`, 잠정 설정은 `configs/research_v0.2.yaml`이다. 기존 파일명 계획은 구현 순서를 설명하지만, 실제 산출물은 contract의 row-level schema를 따라야 한다.

기존 코드를 그대로 복사하기 전에 새 설계의 추정량과 대응하는지 확인한다.

## 예정된 최소 파이프라인

```text
00_inventory.py          기존 artifact와 필드 점검
05_recover_candidates.py 누락된 candidate artifact 검증 또는 재생성
10_reproduce_k10.py      기존 k=10 결과의 용어 수정 재현
20_budget_curves.py      k={5,10,20,50,100} 반복표집
30_summarize.py          success rate, regret, B* 계산
40_figures.py            논문과 발표용 그림 3개 생성
```

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
- sequential stopping
- 새 retriever 학습
- 응용 분야별 annotation pipeline
