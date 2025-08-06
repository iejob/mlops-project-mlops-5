import os
import pendulum
import requests
import json

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.exceptions import AirflowException
from datetime import timedelta


# 서버1 IP 주소 환경 변수 읽기
SERVER_1_IP_ADDRESS = os.getenv('SERVER_1_IP_ADDRESS')
if not SERVER_1_IP_ADDRESS:
    raise ValueError("Airflow 환경 변수에 'SERVER_1_IP_ADDRESS'가 설정되지 않았습니다.")

SERVER1_API_BASE = f"http://{SERVER_1_IP_ADDRESS}:8000"


def _check_api_health():
    """서버1 FastAPI의 /health 엔드포인트를 호출하여 상태를 확인합니다."""
    try:
        url = f"{SERVER1_API_BASE}/health"
        response = requests.get(url, timeout=60) # 타임아웃 60초(1분)
        response.raise_for_status() # 2xx 상태 코드가 아니면 HTTPError 발생
        
        health_status = response.json().get("status")
        if health_status == "ok":
            print(f"✅ API Health-check 성공: {response.json()}")
            return True
        else:
            print(f"🚨 API 상태가 'ok'가 아닙니다: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 API Health-check 중 네트워크 오류 발생: {e}")
        return False

def _run_pipeline_task(endpoint: str, expected_result: str, payload: dict = None):
    """지정된 FastAPI 엔드포인트를 호출하고 결과를 검증하는 공통 함수 (예외 처리 강화)"""
    url = f"{SERVER1_API_BASE}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    print(f"🚀 API 호출 시작: {url}, 페이로드: {payload or '없음'}")
    
    try:
        if payload:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=600) # 10분 타임아웃
        else:
            # timeout=1800초(30분)로 설정하여 긴 실행 시간 허용
            response = requests.post(url, headers=headers, timeout=1800)
            
        # 1. HTTP 상태 코드 검사
        response.raise_for_status()
        
        # 2. 응답 JSON 내용 검사
        response_json = response.json()
        result = response_json.get("result")
        if result == expected_result:
            print(f"✅ 태스크 성공: {response_json}")
            return response_json
        else:
            # 성공 응답(200)을 받았지만, 내용이 기대와 다른 경우
            error_message = f"🚨 태스크 응답 검증 실패. 예상 결과: '{expected_result}', 실제 응답: {response_json}"
            print(error_message)
            raise AirflowException(error_message)
            
    except requests.exceptions.HTTPError as e:
        # 4xx, 5xx 에러 처리
        error_message = f"🚨 API가 오류 응답을 반환했습니다 (HTTP Error). 상태코드: {e.response.status_code}, 응답: {e.response.text}"
        print(error_message)
        raise AirflowException(error_message)
        
    except requests.exceptions.RequestException as e:
        # 네트워크 연결 오류, 타임아웃 등
        error_message = f"🚨 API 호출 중 네트워크 오류 발생: {e}"
        print(error_message)
        raise AirflowException(error_message)
        
    except Exception as e:
        # JSON 파싱 실패 등 예기치 않은 오류
        error_message = f"🚨 태스크 실행 중 예기치 않은 오류 발생: {e}"
        print(error_message)
        raise AirflowException(error_message)

default_args = {
    'owner': 'mlops-3xplusy-team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="mlops-pipeline-gemini-dag",
    default_args=default_args,
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Seoul"),
    schedule_interval='*/10 * * * *',
    catchup=False,
    tags=["mlops", "fastapi", "automated-pipeline"],
    doc_md="""
    ### MLOps 전체 파이프라인 DAG (환경 변수 기반)
    
    **환경 변수**를 사용하여 서버1의 API URL을 동적으로 설정합니다.
    **PythonOperator**를 사용하여 FastAPI 엔드포인트를 호출합니다.
    
    1. **데이터 준비**: TMDB 데이터 크롤링, 전처리, PostgreSQL/S3 저장
    2. **모델 학습**: 데이터셋 로드, MLflow 연동 학습, 모델 아티팩트 저장
    3. **배치 추론**: 학습된 최신 모델로 배치 추론 수행, 결과 저장
    """,
) as dag:
    # 1. API 서버 상태 확인 (PythonSensor)
    api_health_check = PythonSensor(
        task_id="check_api_health",
        python_callable=_check_api_health,
        poke_interval=10,
        timeout=60,
        mode="poke",
    )

    # 2. 데이터 준비 파이프라인 실행
    run_prepare_data_task = PythonOperator(
        task_id="run_prepare_data",
        python_callable=_run_pipeline_task,
        op_kwargs={
            "endpoint": "run/prepare-data",
            "expected_result": "prepare-data finished",
        },
    )

    # 3. 모델 학습 파이프라인 실행
    run_train_task = PythonOperator(
        task_id="run_train",
        python_callable=_run_pipeline_task,
        op_kwargs={
            "endpoint": "run/train",
            "expected_result": "train finished",
            "payload": {"model_name": "movie_predictor"},
        },
    )

    # 4. 모델 배치 추론 파이프라인 실행
    run_batch_inference_task = PythonOperator(
        task_id="run_batch_inference",
        python_callable=_run_pipeline_task,
        op_kwargs={
            "endpoint": "run/model-inference",
            "expected_result": "model-inference finished",
        },
    )

    # 태스크 의존성 설정
    api_health_check >> run_prepare_data_task >> run_train_task >> run_batch_inference_task