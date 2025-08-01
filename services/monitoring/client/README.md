# Monitoring Client
- `Prometheus`가 metrics 를 스크랩 할 수 있도록 `FastAPI`를 통해 `/metrics` 엔드포인트 제공
- `node-exporter`를 통해 서버 상태 모니터링


## 구성요소

### monitoring-app
  FastAPI 기반 애플리케이션으로, 메트릭 수집을 위한 엔드포인트를 제공하고, `/metrics` 엔드포인트를 통해 Prometheus가 스크랩하여 데이터를 수집할 수 있게 합니다.
  
  포트번호 : `8000`

### node-exporter
  Prometheus가 리눅스 서버의 CPU, 메모리, 디스크, 네트워크 등 시스템 자원 상태를 수집할 수 있도록  메트릭 정보를 제공하는 에이전트입니다.

  포트번호 : `9100`(기본)