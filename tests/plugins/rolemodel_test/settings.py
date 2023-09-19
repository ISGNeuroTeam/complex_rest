import configparser
import os

from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults, configparser_to_dict

default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'db_conf': {
        'host': 'localhost',
        'port': '5432',
        'database':  'rolemodel_test',
        'user': 'rolemodel_test',
        'password': 'rolemodel_test'
    }
}


# try to read path to config from environment
conf_path_env = os.environ.get('rolemodel_test_conf', None)
base_dir = Path(__file__).resolve().parent
if conf_path_env is None:
    conf_path = base_dir / 'rolemodel_test.conf'
else:
    conf_path = Path(conf_path_env).resolve()

config = configparser.ConfigParser()

config.read(conf_path)

config = configparser_to_dict(config)

ini_config = merge_ini_config_with_defaults(config, default_ini_config)

ROLE_MODEL_AUTH_COVERED_CLASSES = {
    'rolemodel_test.models.SomePluginAuthCoveredModel': [
        'test.create',
        'test.protected_action1',
        'test.protected_action2'
    ],
    'rolemodel_test.models.SomePluginAuthCoveredModelUUID': [
        'test.create',
        'test.protected_action1',
        'test.protected_action2'
    ],
}

ROLE_MODEL_ACTIONS = {
    'test.create': {
        'default_rule': True,  # allow or deny True or False, default True,
    },
    'test.protected_action1': {
            'default_rule': False,  # allow or deny True or False, default True,
    },
    'test.protected_action2': {
        'default_rule': True,  # allow or deny True or False, default True,
    },
}

# configure your own database if you need
# DATABASE = {
#         "ENGINE": 'django.db.backends.postgresql',
#         "NAME": ini_config['db_conf']['database'],
#         "USER": ini_config['db_conf']['user'],
#         "PASSWORD": ini_config['db_conf']['password'],
#         "HOST": ini_config['db_conf']['host'],
#         "PORT": ini_config['db_conf']['port']
# }

