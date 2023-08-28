#!/bin/sh

/opt/keycloak/bin/kc.sh import --dir /opt/keycloak/realm_config
exec "$@"