#!/bin/bash

sudo -u postgres psql << EOF
create database complex_rest;
grant all privileges on database complex_rest to complex_rest;
create database complex_rest_auth;
grant all privileges on database complex_rest_auth to complex_rest_auth;
EOF
