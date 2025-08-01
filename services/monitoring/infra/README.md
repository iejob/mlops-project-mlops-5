# Monitoring Infra
- Prometheus client를 통해 metric을 수집하고, Grafana를 통해 시각화 합니다.


## 구성요소

### prometheus
  `monitoring-app`의 `/metrics` 엔드포인트를 주기적으로 스크랩하여 데이터를 수집합니다.
  
  포트번호 : `9090`(기본)


### Grafana
  Prometheus에서 수집한 메트릭을 시각화합니다.
  
  포트번호 : `3000`(기본)



