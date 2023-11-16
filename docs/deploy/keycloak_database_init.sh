#! /bin/bash

source ./venv/bin/activate

export PGUSER=postgres
export PGPASSWORD=$(cat ./postgres_config/postgres_password)
export PGPORT=5433


pg_ctl -D complex_rest_db -l ./logs/postgres/stderr.log start

# create users for complex_rest
psql -U postgres << EOF
create user keycloak with password 'keycloak';
EOF

# create database
psql << EOF
create database keycloak with encoding 'UTF8';
grant all privileges on database keycloak to keycloak;
EOF

./venv/apps/keycloak-22.0.5/bin/kc.sh build
./venv/apps/keycloak-22.0.5/bin/kc.sh import --optimized --dir ./venv/apps/keycloak-22.0.5/keycloak_initial_realm_config

pg_ctl -D ./complex_rest_db stop
