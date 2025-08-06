#!/bin/bash

# 저장할 폴더명
BASE_LOG_DIR="logs"

# 서비스 리스트 (컨테이너 명과 동일해야 함)
SERVICES=("webserver" "scheduler" "postgres" "airflow-init")

# logs 디렉토리 생성
mkdir -p $BASE_LOG_DIR

for service in "${SERVICES[@]}"
do
  # 각 서비스 하위 폴더 생성
  mkdir -p $BASE_LOG_DIR/$service
  # 로그 파일 저장
  docker-compose logs --tail 1000 $service > $BASE_LOG_DIR/$service/$service_$(date +%Y%m%d_%H%M%S).log
done

echo "로그 저장 완료!"
