#!/bin/sh
apk add py3-setuptools py3-pip python3 --no-cache
pip install -r requirements.txt
python3 ./daemon_monitor.py