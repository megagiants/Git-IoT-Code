#!/bin/bash

# Gunicorn 서비스 파일 복사
sudo cp /home/ec2-user/app/gunicorn.service /etc/systemd/system/gunicorn.service

# 시스템 데몬 리로드 및 Gunicorn 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn