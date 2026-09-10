# Draft v0.4 — assembly outline (2026-09-10)

Working title: **Where to spend human judgments when an AI judge helps certify a retrieval policy**
(대안: Certifying policy deployment with non-neutral AI judges: decision weights, control variates, and what accuracy does not tell you)

## Claim (one sentence)
정책을 인증하는 데 필요한 추정 대상을 정확히 정의하면 기존 표집·예측 보정 방법을 효율적으로 적용할 수 있다; 판정자의 전체 정확도만으로는
그 효율을 예측할 수 없고, 잘못된 불확실성 가정은 표집 효율을 떨어뜨린다; 인증의 유효성은 판정자와 무관하다.

## Sections → sources
1. Introduction — 문제(배포 인증, AI 판정자 시대), 세 주장, 주장하지 않는 것(DRAFT_v0.4_related_work §5)
2. Setup — 메뉴·utility·인증서·오류 정의 (DRAFT_v0.3 §2 갱신, THEORY 표기)
3. What determines the value of a judge — ρ 메커니즘 (F4, §9.7/§10.1/§11.1), 조건 지도 (F6, §15.1), 자기선호 (§12.2, §17.3)
4. Valid certificates for any judge — 명제 B′, split 설계, 채택 규칙의 역할 (§13.2, §13.5, §14.1 항상-PPI 손실)
5. Where to spend human judgments — 결정 가중치(명제 C 정정판), HT/CV 추정량, active inference와의 관계(THEORY), 비교군 (§18, §19, F7)
6. Evaluation protocol and the J50 metric — DRAFT_v0.4_metrics_section
7. Pre-registered external evaluation — LOCK v0.4, §14 (유효성 통과, 효율 미달, 원인)
8. Negative and bounded results — 구간 국소 하이브리드(§16.2), 메뉴 배분 탐색(EXPLORATION), 보정 가정 능동 표집(§18→§19 정정)
9. Related work — DRAFT_v0.4_related_work
10. Limitations — 판정된 후보군 범위(§13.3), precision 주 결과·set-F1 부록(선형화 편향 실측), anytime 미구현, 개발 데이터 노출, 판정자 2계열
Appendix A: set-F1 linearised audit (86_f1_weighted.py 결과) · B: theory proofs · C: reproducibility (seeds, position_ids, rng streams) · D: full J50 tables

## Figures
F4 gain vs ρ (54 pts) · F5 ACT vs budget by judge (dbpedia) · F6 ρ×N×ε map · F7 J50 by method · (primary run table)

## Open items before assembly
- set-F1 부록 실험(진행 중), 미사용 collection 확증(LOCK v0.5; 데이터 결정 대기), 본문 영문화.
