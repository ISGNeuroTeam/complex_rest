#!/bin/bash

sudo -u postgres psql << EOF
create user complex_rest with password 'complex_rest';
create user complex_rest_auth with password 'complex_rest_auth';
EOF

