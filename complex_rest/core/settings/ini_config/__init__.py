import os
import copy
import configparser

from pathlib import Path
from .defaults import default_config as defaults


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def merge_ini_config_with_defaults(config, default_config):
    """
    Merge ini config with default config
    :param config: config dictionary
    :param default_config: dict with default config
    :return:
    Merged dictionary config
    """
    result_config = merge_dicts(config, default_config)
    return result_config


def merge_dicts(first_dict, second_dict):
    """
    Merges two dicts. Returns new dictionary. Fist dict in priority
    """
    result_dict = copy.deepcopy(second_dict)
    for key, value in first_dict.items():
        if isinstance(value, dict):
            # get node or create one
            node = result_dict.setdefault(key, {})
            result_dict[key] = merge_dicts(value, node)
        else:
            result_dict[key] = value

    return result_dict


def make_abs_paths(config_dict, dict_keys_list):
    """
    Replace relative paths in config to absolute paths and create directories if they doesn't exist
    :param config_dict: dict config
    :param dict_keys_list: list of keys in dictionary where relative path located
    :return:
    """
    for section, option in dict_keys_list:
        # replace relative paths to absolute
        p = Path(config_dict[section][option])
        if not p.is_absolute():
            dir_path = (BASE_DIR / p).resolve()

        # create directory
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)

        config_dict[section][option] = str(dir_path)


def get_ini_config():
    """
    Read config passed in REST_CONF environment variable
    or rest.conf in base directory
    :return:
    config dictionary merged with defaults
    """

    # try to read path to config from environment
    conf_path_env = os.environ.get('REST_CONF', None)

    if conf_path_env is None:
        conf_path = BASE_DIR / 'rest.conf'
    else:
        conf_path = Path(conf_path_env).resolve()

    config = configparser.ConfigParser()

    config.read(conf_path)

    # convert to dictionary
    config = {s: dict(config.items(s)) for s in config.sections()}

    merged_with_defaults = merge_ini_config_with_defaults(
        config, defaults
    )
    make_abs_paths(
        merged_with_defaults,
        [
            ['plugins', 'plugins_dir'],
            ['plugins', 'plugin_dev_dir'],
            ['logging', 'log_dir'],
            ['caches', 'file_cache_dir']
        ]
    )
    return merged_with_defaults


ini_config = get_ini_config()
