import os
import sys

# 현재 파일의 상위 디렉토리를 파이썬 모듈 경로에 추가 (상위폴더 import 용)
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import numpy as np
import uvicorn
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
from sqlalchemy import text

# 모델 추론 및 후처리 관련 함수들 import
from scripts.inference.inference import (
    load_checkpoint, init_model, inference, recommend_to_df
)
from scripts.postprocess.inference_to_db import write_db, read_db, get_movie_metadata_by_ids, get_engine

# 데이터 파이프라인, 학습, 추론 함수 import
from scripts.main import run_popular_movie_pipeline, run_train, run_inference

# FastAPI 앱 생성
app = FastAPI()

# CORS(Cross-Origin Resource Sharing) 설정: 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# .env 파일(환경변수) 로드
load_dotenv()

# 서버 실행 시 최초 1회 모델/스케일러/라벨 인코더 로드
try:
    checkpoint = load_checkpoint()
    model, scaler, label_encoder = init_model(checkpoint)
except Exception as e:
    print("=== 모델/스케일러/라벨 인코더 로딩 실패 ===")
    traceback.print_exc()
    # 오류 발생 시 None 할당(아래 엔드포인트에서 오류 반환)
    model, scaler, label_encoder = None, None, None

# POST /predict 요청에 사용할 입력 데이터 타입 정의 (Pydantic)
class InferenceInput(BaseModel):
    user_id: int
    content_id: int
    watch_seconds: int
    rating: float
    popularity: float
    
    
@app.get("/")
async def read_root():
    """API 상태 확인을 위한 루트 엔드포인트입니다."""
    return {"message": "MLOps API is running!"}    

# 데이터 수집 및 전처리 파이프라인 실행 엔드포인트
@app.post("/run/prepare-data")
def run_prepare_data():
    try:
        run_popular_movie_pipeline()
        return {"result": "prepare-data finished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 모델 학습 파이프라인 실행 엔드포인트
@app.post("/run/train")
def run_training(model_name: str = "movie_predictor"):
    try:
        run_train(model_name)
        return {"result": "train finished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 모델 추론(배치 인퍼런스) 파이프라인 실행 엔드포인트
@app.post("/run/model-inference")
def run_batch_inference():
    try:
        run_inference()
        return {"result": "model-inference finished"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 단일 입력값을 받아 추론 후 추천 결과 반환하는 엔드포인트
@app.post("/predict")
async def predict(input_data: InferenceInput):
    try:
        # 1. 입력 데이터를 numpy array로 변환
        data = np.array([
            input_data.user_id,
            input_data.content_id,
            input_data.watch_seconds,
            input_data.rating,
            input_data.popularity
        ])
        # 2. 추천(모델 추론) 수행
        result = inference(model, scaler, label_encoder, data)

        # 3. 추천 결과를 DataFrame 형태로 변환 후 DB에 저장
        df_to_save = recommend_to_df(result)
        write_db(df_to_save, os.getenv("DB_NAME"), "recommend")

        # 4. 추천 결과의 content_id에 대해 메타데이터 조회
        metadata = get_movie_metadata_by_ids(os.getenv("DB_NAME"), result)
        recommendations = [
            {
                "content_id": int(cid),
                "title": metadata.get(int(cid), {}).get("title", ""),
                "poster_url": metadata.get(int(cid), {}).get("poster_url", ""),
                "overview": metadata.get(int(cid), {}).get("overview", "")
            }
            for cid in result
        ]

        # 5. 사용자 ID와 추천 결과 반환
        return {
            "user_id": input_data.user_id,
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 최근 추천 결과를 조회하는 엔드포인트 (최신 k개)
@app.get("/latest-recommendations")
async def latest_recommendations(k: int = 10):
    try:
        content_ids = read_db(os.getenv("DB_NAME"), "recommend", k=k)
        unique_ids = list(dict.fromkeys(content_ids))  # 중복 제거
        if not unique_ids:
            return {"recent_recommendations": []}

        metadata = get_movie_metadata_by_ids("postgres", [int(cid) for cid in unique_ids])

        recommendations = [
            {
                "content_id": cid,
                "title": metadata.get(int(cid), {}).get("title", ""),
                "poster_url": metadata.get(int(cid), {}).get("poster_url", ""),
                "overview": metadata.get(int(cid), {}).get("overview", "")
            }
            for cid in unique_ids
            if cid in metadata 
        ]

        return {"recent_recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 사용 가능한 content_id 리스트를 반환하는 엔드포인트
@app.get("/available-content-ids")
async def available_ids():
    return {
        "count": len(label_encoder.classes_),
        "available_content_ids": label_encoder.classes_.tolist()
    }

# 사용 가능한 영화 목록(제목, 포스터 등) 반환 엔드포인트
@app.get("/available-contents")
async def available_contents():
    try:
        engine = get_engine("postgres")
        query = text("""
            SELECT DISTINCT content_id, title, poster_path
            FROM watch_logs
            WHERE poster_path IS NOT NULL AND title IS NOT NULL
            ORDER BY title ASC
        """)
        with engine.connect() as conn:
            result = conn.execute(query).mappings().all() 
            contents = [
                {
                    "content_id": int(row["content_id"]),
                    "title": row["title"],
                    "poster_url": f"https://image.tmdb.org/t/p/original{row['poster_path']}"
                }
                for row in result
            ]
        return {"available_contents": contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 서비스 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    # model, scaler, label_encoder가 None이면 degraded, 아니면 ok
    status = "ok" if all([model, scaler, label_encoder]) else "degraded"
    return {"status": status}

# 서비스 정보 반환 엔드포인트 (버전 확인용)
@app.get("/info")
async def get_info():
    return {"service": "my-mlops-api", "version": "1.3.3"}

# 이 파일이 메인으로 실행될 때 uvicorn으로 FastAPI 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
