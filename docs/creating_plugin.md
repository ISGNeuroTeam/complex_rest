# Creating plugin
Instructions for creating plugin

## Prerequisites
1. python 3.9.7
2. [git](https://git-scm.com/)
3. [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
4. [Conda-Pack](https://conda.github.io/conda-pack)

## Creating plugin

### Generate plugin template
1. Deploy complex rest as described in "Getting started" section in [Readme](Readme.md)
2. Create plugin template:  
```bash
python ./complex_rest/manage.py createplugin <plugin_name>
```
Your plugin start template will be available in `./plugin_dev/<plugin_name>`. Open it in your favorite IDE. Add `./complex_rest/complex_rest` directory to python paths in your IDE for syntax highlighting and hints.   
After restarting complex_rest server open http://localhost:8080/<plugin_name>/v1/example/
You must see:  

```json
{
    "message": "plugin with name <plugin_name> created successfully"
}
```
3. Initialize git repository:  
```bash
git init
```
4. Create virtual environment for the plugin and install packages you need, list all packages in `requirements.txt`. Example:  
```bash
cd ./plugin_dev/<plugin_name>
python3 -m venv ./venv
source ./venv/bin/activate
pip install <package_name1>
pip install <package_name2>
...
pip freeze > requirements.txt
```

### Make requests handlers (views)
1.  Create subclass of `rest.views.APIView`.
In views directory create new python file with subclass of `rest.views.APIView`:  
```python
from rest.views import APIView
class ExampleView(APIView):
    pass
```

2. Define `http_method_names` class attribute as list of acceptable http methods. Example:  
```python
class ExampleView(APIView):
    http_method_names = ['get', 'post']
```
3. Define `permission_classes` class attribute as tuple of permissions classes. Available classes are:  
	- AllowAny - access for everyone
	
	- IsAuthenticated - only for authenticated users
	
	- IsAdminUser - only for superusers
	
	- IsAuthenticatedOrReadOnly - read access for everyone and write access for authenticated users
	Example:  
```python
from rest.permissions import IsAuthenticated
class ExampleView(APIView):
    permission_classes = (IsAuthenticated, )
```
4. Write http metod handler. Each http mehthod handler gets request object as first argument and must return response object. To get url params in get method use `request.GET` dictionary. To get body params use `request.data` dictionary.  
Response object takes two initial arguments: data and http status code. Example:  
```python
from rest.response import Response, status
class ExampleView(APIView):
    def post(self, request):
        body_param1 = request.data['param1']
        body_param2 = request.data['param2']
        # do some logic here
        return Response(
            {
                'message': 'Hello world',
            },
            status.HTTP_200_OK
        )
```
### urls.py
In `urls.py` define `urlpatterns` variable as list of `path` objects. Path objects maps url patterns to views.
```python
from rest.urls import path
from .views.example import ExampleView
from .views.hello import HelloView
from .views.int_path_ex import NumberPath

urlpatterns = [
    path('example/', ExampleView.as_view()),
    path('hello/', HelloView.as_view()),
    path('num/<int:number>/test/<path:some_p>/', NumberPath.as_view())
]
```
The url string may contain angle brackets (like `<number>` above) to capture part of the URL and send it as a keyword argument to the view.
```python
    def get(self, request, number, path):
        return Response(
            {
                'number': number,
                'number_type': str(type(number)),
                'path': str(path),
                'path_type': str(type(path))
            },
            status.HTTP_200_OK
        )
```
Captured values can optionally include a converter type. For example, use `<int:name>` to capture an integer parameter. If a converter isn’t included, any string, excluding a / character, is matched.  
For more information see [django urls](https://docs.djangoproject.com/en/3.2/topics/http/urls/)

### Setup.py
In setup.py define author name, email, plugin api version and other variables. Example:  
```python
__author__ = "Ivanov Ivan"
__copyright__ = "Copyright 2021, ISGNeuro"
__credits__ = []
__license__ = ""
__version__ = "0.0.1"
__api_version__ = "1"
__maintainer__ = "Ivanov Ivan"
__email__ = "iivanov@isgneuro.com"
__status__ = "Develop"
```
### Plugin logger
There is a [python logger](https://docs.python.org/3/library/logging.html) created for every plugin with the same name. Use it:  
```python
import logging
log = logging.getLogger('<plugin_name>')
log.info('plugin works')
```

### Caches

#### Cache types
Four caches available:  
1. RedisCache - cache in redis. Common cache for all worker  processes on all hosts if they are configured to connect to the same redis server.
2. DatabaseCache - cache in database. Common cache for all worker processes. 
3. FileCache - cache in files. Common cache for worker process on the same host.
4. LocMemCache - cache in local process memory. Each worker process has it's own cache.

#### Get cache object
To get cache object use `get_cache` function, first argument is cache type:  
```python
from cache import get_cache
c = get_cache('RedisCache')
```
To get cache object with namespace:  
```python
c = get_cache('RedisCache', namespace='mynamespace')
```
Define  cache `max_entries` and `timeout` if you need:  
```python
c = get_cache('RedisCache', namespace='mynamespace', timeout=400, max_entries=400)
```

#### Cache object functions
- `add`. Set a value in the cache if the key does not already exist. If timeout is given, use that timeout for the key; otherwise use the default cache timeout. Return True if the value was stored, False otherwise. Example:  

```python
from cache import get_cache
c = get_cache('RedisCache', namespace='mynamespace')
was_added = c.add('some_key', 'some_value', timeout=100)
```
- `set`. Set a value in the cache. If timeout is given, use that timeout for the key; otherwise use the default cache timeout.
```python
c.set('some_key', 'some_value', timeout=60)
```
- `get`. Fetch a given key from the cache. If the key does not exist, return default, which itself defaults to None.
```python
my_var = c.get('some_key', default='default_value', timeout=60)
```
- `touch`. Update the key's expiry time using timeout. Return True if successful or False if the key does not exist. 
```python
c.touch('some_key', timeout=100)
```
- `delete`. Delete a key from the cache and return whether it succeeded, failing silently.
```python
was_deleted = c.delete('some_key')
```
### Configuration
If your plugin requires any configuration do the following:  
1. Create example of  ini configuration file with name `<plugin_name>.conf.example`. Example:  
```ini
[logging]
level = INFO

[db_conf]
host = localhost
port = 5432
database = {{plugin_name}}
user = {{plugin_name}}
password = {{plugin_name}}
```
2. Define `default_ini_config` variable in `<plugin_name>/settings.py`. Example:  
```python
default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'db_conf': {
        'host': 'localhost',
        'port': '5432',
        'database':  '{{plugin_name}}',
        'user': '{{plugin_name}}',
        'password': '{{plugin_name}}'
```
To get settings in your plugin:  
```python
from plugin_name.settings import ini_config
log_level = ini_config['logging']['level']
```

### Databases
You can define django database for your plugin in settings.py. All plugin models will be saved in this database:  
```python
DATABASE = {
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": ini_config['db_conf']['database'],
        "USER": ini_config['db_conf']['user'],
        "PASSWORD": ini_config['db_conf']['password'],
        "HOST": ini_config['db_conf']['host'],
        "PORT": ini_config['db_conf']['port']
}
```
To migrate run from complex_rest root directory:  
```bash
./venv/bin/python ./complex_rest/manage.py migrate --database=<plugin_name>
```
### Additional plugin processes
If you need to launch additional processes configure `proc.conf` file for supervisor with section `[program]`. Use `%(here)s` string for current directory (where `proc.conf` located). Example:  
```ini
[program: dispatcher]
command=python -u %(here)s/dispatcher/main.py
startsecs=3
autorestart=True
autostart=True
```
`startsecs` - the total number of seconds which the program needs to stay running after a startup to consider the start successful   
`autostart`- If true, this program will start automatically when supervisord is started.  
`autorestart` - specifies if supervisord should automatically restart a process if it exits   
process stdout you wil find in `<logging directory>/<plugin name>/<program name>_stdout.log`  
process stderr in `<logging directory>/<plugin name>/<process name>_stderr.log`  

### Make tests
Make tests for your plugin in tests directory. Define subclass of `TestCase` and use `APIClient` to test api. Example:  
```python
from rest.test import TestCase, APIClient
class TestExample(TestCase):
    def setUp(self):
        """
        define instructions that will be executed before each test method
        """
        pass

    def test_hello(self):
        # How to make get requests
        client = APIClient()
        response = client.get('/{{plugin_name}}/v1/hello/')

        # checking status code
        self.assertEqual(response.status_code, 200)

        # checking body response
        message = response.data['message']
        self.assertEqual(message, 'Hello')
    def tearDown(self):
        """
        define instructions that will be executed after each test method
        """
        pass
```

## Deploying plugin
1. Create plugin archive:  
```bash
make pack
```
2. Unpack archive to complex_rest plugins directory 
