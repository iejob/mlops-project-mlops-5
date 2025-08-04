#!/bin/bash

# DATA_DIR 환경변수 에러 발생하면 스크립트 실행 전에 아래 명령어 실행해야 함
export HOME_DIR=/home/ubuntu

# bash ./setup.sh 

# 현재 스크립트 위치 기준으로 .paths/paths.env 경로 계산
CURRENT_DIR=$(dirname "$0")
PROJECT_ROOT=$(realpath "$CURRENT_DIR/../../..")

# env 파일 로드
source "$PROJECT_ROOT/.paths/paths.env"

# project root 상위에 Grafana 데이터 저장용 dir 생성
GRAFANA_DATA_PATH=$(realpath "${HOME_DIR}/${GRAFANA_DATA_DIR}")
LOKI_DATA_PATH=$(realpath "${HOME_DIR}/${LOKI_DATA_DIR}")

# PROJECT_ROOT 기준 mointoring/infra/docker-compose.yml 위치
COMPOSE_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_INFRA}/docker-compose.yml")

# grafana-data directory 생성 및 권한 변경
mkdir -p "$GRAFANA_DATA_PATH"
sudo chown -R 472:472 "$GRAFANA_DATA_PATH"
sudo chmod -R 775 "$GRAFANA_DATA_PATH"

# loki-data directory 생성 및 권한 변경
mkdir -p "$LOKI_DATA_PATH"
sudo chown -R 10001:10001 "$LOKI_DATA_PATH"
sudo chmod -R 775 "$LOKI_DATA_PATH"

# 환경변수 확인 (테스트용)
# echo "HOME_DIR=$HOME_DIR"
# echo "PROJECT_ROOT=$PROJECT_ROOT"
# echo "GRAFANA_DATA_DIR=$GRAFANA_DATA_DIR"
# echo "GRAFANA_DATA_PATH=$GRAFANA_DATA_PATH"
# echo "LOKI_DATA_DIR=$LOKI_DATA_DIR"
# echo "LOKI_DATA_PATH=$LOKI_DATA_PATH"
# echo "COMPOSE_FILE_PATH=$COMPOSE_FILE_PATH"

docker compose -f $COMPOSE_FILE_PATH up -d