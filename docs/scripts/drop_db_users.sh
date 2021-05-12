sudo -u postgres psql << EOF
drop user complex_rest;
drop user complex_rest_auth
EOF
