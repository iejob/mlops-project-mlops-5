# mlops_pipeline_dag.py

# Airflow 라이브러리 임포트
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

# pipeline_tasks.py에서 메서드 import
from scripts.airflow.pipeline_tasks import (
    call_run_prepare_data_api,
    call_run_train_api,
    call_run_model_inference_api,
    call_health_api,
    call_predict_api
)

# ================ DAG 스케줄 예시 ==================
# schedule_interval 주요 예시
#  - "*/3 * * * *"  : 3분마다 실행
#  - "*/5 * * * *"  : 5분마다 실행
#  - "@hourly"      : 매 정시(매 시간)마다 실행
#  - "0 * * * *"    : 매 시 0분(즉, 매 시간 정각)마다 실행
#  - "0 0 * * *"    : 매일 자정(00:00)에 실행
#  - "30 2 * * *"   : 매일 02:30에 실행
#  - "0 9 * * MON"  : 매주 월요일 오전 9시에 실행
#  - None           : 수동 트리거만 허용(자동 실행 없음)
#  - "@daily"       : 매일 0시 실행(= "0 0 * * *"와 동일)
#  - "@once"        : DAG 최초 등록 시 한 번만 실행
# ==================================================

default_args={
    'owner': 'airflow',                         # DAG 소유자
    'depends_on_past': False,                   # 이전 DAG 실행 결과와 무관하게 실행
    'retries': 2,                               # 실패 시 재시도 횟수
    'retry_delay': timedelta(minutes=5),        # 재시도 간격
}

# DAG(파이프라인) 기본 설정
with DAG(
    dag_id='mlops_movie_recommend_pipeline',    # DAG 이름(유니크)
    default_args=default_args,                  # 기본 인자 설정
    start_date=days_ago(1),                     # DAG 최초 시작일(1일 전)
    schedule_interval='*/3 * * * *',            # 3분마다 실행(테스트용, 필요시 변경)
    tags=['mlops', 'movie_recommend'],          # DAG 태그
    # catchup=False,                            # 이전 실행분 캐치업 방지(선택적, 테스트에 유용)
) as dag:

    # 1. 데이터 수집/전처리 (서버1의 /run/prepare-data API 호출)
    extract_data_task = PythonOperator(
        task_id='extract_data',
        python_callable=call_run_prepare_data_api,
    )

    # 2. 모델 학습 (서버1의 /run/train API 호출)
    train_model_task = PythonOperator(
        task_id='train_model',
        python_callable=call_run_train_api,
        op_kwargs={'model_name': 'movie_predictor'},   # 필요시 파라미터 변경
    )

    # 3. 모델 추론 (서버1의 /run/model-inference API 호출)
    inference_model_task = PythonOperator(
        task_id='inference_model',
        python_callable=call_run_model_inference_api,
    )

    # 4. 서버1 헬스체크 (선택)
    check_health_task = PythonOperator(
        task_id='check_server1_health',
        python_callable=call_health_api,
    )

    # 5. 예측 결과 API 호출 (예: 실시간 추천 테스트)
    def do_predict_fn():
        # payload 예시 (테스트용/실제값으로 교체)
        payload = {
            "user_id" : 1,
            "content_id" : 238,
            "watch_seconds" : 600,
            "rating" : 8.5,
            "popularity" : 100.0
        }
        return call_predict_api(payload)
    
    # 예측 API 호출 Task (실제 실행)
    do_predict_task = PythonOperator(
        task_id='call_predict',
        python_callable=do_predict_fn,
    )

    # --------------- 의존성 정의 (순차 실행) ----------------
    extract_data_task >> train_model_task >> inference_model_task >> check_health_task >> do_predict_task

