# mlops_pipeline_dag.py

# Airflow 라이브러리 임포트
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# 파이프라인에서 사용할 개별 작업 함수 임포트
from scripts.airflow.pipeline_tasks import popular_movie_data_engineering_task
from scripts.airflow.pipeline_tasks import model_train_task
from scripts.airflow.pipeline_tasks import model_inference_task

# ================ DAG 스케줄 예시 ==================
# schedule_interval 주요 예시
#  - "*/3 * * * *" : 3분마다 실행
#  - "*/5 * * * *" : 5분마다 실행
#  - "@hourly" : 매 정시(매 시간)마다 실행
#  - "0 * * * *" : 매 시 0분(즉, 매 시간 정각)마다 실행
#  - "0 0 * * *" : 매일 자정(00:00)에 실행
#  - "30 2 * * *" : 매일 02:30에 실행
#  - "0 9 * * MON" : 매주 월요일 오전 9시에 실행
#  - None : 수동 트리거만 허용(자동 실행 없음)
#  - "@daily" : 매일 0시 실행(= "0 0 * * *"와 동일)
#  - "@once" : DAG 최초 등록 시 한 번만 실행
# ==================================================

# DAG(파이프라인) 기본 설정
with DAG(
    dag_id='mlops_movie_recommend_pipeline',  # DAG 이름(유니크)
    start_date=days_ago(1),                  # DAG 최초 시작일(1일 전)
    schedule_interval='*/3 * * * *',         # 3분마다 실행(테스트용, 필요시 변경)
    # schedule_interval='*/5 * * * *',       # 5분마다 실행
    # schedule_interval='0 * * * *',         # 매 시 정각마다 실행
    # schedule_interval='0 0 * * *',         # 매일 자정(00:00) 실행
    # schedule_interval=None,                # 자동 실행 비활성화(수동 트리거만 허용)
    # schedule_interval='@daily',            # 매일 0시
    # schedule_interval='@hourly',           # 매 시 정각
    # schedule_interval='0 9 * * MON',       # 매주 월요일 오전 9시
    default_args={
        'owner': 'airflow',                  # DAG 소유자
        'depends_on_past': False,            # 이전 DAG 실행 결과와 무관하게 실행
        'retries': 1,                        # 실패 시 재시도 횟수
    },
    tags=['mlops', 'movie_recommend'],       # DAG 태그
    # catchup=False,                        # 이전 실행분 캐치업 방지(선택적, 테스트에 유용)
) as dag:

    # ---------------------------
    # 1. 데이터 추출/전처리/저장
    # ---------------------------
    # extract_data_task: 외부 데이터 수집, 전처리, 저장을 담당하는 함수
    popular_movie_data_engineering_task = PythonOperator(
        task_id='extract_data',                                 # 태스크 ID(유니크)
        python_callable=popular_movie_data_engineering_task,    # 실행 함수
    )

    # ---------------------------
    # 2. 모델 학습 (or 파이프라인 학습)
    # ---------------------------
    # train_task: 머신러닝/딥러닝 모델을 학습하는 함수
    model_train_task = PythonOperator(
        task_id='train_model',                  # 태스크 ID
        python_callable=model_train_task,       # 실행 함수
    )
    
    # ---------------------------
    # 3. 모델 추론 결과
    # ---------------------------
    # inference_task: 머신러닝/딥러닝 모델을 추론하는 함수
    model_inference_task = PythonOperator(
        task_id='inference_model',               # 태스크 ID
        python_callable=model_inference_task,    # 실행 함수
    )

    # --------------------------------
    # Task 간의 의존성(Dependency) 정의
    # --------------------------------
    # 순서대로 실행되도록 의존성 설정
    popular_movie_data_engineering_task >> model_train_task >> model_inference_task

