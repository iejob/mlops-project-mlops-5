# mlops_pipeline_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from scripts.data_prepare.pipeline_tasks import extract_data_task
from scripts.train.pipeline_tasks import train_task
from scripts.train.pipeline_tasks import all_pipeline_task

# DAG 기본 설정
with DAG(
    dag_id='mlops_movie_recommend_pipeline',
    start_date=days_ago(1),
    schedule_interval='*/1 * * * *',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 1,
    },
    tags=['mlops', 'movie_recommend'],
) as dag:

    # 1. 데이터 추출/전처리/저장
    extract_data_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data_task,
    )

    # 2. 모델 학습 (or 파이프라인 학습)
    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_task,
    )

    # Task 간의 의존성(Dependency) 정의
    extract_data_task >> train_task
