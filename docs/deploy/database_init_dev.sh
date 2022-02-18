#! /bin/bash

source ./venv/bin/activate

# create postgres database. superuser: postgres. password from postgres_password file
initdb -D ./complex_rest_db -A md5 -U postgres --pwfile=./postgres_config/postgres_password

export PGUSER=postgres
export PGPASSWORD=$(cat ./postgres_config/postgres_password)
export PGPORT=5433

cat ./postgres_config/postgresql.conf >> ./complex_rest_db/postgresql.conf

mkdir -p ./logs/postgres
pg_ctl -D complex_rest_db -l ./logs/postgres/stderr.log start

# create users for complex_rest
psql -U postgres << EOF
create user complex_rest with password 'complex_rest';
create user complex_rest_auth with password 'complex_rest_auth';
EOF

# create database

psql << EOF
create database complex_rest;
grant all privileges on database complex_rest to complex_rest;
create database complex_rest_auth;
grant all privileges on database complex_rest_auth to complex_rest_auth;
EOF



# to ensure that plugins not loaded
export COMPLEX_REST_PLUGIN_NAME=complex_rest

# django migrations
./venv/bin/python ./complex_rest/manage.py migrate --database=auth_db
./venv/bin/python ./complex_rest/manage.py migrate
./venv/bin/python ./complex_rest/manage.py createcachetable --database=auth_db
./venv/bin/python ./complex_rest/manage.py createcachetable


# create django superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', '', 'admin')" | ./venv/bin/python ./complex_rest/manage.py shell

# stop database
pg_ctl -D ./complex_rest_db stop
