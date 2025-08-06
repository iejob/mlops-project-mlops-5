# Script 실행 방법

### 1. 환경 변수 설정
  각 스크립트를 실행하기 전 필요한 환경변수를 설정합니다.
  - **infra:**
    ```
    export SERVER_1_IP=123.123.123.123
    export WEBHOOK_ERROR_URL=https://hooks.slack.com/services/....
    export WEBHOOK_WARN_URL=https://hooks.slack.com/services/....
    ```
  - **client:**
    ```
    export SERVER_2_IP=123.123.123.123
    ```
### 2. 프로젝트 루트 디렉토리로 이동
  스크립트 실행 전에 프로젝트 루트 디렉토리로 이동합니다.
### 3. 스크립트 실행
  아래 명령어로 스크립트를 실행합니다.
  - **infra:**
    ```
    bash ./scripts/monitoring/infra/setup.sh 
    ```
  - **client:**
    ```
    bash ./scripts/monitoring/client/setup.sh
    ```
### 4. 결과 확인
  아래 파일들이 잘 생성되었는지 확인하고, `docker ps` 명령어로 컨테이너가 정상 실행 중인지 확인합니다.
  - **infra:**
    - ./services/monitoring/infra/prometheus/prometheus.yml
    - ./services/monitoring/infra/alertmanager/alertmanager.yml
  - **client:**
    - ./services/monitoring/client/promtail/promtail-config.yml