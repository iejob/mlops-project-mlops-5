global:
  resolve_timeout: 5m  # 알람(에러상황)이 resolved 상태로 바뀐 후, 해제 처리까지 대기 시간

route:
  group_by: ['severity', 'alertname']
  group_wait: 1s
  group_interval: 5s
  repeat_interval: 5m
  receiver: 'slack-warning'
  routes:
    # error - 즉시 발송
    - match:
        severity: critical
      group_wait: 1s
      group_interval: 1s
      repeat_interval: 30m
      receiver: 'slack-error'
    
    # warning
    - match:
        severity: warning
      group_wait: 10s
      group_interval: 30s  
      repeat_interval: 1h
      receiver: 'slack-warning'

receivers:
  - name: slack-error
    slack_configs:
      - channel: '#error-alerts'     # error 전용 Slack 채널
        send_resolved: true
        username: 'MonitoringBot'
        title: '{{ .CommonAnnotations.summary }}'
        text: |
          🚨 *[ERROR]*
          {{ .CommonAnnotations.description }}
        
          *상세 정보:*
          • 🖥️ *host*: {{ .CommonLabels.host }}
          • 📋 *filename*: {{ .CommonLabels.filename }}
        api_url: '${WEBHOOK_ERROR_URL}'

  - name: slack-warning
    slack_configs:
      - channel: '#warning-alerts'   # warning 전용 Slack 채널
        send_resolved: true
        username: 'MonitoringBot'
        title: '{{ .CommonAnnotations.summary }}'
        text: |
          ⚠️ *[WARNING]* 
          {{ .CommonAnnotations.description }}
        
          *상세 정보:*
          • 🖥️ *host*: {{ .CommonLabels.host }}
          • 📋 *filename*: {{ .CommonLabels.filename }}
        api_url: '${WEBHOOK_WARN_URL}'
