#!/bin/bash

# 저장할 폴더명
BASE_LOG_DIR="logs/docker-services"

# 서비스 리스트 (컨테이너 명과 동일해야 함)
SERVICES=("my-mlops-api" "my-mlops-db" "my-mlops-frontend" "my-mlops-model")

# logs 디렉토리 생성
mkdir -p "$BASE_LOG_DIR"

for service in "${SERVICES[@]}"
do
  # 각 서비스 하위 폴더 생성
  mkdir -p "$BASE_LOG_DIR/$service"
  # 로그 파일 저장 (서비스명_날짜.log 형식)
  docker-compose logs --tail 1000 $service > "$BASE_LOG_DIR/$service/${service}_$(date +%Y%m%d_%H%M%S).log"
done

echo "로그 저장 완료!"
