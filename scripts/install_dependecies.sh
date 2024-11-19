#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx
python3 -m venv /home/ec2-user/myflaskapp/venv
source /home/ec2-user/myflaskapp/venv/bin/activate
pip install -r /home/ec2-user/requirements.txt
deactivate
