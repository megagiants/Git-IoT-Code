#!/bin/bash

# Nginx 설정 파일의 포트를 81로 변경
sudo sed -i 's/listen 80;/listen 81;/' /etc/nginx/nginx.conf
# server_names_hash_bucket_size 128; 추가
sudo sed -i '/http {/a\    server_names_hash_bucket_size 128;' /etc/nginx/nginx.conf
# Nginx 서비스 재시작
sudo systemctl restart nginx