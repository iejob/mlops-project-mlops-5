# Monitoring Client
- `node-exporter`를 통해 서버의 시스템 자원을 모니터링합니다.
- `Promtail`을 통해 `logs` 디렉토리에 저장된 로그 파일을 수집합니다.


## 구성요소


### node-exporter
- Prometheus가 리눅스 서버의 CPU, 메모리, 디스크, 네트워크 등 시스템 자원 상태를 수집할 수 있도록 메트릭 데이터를 제공하는 에이전트입니다.
- 기본 포트 : `9100`


### Promtail
- 로그 파일을 감시하고 모니터링 서버 Loki HTTP API 주소를 통해 전송하는 에이전트입니다.
- 기본 포트 : `9080`