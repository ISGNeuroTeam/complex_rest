cd `dirname "${BASH_SOURCE[0]}"`
../../venv/bin/python ../../complex_rest/manage.py migrate --database=auth_db
../../venv/bin/python ../../complex_rest/manage.py migrate