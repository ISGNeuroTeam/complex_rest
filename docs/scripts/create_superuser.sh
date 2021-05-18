#!/bin/bash

cd `dirname "${BASH_SOURCE[0]}"`
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', '', 'admin')" | ../../venv/bin/python ../../complex_rest/manage.py shell