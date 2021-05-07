import sys

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
