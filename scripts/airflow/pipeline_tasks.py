import os
import requests
import json
from airflow.exceptions import AirflowException


# 서버1 FastAPI의 /health 엔드포인트를 호출하여 상태를 확인하는 함수
def check_api_health(api_base_url: str):
    """
    서버1 FastAPI의 /health 엔드포인트를 호출하여 상태를 확인합니다.
    API 서버가 정상적으로 작동하는지 확인하기 위해 사용됩니다.
    
    Args:
        api_base_url (str): FastAPI 서버의 기본 URL (예: "http://192.168.1.100:8000")
    
    Returns:
        bool: API 상태가 'ok'이면 True, 아니면 False를 반환합니다.
    """
    try:
        url = f"{api_base_url}/health" # ⬅️ API 헬스 체크 엔드포인트 URL
        response = requests.get(url, timeout=60) # 60초 타임아웃 설정
        response.raise_for_status() # HTTP 오류가 발생하면 예외를 발생시킵니다.
        
        health_status = response.json().get("status")
        if health_status == "ok":
            print(f"✅ API Health-check 성공: {response.json()}")
            return True
        else:
            # 상태가 'ok'가 아닌 경우
            print(f"🚨 API 상태가 'ok'가 아닙니다: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        # 네트워크 연결, 타임아웃 등 요청 관련 예외 처리
        print(f"🚨 API Health-check 중 네트워크 오류 발생: {e}")
        return False


# 자동화 파이프라인 태스크를 실행하는 공통 함수
def run_pipeline_task(api_base_url: str, endpoint: str, expected_result: str, payload: dict = None, **kwargs):
    """
    지정된 FastAPI 엔드포인트를 호출하고 결과를 검증하는 공통 함수.
    Airflow 태스크에서 재사용 가능한 형태로 만들어졌습니다.
    
    Args:
        api_base_url (str): FastAPI 서버의 기본 URL
        endpoint (str): 호출할 API의 특정 엔드포인트 (예: "run/prepare-data")
        expected_result (str): API 응답 JSON의 'result' 키에서 기대하는 값
        payload (dict, optional): POST 요청에 포함할 JSON 페이로드. 기본값은 None.
    
    Raises:
        AirflowException: API 호출 또는 응답 검증 중 문제가 발생하면 AirflowException을 발생시켜 태스크를 실패시킵니다.
    """
    url = f"{api_base_url}/{endpoint}" # ⬅️ 완전한 API 요청 URL 생성
    headers = {"Content-Type": "application/json"} # JSON 형식의 데이터 전송을 위한 헤더 설정
    
    print(f"🚀 API 호출 시작: {url}, 페이로드: {payload or '없음'}")
    
    # 엔드포인트에 따라 타임아웃을 다르게 설정. 'run/train'은 모델 학습으로 인해 시간이 오래 걸릴 수 있음.
    # 타임아웃을 30분으로 설정하고, 나머지는 5분으로 설정
    timeout = 3600 if endpoint == "run/train" else 300

    try:
        if payload:
            # 페이로드가 있는 경우 POST 요청 (e.g., 모델명 지정)
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
        else:
            # 페이로드가 없는 경우 POST 요청
            response = requests.post(url, headers=headers, timeout=timeout)
            
        response.raise_for_status() # HTTP 에러(4xx, 5xx)가 발생하면 예외 발생
        
        response_json = response.json()
        result = response_json.get("result")
        
        # API 응답의 'result' 값과 기대하는 값을 비교하여 성공 여부 판단
        if result == expected_result:
            print(f"✅ 태스크 성공: {response_json}")
            return response_json
        else:
            # 응답은 성공적이었으나, 내용이 기대와 다른 경우
            error_message = f"🚨 태스크 응답 검증 실패. 예상 결과: '{expected_result}', 실제 응답: {response_json}"
            print(error_message)
            raise AirflowException(error_message) # Airflow 태스크 실패 처리
            
    except requests.exceptions.HTTPError as e:
        # 4xx 또는 5xx 상태 코드 에러 처리
        error_message = f"🚨 API가 오류 응답을 반환했습니다 (HTTP Error). 상태코드: {e.response.status_code}, 응답: {e.response.text}"
        print(error_message)
        raise AirflowException(error_message)
        
    except requests.exceptions.RequestException as e:
        # 네트워크 연결, DNS 오류, 타임아웃 등 요청 관련 에러 처리
        error_message = f"🚨 API 호출 중 네트워크 오류 발생: {e}"
        print(error_message)
        raise AirflowException(error_message)
        
    except Exception as e:
        # 그 외 예기치 않은 모든 오류 처리 (e.g., JSON 파싱 오류)
        error_message = f"🚨 태스크 실행 중 예기치 않은 오류 발생: {e}"
        print(error_message)
        raise AirflowException(error_message)