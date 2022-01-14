#!/bin/sh
if ! command -v python3 &> /dev/null;then
    if [[$( grep '^VERSION' /etc/os-release) == "ID=alpine" ]];then
        apk add py3-setuptools py3-pip python3 py3-virtualenv --no-cache

    elif [[$( grep '^VERSION' /etc/os-release) == "ID=debian" ]];then
        apt install python3-venv python3 python3-pip python3-setuptools -y
        apt clean
    fi
fi
if [[ -d "./venv" ]];then
    python3 -m venv ./venv
    source ./venv/bin/activate
    pip install -r requirements.txt
fi
source ./venv/bin/activate
python3 ./daemon_monitor.py