import os

from django.test import TestCase
from make_supervisor_config import *


class TestCreateEnvironmentValue(TestCase):
    def test_get_pythonpath_from_environment(self):
        environment = f'KEY1=12, PYTHONPATH="/tmp{os.pathsep}/home/test"'
        pythonpath = get_pythonpath_from_environment(environment)
        self.assertEqual(pythonpath, f'/tmp{os.pathsep}/home/test')

        environment = f'KEY1=12, PYTHONPATH   = "/tmp{os.pathsep}/home/test"'
        pythonpath = get_pythonpath_from_environment(environment)
        self.assertEqual(pythonpath, f'/tmp{os.pathsep}/home/test')

    def test_replace_pythonpath_in_environment(self):
        environment = f'KEY1=12, PYTHONPATH="/tmp{os.pathsep}/home/test"'

        new_environment = replace_pythonpath_in_environment(environment, f"/tmp2{os.pathsep}/home/test2")
        new_pythonpath = get_pythonpath_from_environment(new_environment)
        self.assertEqual(new_pythonpath, f"/tmp2{os.pathsep}/home/test2")

    def test_create_environment_pythonpath_with_existing_pythonpath(self):
        environment = f'KEY1=12, PYTHONPATH="/tmp{os.pathsep}/home/test"'
        new_environment = create_environment_value_for_plugin_proc_config(environment)
        new_pythonpath = get_pythonpath_from_environment(new_environment)
        paths = new_pythonpath.split(os.pathsep)
        self.assertTrue(paths[2].endswith('complex_rest'))
        self.assertTrue(paths[3].endswith('plugins'))
