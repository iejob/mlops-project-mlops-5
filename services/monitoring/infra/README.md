# Monitoring Infra
- `Prometheus` 통해 메트릭 데이터를 수집하고, `Grafana`를 통해 시각화합니다.
- `Loki`를 통해 로그 데이터를 수집하고, `Grafana`에서 조회합니다.
- `Alertmanager`를 통해 `[ERROR]`, `[WARN]` 등의 로그 발생 시 `Slack`으로 알림 메시지를 전송합니다.

## 구성요소

### prometheus
- 각 컴포넌트의 `/metrics` 엔드포인트를 주기적으로 스크랩하여 메트릭 데이터를 수집합니다.
- 기본 포트 : `9090`


### Loki
- `Promtail`이 수집한 로그 데이터를 수신, 저장 및 조회가 가능하게 합니다.
- 기본 포트 : `3100`


### Alertmanager
- `Prometheus`에 정의된 알림 조건을 기반으로 상태를 감지하여 `Slack` 등 외부 알림 메시지를 전송합니다.
- 기본 포트 : `9093`


### Grafana
- `Prometheus`에서 수집한 메트릭을 시각화하고, `Loki`를 통해 수집된 로그를 조회할 수 있는 대시보드를 제공합니다.
- 기본 포트 : `3000`