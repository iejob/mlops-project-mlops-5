# 2025-08-06 update 

주요 업데이트
* 도커 컨테이너 및 네트워크 네이밍 통일
  - PostgreSQL DB   :   `my-mlops-db`   
  - 모델 학습 및 추론 :   `my-mlops-model`     
  - FastAPI         :   `my-mlops-api`    
  - React           :   `my-mlops-frontend`   
  - 네트워크         :   `my-mlops-network`   
  → 앞으로 도커컴포즈파일 작성시 (특히 네트워크) 위 네이밍 사용하시면 됩니다.

* FastAPI 도커 엔드포인트 변경사항
  - `/predict` 에 title, poster_url 추가    
  - `/predict/batch` 삭제   
  - `/latest-recommendations` 기본값 10으로 변경    
  - `/available-contents` 추가    

* React 추가

---

## 모델 학습 및 추론
* 업데이트 버젼: v1.4.4
* 역할
  - TMDB 데이터 다운로드      
  - 가상유저데이터 생성       
  - 모델 학습 및 추론 (학습평가기준: Cross-entropy Loss, Accuracy)    
  - 추론 결과 저장 및 PostgreSQL, S3에 업로드     


## FastAPI 
* 업데이트 버젼: v1.3.4
* 역할: FastAPI 서버 실행 및 추천 결과 제공 (영화 제목 및 포스터)
* 주요 엔드포인트

| Method | Endpoint                       | 설명                                             |
| ------ | ------------------------------ | ------------------------------------------------ |
| GET    | `http://localhost:8000/docs`   | Swagger UI 인터페이스                            |
| GET    | `/health`                      | 서버 상태 확인 (헬스체크)                        |
| GET    | `/available-content-ids`       | 추천 가능한(학습된) 콘텐츠 ID 목록 조회          |
| GET    | `/available-contents`          | 추천 가능한(학습된) 콘텐츠 ID, 제목, 포스터 조회 |
| GET    | `/latest-recommendations?k=10` | 가장 최근 추천 결과 k개 조회 (기본 10개)         |
| POST   | `/predict`                     | 단일 사용자 입력에 대한 콘텐츠 추천              |


## React
* 업데이트 버젼: v1.2.0
* 역할: FastAPI 결과를 React서버를 이용하여 사용자에게 제공 (영화 타이틀 및 포스터)
  - 기본적으로 첫 화면에 latest-recommendations 제공    
  - `POST /predict` 됨에 따라 해당 영화가 추가 제공

---




## 파이프라인 실행 방법
     
**실행 전 필수 설정**         

**1.** 현재 로컬 디렉토리에 `.env` 파일 준비  
- `.env` 파일은 슬랙으로 공유드렸습니다.
- 해당 .env 파일은 PostgreSQL, S3에 접근하기 위함입니다.  

**2.** 현재 로컬 디렉토리에 다음과 같은 `env.js` 파일 생성 또는 수정  
```js
// env.js
window._env_ = {
  REACT_APP_API_ENDPOINT: "http://<EC2_IP>:3000"
};
```
- EC2 퍼블릭 IPv4 주소 확인 *(AWS EC2 대시보드 → 인스턴스 선택 → 퍼블릭 IPv4 주소 복사)* 후 위의 *<EC2_IP>* 에 넣기
   - React 앱은 FastAPI 서버와 통신을 위해 API 서버 주소를 런타임에 설정합니다.  
  - 이를 위해 React 앱은 `env.js` 파일을 사용하며, 해당 파일에는 현재 EC2의 퍼블릭 IPv4 주소를 명시해야 합니다.   
  - 따라서 특히 EC2가 끊기거나 재실행되었다면 이 부분을 수정해주어야 리액트가 제대로 실행됩니다.
  - 또한 FastAPI는 포트 8000을, React 앱은 포트 3000을 이용하므로 EC2 보안 그룹 포트 8000번과 3000번을 반드시 허용해야 합니다.  

**[EC2 보안 그룹 인바운드 규칙 설정 예시]**

| 유형       | 프로토콜 | 포트 범위 | 소스      | 설명                                                                    |
| ---------- | -------- | --------- | --------- | ----------------------------------------------------------------------- |
| Custom TCP | TCP      | 3000      | 0.0.0.0/0 | React 접속 허용 <br> (사용자가 웹앱에 접속하기 위한 포트)               |
| Custom TCP | TCP      | 8000      | 0.0.0.0/0 | FastAPI API 요청 허용 <br> (React 앱이 백엔드 API를 호출하기 위한 포트) |



**3.** 명령어 실행
```bash
# '모델 학습 및 추론', 'FastAPI', 'React'에 해당하는 이미지를 다운로드
docker pull jkim1209/mlops-model:1.4.4
docker pull jkim1209/mlops-api:1.3.4
docker pull jkim1209/mlops-frontend:1.2.0

# PostgreSQL 네트워크 생성 (처음 한 번만 필요)
docker network create my-mlops-network

# PostgreSQL DB 생성
docker run -d \
  --name my-mlops-db \
  --network my-mlops-network \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=root \
  -p 5432:5432 \
  postgres:13

# 모델 학습 및 추론 컨테이너 실행 (실행 후 컨테이너는 중지)
docker run -it \
  --name my-mlops-model \
  --network my-mlops-network \
  --env-file .env \
  jkim1209/mlops-model:1.4.4 \
  python scripts/main.py all movie_predictor

# FastAPI 컨테이너 실행 (백그라운드)
docker run -it -d \
  --name my-mlops-api \
  --network my-mlops-network \
  -p 8000:8000 \
  --env-file .env \
  jkim1209/mlops-api:1.3.4

# React 컨테이너 실행 (백그라운드)
docker run -it -d \
  --name my-mlops-frontend \
  --network my-mlops-network \
  -p 3000:3000 \
  -v $(pwd)/env.js:/usr/share/nginx/html/env.js \
  jkim1209/mlops-frontend:1.2.0
```

## 주요 포트
> PostgreSQL: `5432`    
> FastAPI : `8000`  
> React : `3000` 


## 리액트주소
```html
http://<EC2_IP>:3000
```