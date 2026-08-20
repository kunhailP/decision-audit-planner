# 기존 shift-study 증거 감사

날짜: 2026-08-20  
대상 commit: `ef825e1d35d58d178c50054122ccc9e9ab54012c`

## 결론

기존 코드는 k=10 파일럿의 논리를 확인하는 데는 유용하지만, 현재 저장된 artifact만으로 새 논문의 k별 budget curve를 계산할 수 없다. 새 runner 작성 전에 candidate-level 입력을 복구하거나 재생성해야 한다.

## 확인한 사실

### 1. 저장 파일의 이름과 실제 단위가 다르다

`runs/block1_confirm/per_query.csv`는 13행이며 각 행이 dataset 하나다. 실제 열도 dataset별 평균 policy 성능, regret, `c_star`로 구성된다. query identifier와 repeat identifier가 없다.

따라서 이 파일로는 다음을 복원할 수 없다.

- 다른 k에서의 probe 반복표집
- repeat별 선택 policy
- query-level paired comparison
- Monte Carlo success rate

### 2. 필요한 candidate artifact가 없다

`src/block1_confirm.py`는 `runs/candidates/{dataset}.csv`와 `{dataset}_meta.csv`를 읽는다. 그러나 `runs/candidates/`는 `.gitignore`에 포함되어 있고 현재 작업본과 Documents/Downloads 검색에서도 발견되지 않았다.

### 3. 현재 runner는 budget curve용이 아니다

- `K_PROBE=10`
- `REPEATS=20`
- dataset별 repeat 결과를 저장하지 않고 평균만 저장

새 분석에는 k와 반복 수를 설정값으로 분리하고, 모든 repeat-level 결과를 저장하는 runner가 필요하다.

### 4. probe와 evaluation은 분리되어 있다

각 반복에서 probe index를 먼저 추출하고 나머지를 evaluation set으로 사용한다. 이 부분은 새 코드에서도 유지한다.

### 5. LODO의 의미

각 target fold에서 해당 dataset은 classifier calibration, transferred threshold, truncation model 학습에서 제외된다. 다만 13개 dataset은 서로의 training fold에 반복적으로 사용되므로 과거의 `untouched-4`를 새 논문의 독립 collective holdout으로 표현할 수는 없다.

### 6. `ad_c`의 정확한 의미

`c_star`는 target dataset의 모든 eligible query에 대해 `median(nG / sum(p))`로 계산된다. `ad_c`는 이 full-target scalar를 사용하는 adaptive gate다.

따라서 `ad_c`는 다음과 같이 부른다.

> full-target scalar reference

이는 relevance를 완벽하게 아는 oracle ranking이나 oracle retrieval policy가 아니다.

### 7. 공통 budget grid의 한계

저장된 다른 query-level artifact를 기준으로 가장 작은 dataset은 약 49~50 query다. probe를 evaluation에서 제외하면서 모든 dataset에 공통 적용하려면 core grid는 `{5,10,20}`이 적절하다. k=50 이상은 큰 dataset만 대상으로 별도 표시해야 한다.

### 8. annotation cost는 아직 식별되지 않는다

기존 k는 audited query 수다. 한 query를 audit하는 데 몇 개의 query-document pair 판단이 필요한지는 저장된 aggregate에서 알 수 없다. 더구나 BEIR qrels는 dataset별 judgment coverage가 다르다.

따라서 현 단계에서 가능한 주장은 다음으로 제한한다.

> decision-specific audited-query budget

pair-level human judgment budget은 candidate pool과 judgment protocol을 복원한 뒤에만 주장한다.

## G2 선택지

1. 원래 실행 환경이나 백업에서 `runs/candidates/`를 복구한다.
2. `build_candidates.py`로 artifact를 재생성하되 데이터·시간·저장공간 비용을 먼저 산정한다.
3. 복구가 과도하게 비싸면 보존된 query-level 자료로 답할 수 있는 더 작은 파일럿으로 논문 범위를 재조정한다.

현 단계의 권장 순서는 1 → 2 → 3이다.

## 재생성 자원 감사

2026-08-20 현재 로컬 저장공간은 약 27 GiB 남아 있다. 기존 저장소의 Makefile은 13개 BEIR raw dataset 다운로드에 약 130 GB가 필요하다고 명시한다. `build_candidates.py`는 세 dense encoder의 corpus embedding과 query retrieval에 CUDA를 직접 요구하며, 기존 requirements는 RTX PRO 6000 Blackwell/CUDA 12.8 환경에서 검증되었다고 기록한다.

따라서 현재 Mac 로컬에서 full regeneration을 시작하면 저장공간 부족으로 실패할 가능성이 확실하며, CPU fallback도 구현되어 있지 않다. 이 상태에서 다운로드나 재생성을 실행하지 않는다.

안전한 다음 순서는 다음과 같다.

1. 원 실행환경, 외장 저장장치, cloud volume에서 `runs/candidates/`와 `data/emb/` 백업을 우선 복구한다.
2. 백업이 없으면 GPU와 150 GB 이상의 여유공간을 가진 별도 환경에서 immutable manifest와 함께 재생성한다.
3. 그 자원도 없으면 deeply judged smaller collection 하나로 end-to-end fixture를 먼저 만들고, 기존 13개 전체 재생성은 flagship compute plan으로 분리한다.

현재 blocker는 코드 작성이 아니라 **130 GB급 data/embedding과 CUDA 실행환경의 부재**다.
