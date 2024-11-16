#!/bin/bash

# Gunicorn 서비스 파일을 /etc/systemd/system/gunicorn.service로 생성
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for Flask app
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/myflaskapp
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:1212 app:app

[Install]
WantedBy=multi-user.target
EOF

# 시스템 데몬 리로드 및 Gunicorn 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn