
#.SILENT:
SHELL = /bin/bash


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"complex_rest_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv\n\
"

GENERATE_VERSION = $(shell cat setup.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')
SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))


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


make_build: venv venv_pack
	# required section
	echo make_build
	mkdir make_build

	cp -R ./complex_rest make_build
	cp make_build/complex_rest/rest.conf.example make_build/complex_rest/rest.conf
	cp *.md make_build/complex_rest/
	cp *.py make_build/complex_rest/
	rm -rf make_build/complex_rest/plugins/plugin_example*
	cp ./docs/django_settings/production.py make_build/complex_rest/core/settings/production.py
	mkdir make_build/complex_rest/venv
	mkdir -p make_build/complex_rest/logs
	mkdir make_build/complex_rest/logs/redis
	mkdir make_build/complex_rest/logs/nginx-unit
	mkdir make_build/complex_rest/logs/celery
	mkdir make_build/complex_rest/deploy_state
	cp ./docs/conf/nginx-unit.json make_build/complex_rest/deploy_state/conf.json
	touch make_build/complex_rest/deploy_state/supervisord-control.sock
	cp ./docs/deploy/* make_build/complex_rest/
	tar -xzf ./venv.tar.gz -C make_build/complex_rest/venv


clean_build:
	rm -rf make_build


venv: clean_venv
	echo Create venv
	conda create --copy -p ./venv -y
	conda install -p ./venv redis -y
	conda install -p ./venv python==3.8.5 -y
	./venv/bin/pip install --no-input  -r requirements.txt

venv_pack:
	conda pack -p ./venv -o ./venv.tar.gz


clean_venv:
	rm -rf venv
	rm -f ./venv.tar.gz


clean: clean_build clean_venv clean_pack clean_test


redis: venv
	{ ./venv/bin/redis-server & echo $$! > redis.pid; }


clean_redis:
ifneq (,$(wildcard ./redis.pid))
	kill -9 `cat redis.pid`
	rm -f redis.pid
	rm -f *.rdb
else
	@echo "Redis pid file not found"
endif


test: venv redis
	@echo "Testing..."
	./venv/bin/python ./complex_rest/manage.py test ./tests --settings=core.settings.test


clean_test: clean_redis
	@echo "Clean tests"
