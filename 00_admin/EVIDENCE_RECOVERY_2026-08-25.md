# Evidence Recovery Record — 2026-08-25

## 요약

G1의 핵심 의존성이던 candidate-level artifact(E02)를 **Kaggle 백업에서 복구**했고,
복구본으로 Block 1 확증 파이프라인을 재실행하여 **커밋된 headline 산출물과
byte-identical 재현**을 확인했다. G1 exit condition(“candidate artifacts have
provenance, checksums, and a validated schema”)은 충족되었다. 실행 주체는
Pod가 아니라 로컬 CPU 환경이었다(candidate 재생성이 아닌 백업 복원이므로 GPU 불필요).

## 복구 경위

1. `runs/candidates/`는 shift-study `.gitignore`에 있어 **git 히스토리에 커밋된
   적이 없음**을 확인했다 (`git log --all` 전수 경로 조회). “복구 또는 재생성”의
   실제 선택지는 (a) Kaggle 백업, (b) `build_candidates.py` 재생성(CUDA,
   25–40 GPU시간, 원자료 ~130 GB) 두 가지였다.
2. Kaggle dataset `kunhail/shift-study-artifacts` (v2, 2026-07-03, post-handoff)
   전체(719 MB)를 다운로드했다. 내용: 13개 dataset의
   `runs/candidates/{name}.csv` + `{name}_meta.csv` 전부(26개 파일), Block 1
   종료 시점 runs 스냅샷, git bundle 2종, docids 맵.

## Provenance 검증 (결과를 읽기 전에 수행)

- **git bundle head 일치**: `shift-study-20260703-final.bundle`의 HEAD =
  `ef825e1d35d58d178c50054122ccc9e9ab54012c` — PROJECT.yaml의 고정 커밋과 동일.
- **백업–저장소 교집합 byte-identical**: `block1_confirm/{agg.json,
  per_query.csv, config.json}`, `h1_mechanism/{agg.json, per_query.csv}`,
  `pilot/all_cand.csv`(백업의 `runs/all_cand.csv`) 6종 모두 `cmp` 통과.
- **schema 검증**: candidates CSV는 CONTRACTS 예상 구조와 일치 —
  per-candidate `qid,docid,score_norm,rank,consensus,lexoverlap,in_bm25top10,judged,grade,relevant`,
  meta `qid,nG,n_judged`.
- 복구본 체크섬: `/root/shift-study/runs/candidates/SHA256SUMS.restored`,
  기록: 동일 폴더 `RESTORE_MANIFEST.json`.

## P1 — Legacy reproduction (byte-identical)

- 환경: Linux CPU, Python 3.11.10, scikit-learn 1.9.0, numpy 2.1.2,
  **scipy 1.17.1** (requirements의 1.18.0이 Python 3.11에 미제공 — 편차로 기록;
  결과에 영향 없음이 아래 재현으로 입증됨).
- 실행: `make confirm` 경로 그대로 `h1_mechanism.py` + `block1_confirm.py`.
- 판정: 재실행 후 `git status runs/` 무변화 — **모든 산출물이 커밋본과
  byte-identical**. H1(부호 일치 100%, Spearman 0.995), SUFFICIENCY 13/13,
  untouched-4 SAFETY 0/4, VALUE CI [−0.0369, −0.0131] 전부 재현.

## 상태 변경

- E02: ❌ Missing → ✅ Recovered (Kaggle 백업, provenance 검증 완료)
- M1 (Correct): Block 1 범위에서 충족
- M2 (Reproducible): Block 1 범위에서 충족 (제3자 재현은 artifact bundle 공개 후)
- G1: exit condition 충족 → G2(method validity) 진행 가능
- 후속: `04_code/20_budget_curves.py`가 k-grid retrospective study(P2, C1 증거)를
  repeat-level 저장으로 실행한다. k=10은 legacy seed 공식을 재사용해 Block 1과
  직접 교차검증 가능하다. 임계값(ε_cal=0.005, ε_sel=0.01)은 Block 1 사전등록
  값을 잠정 상속하며 v0.2 freeze 전까지 provisional로 표기한다.
