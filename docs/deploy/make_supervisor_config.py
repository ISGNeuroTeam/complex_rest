import sys
import configparser
import re
import os

from pathlib import Path
from core.settings import BASE_DIR, LOG_DIR, PLUGINS_DIR

# first argument is supervisor_base.conf location
if len(sys.argv) > 1:
    supervisor_base_conf_path = sys.argv[1]
else:
    supervisor_base_conf_path = 'supervisord_base.conf'

# second argument is supervisord.conf location
if len(sys.argv) > 2:
    supervisord_conf_path = sys.argv[2]
else:
    supervisord_conf_path = 'supervisord.conf'


def main():
    """
    Reads supervisord_base.conf, plugins proc.conf files
    and creates supervisord.conf with plugins [program:] sections
    """
    plugins_dir = Path(PLUGINS_DIR)
    # get plugins proc.conf
    plugin_dirs_with_conf_files = [
        plugin_dir
        for plugin_dir in plugins_dir.iterdir() if plugin_dir.is_dir() and (plugin_dir / 'proc.conf').exists()
    ]

    # read base config
    config = configparser.ConfigParser()
    with open(supervisor_base_conf_path, 'r') as f:
        config.read_file(f)

    # create section for every plugin process
    for plugin_dir in plugin_dirs_with_conf_files:
        plugin_name = plugin_dir.name

        plugin_proc_config = configparser.RawConfigParser()

        plugin_proc_config.read(plugin_dir / 'proc.conf')

        for section in plugin_proc_config.sections():
            if not section.startswith('program:'):
                continue

            section_name = section.split('program:')[1].strip()

            # add new section to result config
            config.add_section(section)
            for key in plugin_proc_config[section].keys():
                config[section][key] = make_interpolation(plugin_proc_config[section][key], plugin_dir)

            # add environment config
            environment = plugin_proc_config[section].get('environment', '')
            config[section]['environment'] = make_interpolation(
                create_environment_value_for_plugin_proc_config(environment),
                plugin_dir
            )

            # add stdout and stderr config
            config[section]['stdout_logfile'] = str(
                LOG_DIR / plugin_name / (section_name + '_stdout.log')
            )
            config[section]['stderr_logfile'] = str(
                LOG_DIR / plugin_name / (section_name + '_stderr.log')
            )

            # add priority config
            config[section]['priority'] = '100'

            config[section]['stopwaitsecs'] = '20'
            config[section]['stopasgroup'] = 'true'
            config[section]['killasgroup'] = 'true'

    # write supervisord config
    with open(supervisord_conf_path, 'w') as f:
        config.write(f)


def make_interpolation(value, plugin_dir):
    return value % {
        'plugin_dir': plugin_dir,
        'here': plugin_dir
    }


def create_environment_value_for_plugin_proc_config(environment=""):
    """
    Creates value environment in program section of proc.conf with PYTHONPATH="<complex_rest_dir>:<plugins_dir>"
    :param environment: current environment value, string with format: KEY1="value1",KEY2="value2"
    :return:
    environemt value with PYTHONPATH, Example:
    environment=KEY="1", PYTHONPATH="<complex_rest_dir>:<plugins_dir>"
    """
    default_python_path = f'{str(BASE_DIR)}{os.pathsep}{str(PLUGINS_DIR)}'
    if environment == "":
        return f'PYTHONPATH="{default_python_path}"'

    current_pythonpath = get_pythonpath_from_environment(environment)

    if current_pythonpath:
        return replace_pythonpath_in_environment(
            environment, f'{current_pythonpath}{os.pathsep}{default_python_path}'
        )
    else:
        return f'{environment},PYTHONPATH={default_python_path}'


PYTHON_PATH_PATTERN = re.compile(r'PYTHONPATH\s*=\s*\"(.*)\"')


def get_pythonpath_from_environment(environment):
    """
    Finds PYTHONPATH="python_dir1:python_dir2..." in environment string
    >>> environment = 'KEY1=12, PYTHONPATH="/tmp:/home/test"'
    >>> get_pythonpath_from_environment(environment)
    '/tmp:/home/test'

    :param environment: string to find PYTHONPATH
    :return:
    PYTHONPATH value
    """
    match_obj = PYTHON_PATH_PATTERN.search(environment)
    if match_obj:
        return match_obj.group(1)
    return ''


def replace_pythonpath_in_environment(environment, new_pythonpath):
    return PYTHON_PATH_PATTERN.sub(f'PYTHONPATH="{new_pythonpath}"', environment)


if __name__=='__main__':
    main()










