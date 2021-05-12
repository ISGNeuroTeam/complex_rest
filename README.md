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
After restarting complex_rest server open http://localhost:8080/<plugin_name>/example/  
You must see:  
```json
{
    "message": "plugin with name <plugin_name> created successfully"
}
```

## Running the tests

```bash
source ./venv/bin/activate
python ./complex_rest/manage.py test ./tests/
```

## Deployment


## Built With


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

