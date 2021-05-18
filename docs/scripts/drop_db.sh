#!/bin/bash

sudo -u postgres psql << EOF
drop database complex_rest;
drop database complex_rest_auth
EOF
