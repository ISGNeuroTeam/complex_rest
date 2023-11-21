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
mkdir -p ./logs/nginx-unit
mkdir -p ./logs/celery
mkdir -p ./logs/zookeeper
mkdir -p ./logs/kafka
mkdir -p ./logs/postgres
mkdir -p ./logs/keycloak

mkdir -p ./deploy_state
mkdir -p ./deploy_state/tmp

touch ./deploy_state/supervisord-control.sock

export PYTHONPATH=$PYTHONPATH:./complex_rest
python make_supervisor_config.py
python make_nginx_unit_config.py


supervisord -c ./supervisord.conf
supervisorctl status