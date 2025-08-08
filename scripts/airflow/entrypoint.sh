#!/usr/bin/env bash

# 스크립트 실행 중 오류 발생 시 즉시 중단
set -e

# Airflow 기본 설정 시도
try_init() {
    # 지정된 횟수만큼 DB 연결을 시도
    airflow db check --retry 30 --retry-delay 5
}

# Airflow DB 마이그레이션 및 관리자 계정 생성
init_airflow() {
    # DB가 준비될 때까지 대기
    try_init

    # DB 마이그레이션 실행 (테이블 생성 및 업데이트)
    airflow db migrate

    # Airflow 관리자 계정이 없으면 생성
    airflow users list | grep -q "admin" || \
    airflow users create \
        --username admin \
        --password admin \
        --firstname Anonymous \
        --lastname Admin \
        --role Admin \
        --email admin@example.org
}

# 전달된 인자에 따라 분기 처리
case "$1" in
  webserver)
    # DB가 준비될 때까지 대기 (초기화는 스케줄러가 담당)
    try_init
    exec airflow webserver
    ;;
  scheduler)
    # DB 초기화 및 마이그레이션 실행 후 스케줄러 시작
    init_airflow
    exec airflow scheduler
    ;;
  *)
    # 그 외의 명령어는 그대로 실행
    exec "$@"
    ;;
esac