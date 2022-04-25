import os
import sys
import re

from importlib import import_module
from pathlib import Path


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        ) from err


def get_plugins_names(plugin_dir):
    """
    Returns all plugin names located in plugins dir
    If PLUGIN_NAME environment varialbe exists and not empty then only one plugin name returned
    :param plugin_dir: directory with plugins
    :return:
    list with plugins names
    """
    plugin_name_env = os.environ.get('COMPLEX_REST_PLUGIN_NAME', '')
    if plugin_name_env:
        return [
            plugin_name for plugin_name in plugin_name_env.split()
            if (Path(plugin_dir) / plugin_name).exists()
        ]
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


def get_plugins_celery_schedule(plugins_names):
    """
    Finds settings.py in plugin directory and loads CELERY_BEAT_SCHEDULE
    Returns dictionary with setting
    """
    celery_beat_settings = dict()
    for plugin_name in plugins_names:
        try:
            plugin_celery_settings = import_string(f'{plugin_name}.settings.CELERY_BEAT_SCHEDULE')
            plugin_celery_settings = {
                plugin_name + '_' + rule_name: rule_value for rule_name, rule_value in plugin_celery_settings.items()
            }
            celery_beat_settings.update(plugin_celery_settings)
        except ImportError:
            # plugin doesn't have celery setting
            pass
    return celery_beat_settings


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
    # plugin name may include version <some_name_v2.3>
    version = get_plugin_version_from_full_plugin_name(plugin_name)
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


