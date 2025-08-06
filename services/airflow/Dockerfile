# Dockerfile
# Airflow 공식 이미지를 기반으로 필요한 라이브러리를 추가하는 Dockerfile

# Airflow 공식 이미지 사용
FROM apache/airflow:2.8.2

# requirements.txt 파일을 복사하기 위해 일시적으로 root 사용자로 전환
USER root
COPY requirements.txt .

# pip install은 airflow 사용자로 실행
USER airflow
RUN pip install --no-cache-dir -r requirements.txt \
 && pip check
