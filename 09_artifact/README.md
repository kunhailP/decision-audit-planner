# Public artifact contract

이 폴더는 제출 직전에 급히 만드는 supplement가 아니다. G1부터 재현성 증거를 축적한다.

## Final package

- environment lockfile
- immutable data/candidate manifest와 checksum
- tiny public fixture
- full experiment configs
- source code와 tests
- precomputed long-run row-level results
- `reproduce.sh` 또는 동일 역할의 단일 entry point
- expected runtime, storage, hardware
- paper table/figure mapping
- known deviations and failed runs
- license와 data-access instructions

## Clean-room test

원 연구환경과 다른 빈 환경에서 다음을 확인한다.

1. 설치가 문서대로 완료된다.
2. fixture smoke test가 통과한다.
3. precomputed row-level 결과에서 모든 headline 표·그림이 생성된다.
4. checksum이 맞지 않으면 실행이 중단된다.
5. 결과와 원고의 숫자가 자동 대조된다.

## Artifact claim

clean-room test를 통과하기 전에는 README나 논문에 “fully reproducible”이라고 쓰지 않는다.
