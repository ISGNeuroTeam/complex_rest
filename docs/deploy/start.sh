#!/bin/bash

cd `dirname "${BASH_SOURCE[0]}"`

echo 'Trying activate ./venv virtual environment'
source  ./venv/bin/activate

if [ $? -eq 0 ]; then
    echo Virtual environment activated
else
    echo 'Trying activate ../venv virtual environment'
    source  ../venv/bin/activate
fi

mkdir -p ./logs/redis
mkdir -p ./logs/celery
mkdir -p ./logs/nginx-unit
mkdir -p ./deploy_state

touch ./deploy_state/supervisord-control.sock

python make_supervisor_config.py


supervisord -c ./supervisord.conf
supervisorctl status