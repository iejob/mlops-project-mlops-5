import os
import pendulum
from datetime import timedelta

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor

# DAG의 로직을 간결하게 유지하기 위해 실제 API 호출 로직을 분리해 놓은 파일
from scripts.airflow.pipeline_tasks import (
    check_api_health,  # API 서버의 상태를 확인하는 함수
    run_pipeline_task  # FastAPI 엔드포인트를 호출하는 범용 함수
)

# Airflow UI의 Variable 또는 환경 변수에 'SERVER_1_IP_ADDRESS'를 설정
SERVER_1_IP_ADDRESS = os.getenv('SERVER_1_IP_ADDRESS')
if not SERVER_1_IP_ADDRESS:
    # 환경 변수가 설정되지 않았을 경우 DAG이 로드되지 않도록 예외 발생
    raise ValueError("Airflow 환경 변수에 'SERVER_1_IP_ADDRESS'가 설정되지 않았습니다.")

# FastAPI 서버의 기본 URL 정의
SERVER1_API_BASE = f"http://{SERVER_1_IP_ADDRESS}:8000"

# 기본 DAG 설정
default_args = {
    'owner': 'mlops-3xplusy-team',                              # DAG 소유자 지정
    'depends_on_past': False,                                   # 이전 DAG 실행 성공 여부에 의존하지 않음
    'retries': 2,                                               # 태스크 실패 시 2번 재시도
    'retry_delay': timedelta(minutes=5),                        # 5분 간격으로 재시도
}

# DAG 정의
with DAG(
    dag_id="mlops_automated_pipeline_dag",                      # DAG의 고유 ID
    default_args=default_args,                                  # 기본 인자 설정 
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Seoul"),  # DAG 실행 시작일
    schedule_interval='*/5 * * * *',                            # 5분마다 DAG 실행
    catchup=False,                                              # 이전 실행되지 않은 DAG을 소급하여 실행하지 않음
    tags=["mlops", "fastapi", "automated-pipeline"],            # DAG 분류를 위한 태그
    doc_md="""
    ### MLOps 전체 파이프라인 DAG (로직 분리 버전)
    
    - **pipeline_tasks.py**: 실제 API 호출 로직 담당
    - **DAG 파일**: 전체 파이프라인의 구조와 흐름(오케스트레이션)만 담당
    
    1. **데이터 준비**: TMDB 데이터 크롤링, 전처리, PostgreSQL/S3 저장
    2. **모델 학습**: 데이터셋 로드, MLflow 연동 학습, 모델 아티팩트 저장
    3. **배치 추론**: 학습된 최신 모델로 배치 추론 수행, 결과 저장
    """,
) as dag:

    # 1. API 서버 상태 확인 (PythonSensor)
    # API 서버가 정상적으로 작동할 때까지 대기하는 센서 태스크
    api_health_check = PythonSensor(
        task_id="check_api_health",                             # 태스크 ID
        python_callable=check_api_health,                       # pipeline_tasks.py에서 import한 함수 사용
        op_kwargs={'api_base_url': SERVER1_API_BASE},           # 함수에 전달할 인자
        poke_interval=10,                                       # 10초마다 상태 확인
        timeout=60,                                             # 총 60초(1분) 동안 대기
        mode="poke",                                            # 'poke' 모드로 주기적으로 호출
    )

    # 2. 데이터 준비 파이프라인 실행 (PythonOperator)
    run_prepare_data_task = PythonOperator(
        task_id="run_prepare_data",                             # 태스크 ID
        python_callable=run_pipeline_task,                      # pipeline_tasks.py에서 import한 함수 사용
        op_kwargs={
            "api_base_url": SERVER1_API_BASE,                   # FastAPI 서버의 기본 URL 
            "endpoint": "run/prepare-data",                     # 데이터 준비 엔드포인트
            "expected_result": "prepare-data finished",         # 기대하는 응답 결과
        },
    )

    # 3. 모델 학습 파이프라인 실행 (PythonOperator)
    run_train_task = PythonOperator(
        task_id="run_train",                                    # 태스크 ID
        python_callable=run_pipeline_task,                      # pipeline_tasks.py에서 import한 함수 사용
        op_kwargs={
            "api_base_url": SERVER1_API_BASE,                   # FastAPI 서버의 기본 URL
            "endpoint": "run/train",                            # 모델 학습 엔드포인트
            "expected_result": "train finished",                # 기대하는 응답 결과
            "payload": {"model_name": "movie_predictor"},       # 학습할 모델명을 페이로드로 전달
        },
    )

    # 4. 모델 배치 추론 파이프라인 실행 (PythonOperator)
    run_batch_inference_task = PythonOperator(
        task_id="run_batch_inference",                          # 태스크 ID
        python_callable=run_pipeline_task,                      # pipeline_tasks.py에서 import한 함수 사용
        op_kwargs={
            "api_base_url": SERVER1_API_BASE,                   # FastAPI 서버의 기본 URL
            "endpoint": "run/model-inference",                  # 배치 추론 엔드포인트
            "expected_result": "model-inference finished",      # 기대하는 응답 결과
        },
    )

    # 태스크 의존성 설정 (파이프라인 실행 순서)
    # API서버 상태 확인 -> 데이터 수집/전처리 저장 -> 모델 학습 -> 모델 배치 추론
    api_health_check >> run_prepare_data_task >> run_train_task >> run_batch_inference_task