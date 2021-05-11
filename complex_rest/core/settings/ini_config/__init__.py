import configparser

from pathlib import Path
from .defaults import default_config as defaults


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def merge_ini_config_with_defaults(config, default_config):
    """
    Merge ini config with default config
    :param config: config
    :param default_config: dict with default config
    :return:
    Merged dictionary config
    """
    config = dict(config)
    for key in default_config.keys():
        default_config[key].update(config.get(key, {}))
    return default_config


def make_abs_paths(config_dict, dict_keys_list):
    """
    Replace relative paths in config to absolute paths and create directories if they doesn't exist
    :param config_dict: dict config
    :param dict_keys_list: list of keys in dictionary where relative path located
    :return:
    """
    for keys in dict_keys_list:
        # replace relative paths to absolute
        p = Path(config_dict[keys[0]][keys[1]])
        if not p.is_absolute():
            dir_path = (BASE_DIR / p).resolve()
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
        config_dict[keys[0]][keys[1]] = dir_path


def get_ini_config():
    """
    Read rest.conf in base directory
    :return:
    config dictionary merged with defaults
    """
    config = configparser.ConfigParser()

    config.read(BASE_DIR / 'rest.conf')

    merged_with_defaults = merge_ini_config_with_defaults(
        config, defaults
    )
    make_abs_paths(
        merged_with_defaults, [['plugins', 'plugins_dir'], ['plugins', 'plugin_dev_dir'], ['logging', 'log_dir']]
    )
    return merged_with_defaults


ini_config = get_ini_config()

