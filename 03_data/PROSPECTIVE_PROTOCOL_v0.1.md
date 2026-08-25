# Prospective Validation Protocol v0.1 (C4 / M5) — 2026-08-25

상태: 후보 감사 단계. **collection lock 전에는 어떤 target label도 열지 않는다.**
이 문서의 확정(lock)은 사용자 결정 사항이며, lock 이후 변경은 금지된다.

## 원칙 (M6/D-007 대응)

- 기존 BEIR 13개는 전부 개발에 노출됨 → C4는 완전히 새로운 collection에서
  **단 한 번의 primary run**(P4)으로만 판정한다.
- Lock 내용: collection ID·버전·체크섬, candidate 구성 파이프라인 커밋,
  planner 하이퍼파라미터(FREEZE_PROPOSAL_v0.3), ε·α, 성공 판정 기준.
- Primary run 실패 시 결과를 덮어쓰지 않고 논문의 제약으로 보고한다 (POD_HANDOFF P4 규칙).

## 후보 3안 비교

### 옵션 A — TREC-DL passage (2021/2022) **run-set 기반** (권고)
- **장점: GPU 불필요.** TREC 제출 run들이 공개되어 있어, 여러 시스템의 run을
  "후보 생성기"로 사용해 consensus/rank 특성을 재구성할 수 있다. NIST graded
  qrels가 깊다(judgment coverage 우수 — M5 hole 문제 완화).
- 주의: 후보 특성 정의가 dense-embedding 파이프라인과 달라짐 → candidate
  구성 계약을 run-set 버전으로 별도 고정해야 함. lexoverlap은 corpus 텍스트
  필요(다운로드 가능, ~수 GB).
- 사전 확인 필요: 사용 run 목록과 연도, qrels 버전, licence.

### 옵션 B — BRIGHT (2024, reasoning-intensive retrieval)
- 장점: 최신, 분포 이동이 극적, ML 독자 관심 높음.
- 단점: dense 후보 생성에 GPU 필요(Pod), qrels가 상대적으로 얕음.

### 옵션 C — LongEval (CLEF, 시간적 shift)
- 장점: "시간에 따른 shift"라는 배포 서사와 정확히 일치, 공식 train/test 분리.
- 단점: 규모·라이선스 확인 필요, GPU 필요 가능성.

## 권고 조합

Primary = **옵션 A** (GPU 없이 로컬 실행 가능, coverage 깊음),
Secondary(자원 허용 시) = 옵션 B (Pod). 두 개가 되면 C4의 일반성이 강해진다.

## Lock 절차 (체크리스트)

1. [ ] collection·버전·다운로드 URL·checksum을 DATA_REGISTRY.yaml에 기록
2. [ ] candidate 구성 코드 commit hash 고정 (run-set 변형이면 별도 계약 문서)
3. [ ] planner 설정: FREEZE_PROPOSAL_v0.3 비준본의 hash 기록
4. [ ] 성공 판정 pre-registration: wrong-cert ≤ α, act 시 loss ≤ ε,
       abstain은 실패가 아님을 명시
5. [ ] 위 4개가 모두 커밋된 후에만 qrels/label 접근 (단 한 번)
