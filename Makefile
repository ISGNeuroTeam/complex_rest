#.SILENT:
SHELL = /bin/bash

.PHONY: clean clean_build clean_venv.tar.gz clean_pack clean_kafka clean_unit test docker_test clean_docker_test

all:
	echo -e "Sections:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"complex_rest_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
 dev - deploy for developing \n\
"

GENERATE_VERSION = $(shell cat setup.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')
SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

define clean_docker_containers
	@echo "Stopping and removing docker containers"
	docker-compose -f docker-compose-test.yml stop
	if [[ $$(docker ps -aq -f name=complex_rest) ]]; then docker rm $$(docker ps -aq -f name=complex_rest);  fi;
endef

pack: make_build
	$(SET_VERSION)
	$(SET_BRANCH)
	rm -f complex_rest-*.tar.gz
	echo Create archive \"complex_rest-$(VERSION)-$(BRANCH).tar.gz\"
	cd make_build; tar czf ../complex_rest-$(VERSION)-$(BRANCH).tar.gz complex_rest


clean_pack:
	rm -f complex_rest-*.tar.gz


complex_rest.tar.gz: build
	cd make_build; tar czf ../complex_rest.tar.gz complex_rest && rm -rf ../make_build


build: make_build


make_build: venv.tar.gz
	# required section
	echo make_build
	mkdir -p make_build/complex_rest

	cp -R ./complex_rest make_build/complex_rest
	cp ./docs/deploy/rest.conf make_build/complex_rest/complex_rest/rest.conf
	rm -rf make_build/complex_rest/complex_rest/plugins/plugin_example*
	cp ./docs/deploy/django_settings/production.py make_build/complex_rest/complex_rest/core/settings/production.py

	mkdir -p make_build/complex_rest/logs
	mkdir -p make_build/complex_rest/logs/redis
	mkdir -p make_build/complex_rest/logs/nginx-unit
	mkdir -p make_build/complex_rest/logs/celery
	mkdir -p make_build/complex_rest/logs/zookeeper
	mkdir -p make_build/complex_rest/logs/kafka
	mkdir -p make_build/complex_rest/logs/postgres

	mkdir -p make_build/complex_rest/plugins

	mkdir -p make_build/complex_rest/deploy_state

	cp ./docs/deploy/nginx-unit*.json make_build/complex_rest/

	touch make_build/complex_rest/deploy_state/supervisord-control.sock
	cp ./docs/deploy/*.sh make_build/complex_rest/
	cp ./docs/deploy/*.py make_build/complex_rest/
	cp ./docs/deploy/supervisord_base.conf make_build/complex_rest/supervisord_base.conf
	cp -R ./docs/deploy/postgres_config make_build/complex_rest/postgres_config
	cp ./docs/deploy/database_init.sh make_build/complex_rest/database_init.sh
	cp ./docs/deploy/collectstatic.sh make_build/complex_rest/collectstatic.sh
	mkdir make_build/complex_rest/venv
	tar -xzf ./venv.tar.gz -C make_build/complex_rest/venv

venv.tar.gz: unit/venv
	conda pack -p ./unit/venv -o ./venv.tar.gz

unit/venv: unit kafka.tar.gz
	./docs/scripts/create_conda_env_with_all_dependences.sh

unit:
	git clone --depth 1 --branch 1.27.0https://github.com/nginx/unit

kafka.tar.gz:
	curl https://archive.apache.org/dist/kafka/3.0.0/kafka_2.13-3.0.0.tgz --output kafka.tar.gz

clean_kafka:
	rm -f kafka.tar.gz

clean_unit:
	rm -rf ./unit/

clean_venv.tar.gz:
	rm -f ./venv.tar.gz

clean_build:
	rm -rf make_build

clean: clean_build clean_venv.tar.gz clean_pack clean_kafka clean_unit clean_docker_test clean_dev

test: docker_test

docker_test:
	$(call clean_docker_containers)
	@echo "Testing..."
	CURRENT_UID=$$(id -u):$$(id -g) docker-compose -f docker-compose-test.yml run --rm  complex_rest python ./complex_rest/manage.py test ./tests --settings=core.settings.test --no-input
	$(call clean_docker_containers)

clean_docker_test:
	$(call clean_docker_containers)


dev: venv logs
	mkdir -p ./plugins
	mkdir -p ./plugin_dev

	cp ./docs/deploy/start_dev.sh ./start.sh
	cp ./docs/deploy/stop.sh ./stop.sh
	cp -R ./docs/deploy/postgres_config ./postgres_config
	cp ./docs/deploy/rest_dev.conf ./complex_rest/rest.conf

	./docs/deploy/database_init_dev.sh
	touch dev


deploy_state/supervisord.pid: dev
	./start.sh
	sleep 5

dev_test: deploy_state/supervisord.pid
	./venv/bin/python ./complex_rest/manage.py test ./tests --settings=core.settings.test

logs:
	mkdir -p ./logs
	mkdir -p ./logs/redis
	mkdir -p ./logs/complex_rest
	mkdir -p ./logs/celery
	mkdir -p ./logs/zookeeper
	mkdir -p ./logs/kafka
	mkdir -p ./logs/postgres

venv: venv_dev_pack.tar.gz
	mkdir -p ./venv
	tar -xzf ./venv_dev_pack.tar.gz -C ./venv

venv_dev_pack.tar.gz: venv_dev
	conda pack -p ./venv_dev -o ./venv_dev_pack.tar.gz


venv_dev: kafka.tar.gz
	conda create --copy -p ./venv_dev -y
	conda install -p ./venv_dev python==3.9.7 -y
	conda install -p ./venv_dev redis -y
	conda install -p ./venv_dev postgresql==12.9 -y
	./venv_dev/bin/pip install --no-input  -r ./requirements.txt
	mkdir ./venv_dev/apps
	tar zxf ./kafka.tar.gz -C ./venv_dev/apps/


clean_venv:
	rm -rf ./venv
	rm -rf ./venv_dev
	rm -rf ./venv_dev_pack.tar.gz

clean_dev: clean_venv
	-./stop.sh
	rm -rf ./deploy_state
	rm -rf ./logs
	rm -rf ./postgres_config
	rm -f stop.sh
	rm -f start.sh
	rm -rf ./complex_rest_db
	rm -f ./complex_rest/rest.conf
	rm -f ./supervisord.conf
	rm -rf ./plugins
	rm -f dev



