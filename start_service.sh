#!/bin/bash
# Reload systemd to apply Gunicorn service
sudo systemctl daemon-reload

# Restart and enable Gunicorn
sudo systemctl restart gunicorn
sudo systemctl enable gunicorn

# Restart and enable Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx