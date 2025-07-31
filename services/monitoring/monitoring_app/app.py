from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import generate_latest, Counter, CONTENT_TYPE_LATEST


app = FastAPI()

# method, endpoint 별로 라벨 추가
# 요청 카운트
REQUEST_COUNT = Counter(
    "app_requests_count",
    "Total number of requests to app",
    ["method", "endpoint"]
)


@app.middleware("http")
async def count_requests(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response


@app.get("/")
async def read_root():
    return {"message": "Hello!"}


@app.get("/metrics")
async def metrics():
    # Prometheus 가 수집해갈 메트릭
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)


