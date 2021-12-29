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

supervisorctl stop all
kill `cat ./deploy_state/supervisord.pid`
rm ./deploy_state/supervisord-control.sock
