default_config = {
    'default_db': {
        'database': 'complex_rest',
        'host': 'localhost',
        'user': 'complex_rest',
        'password': 'complex_rest',
        'port': '5432'
    },
    'auth_db': {
        'database': 'complex_rest_auth',
        'host': 'localhost',
        'user': 'complex_rest_auth',
        'password': 'complex_rest_auth',
        'port': '5432'
    },
    'plugins': {
        'plugins_dir': './plugins',
        'plugin_dev_dir': '../plugin_dev',
    },
    'caches': {
        'default_timeout': '300',
        'default_max_entries': '300',
        'file_cache_dir': '/tmp/complex_rest_cache',
    },
    'redis': {
        'host': 'localhost',
        'port': '6379',
        'DB': '0',
        'password': '',
    },
    'auth': {
        'period': '24',
    },
    'logging': {
        'active': 'True',
        'log_dir': './logs',
        'level': 'INFO',
        'rotate': 'True',
        'rotation_size': '10',
        'keep_files': '10'
    }
}

