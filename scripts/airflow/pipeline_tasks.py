import requests
import logging
import os

# server1 API 베이스 URL 설정
SERVER_WORKHORSE = os.getenv('SERVER_WORKHORSE')
SERVER1_API_BASE = f"http://13.220.161.211:8000"

# -----------------------------
# 파이프라인 단계별 POST 엔드포인트 추가
# -----------------------------

# 데이터 준비 API 호출
def call_run_prepare_data_api():
    try:
        resp = requests.post(f"{SERVER1_API_BASE}/run/prepare-data", timeout=600)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"Prepare data API failed: {e}")
        raise

# 모델 학습 API 호출
def call_run_train_api(model_name="movie_predictor"):
    try:
        params = {"model_name": model_name}
        resp = requests.post(f"{SERVER1_API_BASE}/run/train", params=params, timeout=1200)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"Train API failed: {e}")
        raise

# 모델 추론 API 호출
def call_run_model_inference_api():
    try:
        resp = requests.post(f"{SERVER1_API_BASE}/run/model-inference", timeout=600)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"Model inference API failed: {e}")
        raise

# 서버 상태 확인 API 호출
def call_health_api():
    try:
        resp = requests.get(f"{SERVER1_API_BASE}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        raise

# 예측 API 호출
def call_predict_api(payload):
    try:
        resp = requests.post(f"{SERVER1_API_BASE}/predict", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()  # 예측 결과 반환
    except Exception as e:
        logging.error(f"Predict API failed: {e}")
        raise

# 서버 정보 API 호출
def call_info_api():
    try:
        resp = requests.get(f"{SERVER1_API_BASE}/info", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"Info API failed: {e}")
        raise