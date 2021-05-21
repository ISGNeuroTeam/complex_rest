# Complex Rest

OT Platform REST API 2.0. 

## Getting Started

Configure database, launch redis-server, make migrations

### Prerequisites

You need:  
* [postgresql server](https://www.postgresql.org/download/linux/)
* [redis-server](https://redis.io/download)
* postgresql libraries and headers for C language backend development
```bash
yum install postgresql-server, postgresql-devel
postgresql-setup --initdb
systemctl enable postgresql.service
systemctl start postgresql.service
```

### Installing
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
4. Launch redis server:  
```bash
redis-server --daemonize yes
```
5. Make migrations:  
```bash
./docs/scripts/migrations.sh
```
6. Launch complex rest server:  
```bash
source ./venv/bin/activate
python ./complex_rest/manage.py runserver [::]:8080
```
7. Create admin user:  
```bash
python ./complex_rest/manage.py createsuperuser --database=auth_db
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

## Running the tests

```bash
source ./venv/bin/activate
python ./complex_rest/manage.py test ./tests/ --settings=core.settings.test

```

## Deployment
1. Unpack tar archive to destination directory
2. Create default database and database user for it. Example:  
```SQL
create user complex_rest with password 'complex_rest';
create database complex_rest;
grant all privileges on database complex_rest to complex_rest;
```
3. Create  database for user administration and authentication and user for that database. Example:  
```SQL
create user complex_rest_auth with password 'complex_rest_auth';
create database complex_rest_auth;
grant all privileges on database complex_rest_auth to complex_rest_auth;
```
4. Configure sections `[auth_db]` and `[default_db]`  for created databases in `rest.conf`. Example:  
```ini
[default_db]
host = localhost
database = complex_rest
user = complex_rest
password = complex_rest
port = 5432

[auth_db]
host = localhost
database = complex_rest_auth
user = complex_rest_auth
password = complex_rest_auth
port = 5432
```
5. Run redis server. Example:
```bash
redis-server --daemonize yes
```
6. Configure section `[redis]` in `rest.conf` for redis usage. Example:  
```ini
host = localhost
port = 6379
DB = 0
password =
```
7. Make migrations (create all necessary tables):  
```bash
./venv/bin/python ./manage.py migrate --database=auth_db --settings=core.settings.base
```
```bash
./venv/bin/python ./manage.py migrate --settings=core.settings.base
```
8. Create cache tables in databases:  
```bash
./venv/bin/python ./manage.py createcachetable --database=auth_db --settings=core.settings.base
```
```bash
./venv/bin/python ./manage.py createcachetable --settings=core.settings.base
```
9. Create admin user:  
```bash
./venv/bin/python ./manage.py createsuperuser --database=auth_db
```
10. Create user for launching server. Make sure he has access  to application directory, logging directory and plugin directory. Example:  
```bash
useradd complex_rest
chown -R complex_rest:complex_rest /opt/otp/complex_rest
```
11. Create json config for nginx-unit. Example:  
```json
{
    "listeners": {
        "*:50000": {
            "pass": "applications/complex_rest"
        }
    },

    "applications": {
        "complex_rest": {
            "user": "complex_rest",
            "group": "complex_rest",
            "type": "python 3.8",
            "home": "/opt/otp/complex_rest/venv/",
            "path": "/opt/otp/complex_rest",
            "working_directory": "/opt/otp/complex_rest",
            "module": "core.wsgi",
            "environment": {
                "DJANGO_SETTINGS_MODULE": "core.settings"
            },
            "limits": {
                "timeout": 60
            },
            "processes": 10
        }
    }
}
```
11. Configure nginx-unit. Example:  
```bash
curl -X PUT --data-binary @nginx-unit.json --unix-socket /run/control.unit.sock http://localhost/config/
```


## Built With


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

