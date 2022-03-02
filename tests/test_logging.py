import json
import super_logger
import sys
import manage
import shutil
import os
import importlib
import core
from django.utils.log import configure_logging
from django.test import TestCase

PLUGIN1 = 'test_logger1'
PLUGIN2 = 'test_logger2'

CONF1 = """
[logger1]
type = HR
level = DEBUG
rotation = true
message_format = [@level@] @name@ <@msg@>

[standard_attributes1]
name = name
levelname = level
module = module
filename = filename
lineno = line
funcName = func
processName = proc
process = PID
message = msg
exception = exception
created = _time
extra = extra

[logger2]
type = JSON
file = logs/test_logger1/json_test_logger1.log
level = WARNING
rotation = true

[standard_attributes2]
name = name
levelname = LVL
module = module
filename = filename
lineno = line
funcName = func
processName = proc
process = PID
message = message
exception = exception
created = _time
extra = extra

[logging]
separate_logs = DEBUG
common_logs = ERROR
"""

CONF2 = """
[logger1]
type = HR
level = DEBUG
rotation = true
message_format = [@level@] !@name@! <@msg@>

[standard_attributes1]
name = name
levelname = level
module = module
filename = filename
lineno = line
funcName = func
processName = proc
process = PID
message = msg
exception = exception
created = _time
extra = extra

[logger2]
active = false
type = JSON
file = logs/test_logger2/json_test_logger2.log
level = INFO
rotation = true

[standard_attributes2]
name = name
levelname = LVL
module = module
filename = filename
lineno = line
funcName = func
processName = proc
process = PID
message = message
exception = exception
created = _time
extra = extra

[logging]
separate_logs = INFO
common_logs = CRITICAL
"""

HR_SEPARATE1 = """[DEBUG] test_logger1 <ladybug 1 10>
[INFO] test_logger1 <ladybug 1 20>
[WARNING] test_logger1 <ladybug 1 30>
[ERROR] test_logger1 <ladybug 1 40>
[CRITICAL] test_logger1 <ladybug 1 50>"""

HR_SEPARATE2 = """[INFO] !test_logger2! <ladybug 2 20>
[WARNING] !test_logger2! <ladybug 2 30>
[ERROR] !test_logger2! <ladybug 2 40>
[CRITICAL] !test_logger2! <ladybug 2 50>"""

HR_COMMON0 = """|test_logger1| <ladybug 1 40>"""
HR_COMMON1 = """|test_logger1| <ladybug 1 50>"""
HR_COMMON2 = """|test_logger2| <ladybug 2 50>"""


def overwrite_config(plugin_name, addition):
    file_path = f'plugin_dev/{plugin_name}/{plugin_name}/{plugin_name}.conf'
    with open(file_path, 'r') as config_file:
        # remove logging section from default file
        for i in range(9):
            config_file.readline()
        tmp = config_file.read()
    with open(file_path, 'w') as config_file:
        config_file.write(tmp)
        config_file.write(addition)


class LoggingTestCase(TestCase):

    def setUp(self) -> None:
        # create plugins
        sys.argv = ['__main__.py', 'createplugin', PLUGIN1]
        manage.main()
        sys.argv = ['__main__.py', 'createplugin', PLUGIN2]
        manage.main()
        # change configurations
        overwrite_config(PLUGIN1, CONF1)
        overwrite_config(PLUGIN2, CONF2)
        # make django re-read setup.py
        importlib.reload(core.settings.base)
        configure_logging(core.settings.base.LOGGING_CONFIG, core.settings.base.LOGGING)

    def test_plugin_logging(self):
        logger1 = super_logger.getLogger(PLUGIN1)
        logger2 = super_logger.getLogger(PLUGIN2)
        logger1.debug('ladybug', 1, 10)
        logger1.info('ladybug', 1, 20)
        logger1.warning('ladybug', 1, 30)
        logger1.error('ladybug', 1, 40)
        logger1.critical('ladybug', 1, 50)
        logger2.debug('ladybug', 2, 10)
        logger2.info('ladybug', 2, 20)
        logger2.warning('ladybug', 2, 30)
        logger2.error('ladybug', 2, 40)
        logger2.critical('ladybug', 2, 50)
        # HR
        # check separate logs
        with open('logs/test_logger1/test_logger1.log') as file:
            hr_logs1 = file.read().strip()
        self.assertEqual(hr_logs1, HR_SEPARATE1)
        with open('logs/test_logger2/test_logger2.log') as file:
            hr_logs2 = file.read().strip()
        self.assertEqual(hr_logs2, HR_SEPARATE2)
        # check common logs
        with open('logs/hr_rest.log') as file:
            hr_logs = file.read().strip()
        self.assertEqual(HR_COMMON0 in hr_logs, True)
        self.assertEqual(HR_COMMON1 in hr_logs, True)
        self.assertEqual(HR_COMMON2 in hr_logs, True)
        # JSON
        # check separate logs
        self.assertEqual(os.path.isfile('logs/test_logger2/json_test_logger2.log'), False)  # TODO INVESTIGATE
        json_logs = []
        with open('logs/test_logger1/json_test_logger1.log') as file:
            json_logs.append(json.loads(file.readline()))
            json_logs.append(json.loads(file.readline()))
            json_logs.append(json.loads(file.readline()))
        for l in json_logs:
            # remove what can change
            l.pop("_time")
            l.pop('PID')
        self.assertEqual(json_logs[0], {"message": "ladybug 1 30", "proc": "MainProcess", "filename": "None", "func": "None", "LVL": "WARNING", "module": "None", "extra": {}, "name": "test_logger1", "line": 0})
        self.assertEqual(json_logs[1], {"message": "ladybug 1 40", "proc": "MainProcess", "filename": "None", "func": "None", "LVL": "ERROR", "module": "None", "extra": {}, "name": "test_logger1", "line": 0})
        self.assertEqual(json_logs[2], {"message": "ladybug 1 50", "proc": "MainProcess", "filename": "None", "func": "None", "LVL": "CRITICAL", "module": "None", "extra": {}, "name": "test_logger1", "line": 0})
        with open('logs/json_rest.log') as file:
            json_logs = file.read()
        self.assertEqual('"message": "ladybug 1 30"' in json_logs, False)
        self.assertEqual('"message": "ladybug 1 40"' in json_logs, True)
        self.assertEqual('"message": "ladybug 1 50"' in json_logs, True)


    def tearDown(self) -> None:
        # remove plugins
        shutil.rmtree('plugin_dev/test_logger1')
        shutil.rmtree('plugin_dev/test_logger2')
        os.remove('plugins/test_logger1')
        os.remove('plugins/test_logger2')
        os.remove('logs/hr_rest.log')
        os.remove('logs/json_rest.log')
        shutil.rmtree('logs/test_logger1')
        shutil.rmtree('logs/test_logger2')
