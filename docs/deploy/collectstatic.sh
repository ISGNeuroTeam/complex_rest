cd `dirname "${BASH_SOURCE[0]}"`

source ./venv/bin/activate

python ./complex_rest/manage.py collectstatic
