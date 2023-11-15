#! /bin/bash
install_path=$1

wget -O keycloak.tar.gz "https://github.com/keycloak/keycloak/releases/download/22.0.5/keycloak-22.0.5.tar.gz"
tar -xzf keycloak.tar.gz -C $install_path