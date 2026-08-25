# 저장소·백업 지도 (2026-08-25)

무엇이 어디에 살고, 무엇이 원본(source of truth)이며, 소실 시 어떻게 복원하는가.

## 원칙

- **코드·문서·row-level 결과의 원본 = 이 허브 git.** GitHub은 미러, Kaggle은 재해복구.
- **shift-study는 ef825e1에서 영구 동결** (append-only; 논문이 이 커밋을 인용).
  새 작업은 전부 허브에서만.
- 무거운 재생성물(원 corpus, 임베딩)은 git에 넣지 않고 Kaggle + 재생성 명령으로.

## 자산별 위치

| 자산 | 원본 | 미러/백업 | 소실 시 복원 |
|---|---|---|---|
| 허브 (코드·문서·초안·05_results) | 로컬 git `DXW_2026_shift_audit` | GitHub `decision-audit-planner`(private, 토큰 대기) + Kaggle v3 bundle | bundle에서 `git clone` |
| shift-study 코드+커밋된 runs | GitHub `kunhailP/shift-study` (ef825e1) | Kaggle v2/v3 git bundle | clone 또는 bundle |
| 13개 dev candidates (E02) | `/root/shift-study/runs/candidates/` | Kaggle v2 (`runs-block1closed-*`), 체크섬: `SHA256SUMS.restored` | Kaggle에서 재다운로드 |
| android candidates+임베딩 (P4) | 같은 폴더 + `data/emb/` | Kaggle v3 `prospective/` | Kaggle 또는 Tier-3 재빌드(~1.5h) |
| P4 primary 결과 | 허브 `05_results/prospective_android/` | 허브 git + Kaggle v3 | **재실행 금지** (primary 규약) — 백업본만이 원본 |
| BEIR 원 corpus (cqadupstack) | 다운로드 캐시 (일회성) | 공개 BEIR 서버, zip sha256 `6072f7d3...` | 재다운로드 |
| legal-ir-pilot | GitHub `kunhailP/legal-ir-pilot` (동결) | Kaggle v2 `legal-ir-shift-full.bundle` (전체 미러) | clone/bundle |
| 레거시 정치학 프로젝트 | `2026_DXW_conference/_legacy/` (zip 원본) | 로컬 zip `2026_DXW_conference.zip` | zip 재해제 |

## 로컬에 남기는 것 / 지워도 되는 것

- **남김**: 허브 전체, `/root/shift-study` (candidates 포함), `data/emb/*.npy`
  (P4 재검증용), `2026_DXW_conference.zip` (레거시 원본)
- **지워도 됨** (Kaggle 업로드 확인 후): scratchpad의 `kaggle_backup/`,
  `cqadupstack.zip`, BEIR 압축 해제 잔여물
- **절대 로컬만 두지 않을 것**: `05_results/prospective_android/` (primary run
  산출물 — 재실행 불가라 유일본; 커밋+Kaggle 즉시)

## 남은 액션

1. [x] 허브 git 커밋 (단독 저자 히스토리: `3cb1d57`, `5edf8c8`)
2. [x] Kaggle v3.1 업로드 완료 (bundle 복원 시험 통과)
3. [x] GitHub `kunhailP/decision-audit-planner` (private) 생성·push 완료 (2026-08-25)
4. [ ] Pod-A(G5 clean-room)에 Kaggle v3.1 사본 전달
