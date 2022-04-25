# Complex Rest

OT Platform REST API 2.0. 

## Getting Started

### Deploy on host machine
####  Prerequisites
You need:  
* python 3.9.7
* [postgresql server 12.9](https://www.postgresql.org/download/linux/)
* [redis-server](https://redis.io/download)
* [kafka 3.0.0](https://kafka.apache.org/quickstart)
* [JDK 11](https://openjdk.java.net/projects/jdk/11/) for kafka (with jdk 8 also works)
* postgresql libraries and headers for C language backend development
```bash
yum install postgresql-server, postgresql-devel
postgresql-setup --initdb
systemctl enable postgresql.service
systemctl start postgresql.service
```
#### Deploy
1. Install virtual environment from requirements.txt:  
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt
```
2. Create users and databases:  
```bash
./docs/scripts/create_db_users.sh
./docs/scripts/create_db.sh
```
3. Make migrations:  
```bash
./docs/scripts/migrations.sh
```
4. Create admin user:  
```bash
python ./complex_rest/manage.py createsuperuser --database=auth_db
```
5. Launch redis server:  
```bash
redis-server --daemonize yes
```
6. Launch celery workers:  
```bash
./docs/scripts/start_celery.sh
```
7. Launch kafka.  
8. Launch complex rest server:  
```bash
source ./venv/bin/activate
python ./complex_rest/manage.py runserver [::]:8080
```
9. Configure rest.conf:  
```bash
cp ./complex_rest/rest.conf.example ./complex_rest/rest.conf
```
### Deploy complex rest with conda
####  Prerequisites
1. [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. [Conda-Pack](https://conda.github.io/conda-pack)
#### Deploy
1. Create virtual environment for project:  
```bash
make dev
```
2. To activate virtual environment:  
```bash
source ./venv/bin/activate
```
3. Launch services:  
```bash
./start.sh
```
4. Check `localhost:8080/admin`. Login: `admin`, password `admin`  
5. Use `supervisorctl`  to manage services:  
```bash
supervisorctl status
celery-beat                      RUNNING   pid 74381, uptime 0:01:57
celery-worker                    RUNNING   pid 74383, uptime 0:01:57
complex_rest                     RUNNING   pid 74388, uptime 0:01:57
kafka                            RUNNING   pid 75911, uptime 0:01:33
postgres                         RUNNING   pid 74379, uptime 0:01:57
redis                            RUNNING   pid 74380, uptime 0:01:57
zookeeper                        RUNNING   pid 74382, uptime 0:01:57
```
6. For testing:  
```bash
make dev_test
```

### Deploy with docker 
#### Prerequisites
1. [Docker](https://docs.docker.com/engine/install/).   
[Manage Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/)
2. [Docker compose](https://docs.docker.com/compose/install/)
#### Deploy
```bash
CURRENT_UID=$(id -u):$(id -g) docker-compose -f "docker-compose-dev.yml" up -d --build
```

### Create your plugin
```bash
python ./complex_rest/manage.py createplugin <plugin_name>
```
Your plugin start template will be available in ./plugin_dev/<plugin_name>  
After restarting complex_rest server open http://localhost:8080/<plugin_name>/v1/example/
You must see:  
```json
{
    "message": "plugin with name <plugin_name> created successfully"
}
```
See [creating plugin](docs/creating_plugin.md)

## Running the tests
### On host machine
```bash
source ./venv/bin/activate
python ./complex_rest/manage.py test ./tests/ --settings=core.settings.test
```
### With conda
```
make dev_test
```
### With docker-compose
```bash
docker-compose -f docker-compose-dev.yml run --rm  complex_rest python ./complex_rest/manage.py test ./tests --settings=core.settings.test
```

## Deployment
1. Unpack tar archive to destination directory
2. Make database:  
```bash
./database_init.sh
```
3. Run `start.sh`

## Updating
1. Stop complex_rest
```bash
./stop.sh
```
2. Unpack tar archive to destination directory excluding any configuration files that have been changed. Example:
```bash
tar -xzf complex_rest.tar.gz -C /opt/otp/ --exclude=complex_rest/complex_rest/rest.conf --exclude=complex_rest/complex_rest/nginx_unit.json
```
3. Start complex rest
```bash
./start.sh
```
4. Do migrations:
```bash
./venv/bin/python ./complex_rest/manage.py migrate --database=auth_db
./venv/bin/python ./complex_rest/manage.py migrate
```


## Built With
- Conda
- Postgres 12.9
- Kafka 3.0.0
- Redis
- python 3.9.7
And python packages:
- Django 3.2.9
- psycopg2-binary 2.9.2
- djangorestframework 3.12.4
- pottery 2.0.0
- django-redis 5.0.0
- redis 4.0.2
- celery 5.2.1
- django-celery-beat 2.2.1
- aiokafka 0.7.2
- kafka-python 2.0.2
- supervisor 4.2.2
- django-mptt 0.13.4
- PyJWT 2.3.0

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## License

See the [LICENSE.md](LICENSE.md) file for details
