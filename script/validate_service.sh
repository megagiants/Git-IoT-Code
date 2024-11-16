#!/bin/bash

# 애플리케이션 상태 확인
STATUS_CODE=$(curl -o /dev/null -s -w "%{http_code}" "ALB dns주소 넣기:81  안되면 81도 빼고 ㄱㄱ")
if [ "$STATUS_CODE" -ne 200 ]; then
  echo "Validation failed."
  exit 1
fi
echo "Validation succeeded."
exit 0