#!/bin/bash

# use this script to set SECRET_KEY variable
# source generate_django_secret_key.sh

CUR_DIR=$(pwd)
cd `dirname "${BASH_SOURCE[0]}"`
export SECRET_KEY=$(../../venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
cd $CUR_DIR