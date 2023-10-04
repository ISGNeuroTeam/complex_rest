#! /bin/bash

python ./complex_rest/manage.py test ./tests --settings=core.settings.test --no-input
export REST_CONF=/complex_rest/docs/docker_dev/complex_rest/rest_test_keycloak.conf
python ./complex_rest/manage.py test test_auth.test_keycloak --settings=core.settings.test --no-input --pythonpath /complex_rest/tests
