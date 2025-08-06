import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import numpy as np
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List

from scripts.inference.inference import (
    load_checkpoint, init_model, inference, recommend_to_df
)
from scripts.postprocess.inference_to_db import read_db
from scripts.main import run_popular_movie_pipeline, run_train, run_inference

# FastAPI 앱 정의 및 CORS 설정
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 환경변수 로드
load_dotenv()

# 모델 불러오기 (서버 시작 시 1회)
try:
    checkpoint = load_checkpoint()
    model, scaler, label_encoder = init_model(checkpoint)
except Exception as e:
    import traceback
    print("=== 모델/스케일러/라벨 인코더 로딩 실패 ===")
    traceback.print_exc()
    # 임시로 None 할당 (추론/학습 엔드포인트는 500을 반환하도록)
    model, scaler, label_encoder = None, None, None

# 요청 데이터 스키마 정의
class InferenceInput(BaseModel):
    user_id: int
    content_id: int
    watch_seconds: int
    rating: float
    popularity: float

class InferenceBatchInput(BaseModel):
    batch: List[InferenceInput]


# 데이터 수집/전처리 엔드 포인트
@app.post("/run/prepare-data")
def run_prepare_data():
    try:
        run_popular_movie_pipeline()
        return {"result": "prepare-data finished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 모델 학습 엔드 포인트
@app.post("/run/train")
def run_training(model_name: str = "movie_predictor"):
    try:
        run_train(model_name)
        return {"result": "train finished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 모델 추론 엔드 포인트
@app.post("/run/model-inference")
def run_batch_inference():
    try:
        run_inference()
        return {"result": "model-inference finished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST /predict
@app.post("/predict")
async def predict(input_data: InferenceInput):
    try:
        data = np.array([
            input_data.user_id,
            input_data.content_id,
            input_data.watch_seconds,
            input_data.rating,
            input_data.popularity
        ])
        result = inference(model, scaler, label_encoder, data)
        return {
            "user_id": input_data.user_id,
            "recommended_content_id": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST /predict/batch
@app.post("/predict/batch")
async def predict_batch(input_batch: InferenceBatchInput):
    try:
        input_list = input_batch.batch

        data_list = []
        user_ids = []

        for item in input_list:
            user_ids.append(item.user_id)
            data_list.append([
                item.user_id,
                item.content_id,
                item.watch_seconds,
                item.rating,
                item.popularity
            ])

        data = np.array(data_list)

        results = inference(model, scaler, label_encoder, data, batch_size=len(data))

        output = []
        for uid, reco in zip(user_ids, results):
            output.append({
                "user_id": uid,
                "recommended_content_id": reco
            })

        return {"batch_results": output}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

# GET /latest-recommendations
@app.get("/latest-recommendations")
async def latest_recommendations(k: int = 5):
    try:
        result = read_db("postgres", "recommend", k=k)
        return {"recent_recommend_content_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get /available-content-ids
@app.get("/available-content-ids")
async def available_ids():
    return {
        "count": len(label_encoder.classes_),
        "available_content_ids": label_encoder.classes_.tolist()
    }


# Get /health
@app.get("/health")
async def health_check():
    # model, scaler, label_encoder 등이 None이면 warning 메시지 추가
    status = "ok" if all([model, scaler, label_encoder]) else "degraded"
    return {"status": status}


@app.get("/info")
async def get_info():
    return {"service": "mlops-api", "version": "1.0.2"}

# 서버 직접 실행 시
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

