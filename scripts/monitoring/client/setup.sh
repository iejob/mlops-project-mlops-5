#!/bin/bash

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

MONITORING_CLIENT_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_CLIENT}")
COMPOSE_FILE_PATH=$(realpath "${MONITORING_CLIENT_PATH}/docker-compose.yml")

export PROJECT_ROOT=$PROJECT_ROOT

# 환경변수 확인 (테스트용)
# echo "PROJECT_ROOT=$PROJECT_ROOT"
# echo "COMPOSE_FILE_PATH=$COMPOSE_FILE_PATH"

if [ -z "$SERVER_2_IP" ]; then
  echo "❌ SERVER_2_IP 환경변수가 설정되지 않았습니다."
  exit 1
fi

if [ -z "$PROJECT_ROOT" ]; then
  echo "❌ PROJECT_ROOT 환경변수가 설정되지 않았습니다."
  exit 1
fi

# .tpl 파일 -> 실제 설정 파일 생성
echo "📄 promtail-config.yml 생성 중..."
PROMTAIL_CONFIG_TPL_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_CLIENT}/promtail/promtail-config.yml.tpl")
PROMTAIL_CONFIG_FILE_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_CLIENT}/promtail/promtail-config.yml")

# echo "PROMTAIL_CONFIG_TPL_FILE_PATH=$PROMTAIL_CONFIG_TPL_FILE_PATH"
# echo "PROMTAIL_CONFIG_FILE_PATH=$PROMTAIL_CONFIG_FILE_PATH"

envsubst < $PROMTAIL_CONFIG_TPL_FILE_PATH > $PROMTAIL_CONFIG_FILE_PATH

# monitoring-network 네트워크가 없으면 생성
docker network inspect monitoring-network >/dev/null 2>&1 || docker network create monitoring-network

# docker compose 실행 --build 옵션이 없으면 원격 저장소 docker를 먼저 pull 받게 된다
docker compose -f $COMPOSE_FILE_PATH up --build -d