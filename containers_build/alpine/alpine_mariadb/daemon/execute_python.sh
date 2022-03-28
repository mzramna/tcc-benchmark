#!/bin/sh
if ! command -v python3 &> /dev/null ; then
    if [[ $( grep '^ID' /etc/os-release) == "ID=alpine" ]] ; then
        apk add py3-setuptools py3-pip py3-virtualenv --no-cache --upgrade python3-dev

    elif [[ $( grep '^ID' /etc/os-release) == "ID=debian" ]] ; then
        apt install python3-venv python3-pip python3-setuptools -y python3-dev
        apt clean
    fi
fi
if ! [[ -d "/daemon/venv" ]] ; then
    python3 -m venv /daemon/venv
    source /daemon/venv/bin/activate
    pip install -r /daemon/requiriments.txt
    
fi
cd /daemon
source /daemon/venv/bin/activate
python3 /daemon/daemon_monitor.py &