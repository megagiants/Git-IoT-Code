#!/bin/bash
# Create Gunicorn systemd service file
cat <<EOL > /etc/systemd/system/gunicorn.service
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
EOL

# Update Nginx main configuration
sudo sed -i 's/listen 80;/listen 81;/g' /etc/nginx/nginx.conf
sudo sed -i '/http {/a\\    server_names_hash_bucket_size 128;' /etc/nginx/nginx.conf

# Create Flask-specific Nginx config
cat <<EOL > /etc/nginx/conf.d/flask_app.conf
server {
    listen 81;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:1212;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
}
EOL