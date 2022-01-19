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
mkdir -p ./logs/complex_rest
mkdir -p ./logs/celery
mkdir -p ./logs/zookeeper
mkdir -p ./logs/kafka
mkdir -p ./logs/postgres

mkdir -p ./deploy_state

touch ./deploy_state/supervisord-control.sock


export PYTHONPATH=$PYTHONPATH:./complex_rest
python ./docs/deploy/make_supervisor_config.py ./docs/deploy/supervisord_base_dev.conf


supervisord -c ./supervisord.conf
supervisorctl status