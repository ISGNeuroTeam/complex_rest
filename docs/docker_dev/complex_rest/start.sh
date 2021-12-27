#!/bin/bash

mkdir -p ./logs/celery
mkdir -p ./logs/complex_rest
mkdir -p ./deploy_state
mkdir -p ./plugins
mkdir -p ./plugin_dev

touch ./deploy_state/supervisord-control.sock

export PYTHONPATH=$PYTHONPATH:./complex_rest
rm -f ./supervisord.conf
python /complex_rest/docs/deploy/make_supervisor_config.py /complex_rest/docs/docker_dev/complex_rest/supervisor_base.conf


supervisord -c ./supervisord.conf


