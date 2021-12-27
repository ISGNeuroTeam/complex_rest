#!/bin/sh

echo "Waiting for postgres..."
sleep 5


python ./complex_rest/manage.py flush --no-input
python manage.py migrate
python ./complex_rest/manage.py migrate --database=auth_db
python ./complex_rest/manage.py migrate
python ./complex_rest/manage.py createcachetable --database=auth_db
python ./complex_rest/manage.py createcachetable

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', '', 'admin')" | python /complex_rest/complex_rest/manage.py shell

exec "$@"