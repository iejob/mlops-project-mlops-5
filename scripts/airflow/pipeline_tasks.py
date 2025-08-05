from scripts.main import run_popular_movie_pipeline
from scripts.main import run_train
from scripts.main import run_inference

# ========== Airflow에서 사용할 Task 함수 ==========
# 데이터 크롤링, 전처리 및 저장 작업
def popular_movie_data_engineering_task(**context):
    run_popular_movie_pipeline()
    
# 데이터 분석 및 모델 학습 작업
def model_train_task(**context):
    # 필요시 context에서 파라미터 전달
    run_train(model_name, batch_size, dim, num_epochs)

# 모델 추론 작업
def model_inference_task(**context):
    # 필요시 context에서 파라미터 전달
    run_inference(batch_size=batch_size)