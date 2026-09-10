# STATUS — branch `2027-nonneutral-judge` (2026-09-10)

이 브랜치는 v0.3 초안(main) 위에서 하루 동안 진행한 방법 재설계·검증 작업의 기록이다. main은 v0.3 기록으로 보존하고,
병합은 저자 검토 후에 한다. 모든 수치는 `05_results/`의 row-level 파일에서 재생성된다.

## 읽는 순서
1. `01_design/PAPER_2027_DESIGN_v0.1.md` — §1–8 설계, §9–20 단계별 실행 기록(사전 등록 평가·정정·탐색 종료 포함)
2. `06_paper/THEORY_v0.1.md` — 명제 A·B′·C(정정판), active inference와의 관계
3. `03_data/PROSPECTIVE_LOCK_v0.4_2026-09-10.md` — TREC DL 2021–23 primary run 사전 등록 (결과: 유효성 통과, 효율 미달)
4. `06_paper/TABLES_v0.1.md`, `06_paper/DRAFT_v0.4_metrics_section.md` — 통일 지표 J50과 정의
5. `01_design/EXPLORATION_menu_allocation.md` — 범위 제한 탐색(종료, 부정 결과)

## 확정된 논문 주장
정책을 인증하는 데 필요한 추정 대상을 정확히 정의하면 기존 표집·예측 보정 방법을 효율적으로 적용할 수 있다. 판정자의 전체
정확도만으로는 그 효율을 예측할 수 없고, 잘못된 불확실성 가정은 표집 효율을 떨어뜨린다. 인증의 유효성은 판정자와 무관하다.

## 코드 지도 (04_code)
- `lib/certificates.py` 인증서(breakpoint 보정, 동시 t/PPI, cross-fit λ, 정확 median 구간), `lib/neutrality.py` ρ 하한(BCa)
- `61`–`64`, `69`, `75` pool 빌더(legacy/modern BEIR, TREC DL v1/v2 완전 판정 pool), `66` LLM 판정(Qwen3-8B, Mistral-7B, 공통), `73` MPNet 대조 판정
- `63` 순차 planner v2(방법 변형·판정자·메뉴4·look 격자), `67` PPI 이득, `70` 중립성 진단, `72` 자기선호, `76` primary 보고, `77`–`78` ρ 조건 지도(F6)
- `80`–`83` 문서 단위 감사(결정 가중 HT/CV, 표집 비교군, 충실한 active inference, 메뉴 배분), `84`–`85` 통일 지표 J50(F7)
- 재현 규율: 방법별 독립 rng, 배치 LLM 추론 시 position_ids 명시, 결과 파일명에 판정자·설정 포함

## 남은 작업 (경로 1)
set-F1 확장 부록(nG의 PPI 보정), 관련연구 절, 미사용 completely-judged collection에서 LOCK v0.5 확증 평가, 원고 조립.
