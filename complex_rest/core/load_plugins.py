import sys
import re

from pathlib import Path
from django.utils.module_loading import import_string


def get_plugins_names(plugin_dir):
    """
    :param plugin_dir: directory with plugins
    :return:
    list with plugins names
    """
    return [full_plugin_path.name for full_plugin_path in Path(plugin_dir).iterdir()]


def add_plugins_env_dirs_to_sys_path(plugin_dir, plugins_names):
    """
    Finds and adds all plugin virtual environment directories to sys.path
    """
    # virtual environment relative paths
    venv_relative_dirs_list = [
        f'lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages',
        f'lib/python{sys.version_info.major}{sys.version_info.minor}.zip',
        f'lib/python{sys.version_info.major}.{sys.version_info.minor}',
        f'lib/python{sys.version_info.major}.{sys.version_info.minor}/lib-dynload',
    ]

    plugin_dir = Path(plugin_dir)
    for plugin_name in plugins_names:
        venv_dir = plugin_dir / plugin_name / 'venv'
        if venv_dir.exists():
            sys.path.extend(
                list(
                    map(
                        lambda x: str(venv_dir / x),
                        venv_relative_dirs_list
                    )
                )
            )


def get_plugins_databases(plugins_names):
    """
    Finds settings.py in plugin directory and loads DATABASE setting
    :return:
    Dictionary with plugin_name: db settings
    """
    plugin_db_settings = dict()
    for plugin_name in plugins_names:
        try:
            db_settings = import_string(f'{plugin_name}.settings.DATABASE')
            plugin_db_settings.update({plugin_name: db_settings})
        except ImportError:
            # plugin doesn't have DATABASE setting
            pass
    return plugin_db_settings


def get_plugins_handlers_config(plugins_names, log_dir, handler_base_config):
    """
    Creates log handler config with name {plugin_name}_handler for every plugin name
    """
    handlers_config = dict()
    for plugin_name in plugins_names:
        plugin_log_dir = Path(log_dir) / plugin_name
        plugin_log_dir.mkdir(exist_ok=True)
        plugin_main_log = plugin_log_dir / f'{plugin_name}.log'
        handlers_config.update({
            f'{plugin_name}_handler': {
                **handler_base_config,
                'filename': str(plugin_main_log)
            }
        })
    return handlers_config


def get_plugins_loggers(plugins_names, logger_config):
    """
    Creates logger for every plugin name with logger config and {plugin_name}_handler handler
    """
    loggers_config = dict()
    for plugin_name in plugins_names:
        loggers_config.update({
            f'{plugin_name}': {
                **logger_config,
                'handlers': [f'{plugin_name}_handler', ]
            }
        })
    return loggers_config


def get_plugin_api_version(plugin_name):
    """
    Returns plugin version from plugin name or from setup.py
    """
    # try to get plugin version from name
    # plugin name may include version <some_name~2.3>
    version = get_plugin_version_from_full_plugin_name(plugin_name)
    print(version)
    if version:
        return version
    # try to get version from setup.py
    try:
        return import_string(f'{plugin_name}.setup.__api_version__')
    except ImportError:
        return '1'


PLUGIN_VERSION_PATTERN = re.compile(r'_v(\d+(\.\d)*)$')


def get_plugin_version_from_full_plugin_name(plugin_name):
    match_obj = PLUGIN_VERSION_PATTERN.search(plugin_name)
    if match_obj:
        version = match_obj.group(1)
        return version
    return ''


def get_plugin_name_from_full_plugin_name(plugin_name):
    """
    Discard PLUGIN_VERSION_PATTERN
    Returns only plugin name
    """
    match_obj = PLUGIN_VERSION_PATTERN.search(plugin_name)
    if match_obj:
        version_suffix = match_obj.group(0)
        return re.sub(version_suffix, '', plugin_name)
    else:
        return plugin_name


def get_plugin_base_url(plugin_name):
    return f'{get_plugin_name_from_full_plugin_name(plugin_name).lower()}/v{get_plugin_api_version(plugin_name)}/'


