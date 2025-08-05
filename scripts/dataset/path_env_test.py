import os
import pandas as pd

def load_data():
    """
    paths.env에 정의된 DATA_RAW_DIR 환경 변수를 사용해
    data/raw 폴더의 파일들을 로드하는 함수
    """
    # 1. os.getenv()를 사용해 환경 변수 값을 가져옵니다.
    raw_path = os.getenv('DATA_RAW_DIR')

    # 2. 환경 변수가 설정되지 않았을 경우를 대비한 예외 처리
    if not raw_path:
        print("🚨 에러: DATA_RAW_DIR 환경 변수가 설정되지 않았습니다.")
        print("터미널에서 'source .paths/paths.env' 명령어를 먼저 실행해주세요.")
        return

    print(f"✅ 환경 변수에서 경로를 찾았습니다: {raw_path}")

    # 3. os.path.join()으로 전체 파일 경로를 안전하게 생성합니다.
    csv_file_path = os.path.join(raw_path, 'raw_data_20250730035632.csv')
    parquet_file_path = os.path.join(raw_path, 'watch_logs_20250730075747.parquet')

    try:
        # 4. pandas로 데이터 불러오기
        print(f"\n📄 '{csv_file_path}' 파일 로딩 중...")
        csv_df = pd.read_csv(csv_file_path)
        print("--- CSV 데이터 ---")
        print(csv_df.head())

        print(f"\n📄 '{parquet_file_path}' 파일 로딩 중...")
        # parquet 파일을 읽으려면 pyarrow 라이브러리가 필요할 수 있습니다. (pip install pyarrow)
        parquet_df = pd.read_parquet(parquet_file_path)
        print("--- Parquet 데이터 ---")
        print(parquet_df.head())

    except FileNotFoundError as e:
        print(f"🚨 에러: 파일을 찾을 수 없습니다. 경로를 확인해주세요. {e}")

if __name__ == '__main__':
    load_data()