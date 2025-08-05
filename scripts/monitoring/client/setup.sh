#!/bin/bash

# bash ./setup.sh 

# 현재 스크립트 위치 기준으로 .paths/paths.env 경로 계산
CURRENT_DIR=$(dirname "$0")
PROJECT_ROOT=$(realpath "$CURRENT_DIR/../../..")

# env 파일 로드
source "$PROJECT_ROOT/.paths/paths.env"

MONITORING_CLIENT_PATH=$(realpath "${PROJECT_ROOT}/${SERVICES_MONITORING_CLIENT}")
COMPOSE_FILE_PATH=$(realpath "${MONITORING_CLIENT_PATH}/docker-compose.yml")

export PROJECT_ROOT=$PROJECT_ROOT
export SERVICES_MONITORING_CLIENT=$SERVICES_MONITORING_CLIENT

# 환경변수 확인 (테스트용)
# echo "PROJECT_ROOT=$PROJECT_ROOT"
# echo "COMPOSE_FILE_PATH=$COMPOSE_FILE_PATH"

# docker compose 실행 --build 옵션이 없으면 원격 저장소 docker를 먼저 pull 받게 된다
docker compose -f $COMPOSE_FILE_PATH up --build -d
