#!/bin/bash

# DATA_DIR 환경변수 에러 발생하면 스크립트 실행 전에 아래 명령어 실행해야 함
export HOME_DIR=/home/ubuntu

# bash ./setup.sh 

# 현재 스크립트 위치 기준으로 .paths/paths.env 경로 계산
CURRENT_DIR=$(dirname "$0")
PROJECT_ROOT=$(realpath "$CURRENT_DIR/../../..")

# 기존 경로 계산 코드 아래에 추가
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE"
fi

# env 파일 로드
source "$PROJECT_ROOT/.paths/paths.env"

# project root 상위에 Grafana 데이터 저장용 dir 생성
GRAFANA_DATA_PATH=$(realpath "${HOME_DIR}/${GRAFANA_DATA_DIR}")
LOKI_DATA_PATH=$(realpath "${HOME_DIR}/${LOKI_DATA_DIR}")

# PROJECT_ROOT 기준 mointoring/infra/docker-compose.yml 위치
COMPOSE_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_INFRA}/docker-compose.yml")

# 환경변수 확인 (테스트용)
# echo "HOME_DIR=$HOME_DIR"
# echo "PROJECT_ROOT=$PROJECT_ROOT"
# echo "GRAFANA_DATA_DIR=$GRAFANA_DATA_DIR"
# echo "GRAFANA_DATA_PATH=$GRAFANA_DATA_PATH"
# echo "LOKI_DATA_DIR=$LOKI_DATA_DIR"
# echo "LOKI_DATA_PATH=$LOKI_DATA_PATH"
# echo "COMPOSE_FILE_PATH=$COMPOSE_FILE_PATH"


# prometheus, alertmanager 환경 설정 yml 파일 생성
if [ -z "$SERVER_1_IP" ]; then
  echo "❌ SERVER_1_IP 환경변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$WEBHOOK_ERROR_URL" ]; then
  echo "❌ WEBHOOK_ERROR_URL 환경변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$WEBHOOK_WARN_URL" ]; then
  echo "❌ WEBHOOK_WARN_URL 환경변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$HOME_DIR" ]; then
  echo "❌ HOME_DIR 환경변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$GRAFANA_DATA_PATH" ]; then
  echo "❌ GRAFANA_DATA_PATH 환경변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$LOKI_DATA_PATH" ]; then
  echo "❌ LOKI_DATA_PATH 환경변수가 설정되지 않았습니다."
  exit 1
fi


# grafana-data directory 생성 및 권한 변경
mkdir -p "$GRAFANA_DATA_PATH"
sudo chown -R 472:472 "$GRAFANA_DATA_PATH"
sudo chmod -R 775 "$GRAFANA_DATA_PATH"

# loki-data directory 생성 및 권한 변경
mkdir -p "$LOKI_DATA_PATH"
sudo chown -R 10001:10001 "$LOKI_DATA_PATH"
sudo chmod -R 775 "$LOKI_DATA_PATH"


# .tpl 파일 -> 실제 설정 파일 생성
echo "📄 prometheus.yml 생성 중..."
PROMETHEUS_CONFIG_TPL_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_INFRA}/prometheus/prometheus.yml.tpl")
PROMETHEUS_CONFIG_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_INFRA}/prometheus/prometheus.yml")

# echo "PROMETHEUS_CONFIG_TPL_FILE_PATH=$PROMETHEUS_CONFIG_TPL_FILE_PATH"
# echo "PROMETHEUS_CONFIG_FILE_PATH=$PROMETHEUS_CONFIG_FILE_PATH"

envsubst < $PROMETHEUS_CONFIG_TPL_FILE_PATH > $PROMETHEUS_CONFIG_FILE_PATH

echo "📄 alertmanager.yml 생성 중..."
ALERTMANAGER_CONFIG_TPL_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_INFRA}/alertmanager/alertmanager.yml.tpl")
ALERTMANAGER_CONFIG_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_INFRA}/alertmanager/alertmanager.yml")

# echo "ALERTMANAGER_CONFIG_TPL_FILE_PATH=$ALERTMANAGER_CONFIG_TPL_FILE_PATH"
# echo "ALERTMANAGER_CONFIG_FILE_PATH=$ALERTMANAGER_CONFIG_FILE_PATH"

# monitoring-network 네트워크가 없으면 생성
docker network inspect monitoring-network >/dev/null 2>&1 || docker network create monitoring-network

envsubst < $ALERTMANAGER_CONFIG_TPL_FILE_PATH > $ALERTMANAGER_CONFIG_FILE_PATH

docker compose -f $COMPOSE_FILE_PATH up -d