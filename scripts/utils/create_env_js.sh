#!/bin/bash

# .env 파일에서 환경변수 로드
source .env

# env.js 파일 생성 (환경변수 치환)
cat <<EOF > ./env.js
window._env_ = {
  REACT_APP_API_ENDPOINT: "http://${SERVER_1_IP}:3000"
};
EOF
