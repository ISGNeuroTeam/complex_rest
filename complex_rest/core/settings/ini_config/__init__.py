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
    if isinstance(config, configparser.ConfigParser):
        config = configparser_to_dict(config)

    result_config = merge_dicts(config, default_config)
    return result_config


def configparser_to_dict(config):
    """
    Convert configparser  to dictionary
    """
    return {s: dict(config.items(s)) for s in config.sections()}


def merge_dicts(first_dict, second_dict):
    """
    Merges two dicts. Returns new dictionary. First dict in priority
    """
    result_dict = copy.deepcopy(second_dict)
    for key, value in first_dict.items():
        if isinstance(value, dict):
            # get node or create one
            node = result_dict.setdefault(key, {})
            result_dict[key] = merge_dicts(value, node)
        else:
            if value:
                result_dict[key] = value

    return result_dict


def make_abs_paths(config_dict, dict_keys_list, base_dir: Path = None):
    """
    Replace relative paths in config to absolute paths and create directories if they doesn't exist
    :param config_dict: dict config
    :param dict_keys_list: list of keys in dictionary where relative path located
    :param base_dir: base directory to evaluate absolute path
    :return:
    """
    if base_dir is None:
        base_dir = BASE_DIR

    for section, option in dict_keys_list:
        # replace relative paths to absolute
        p = Path(config_dict[section][option])
        if not p.is_absolute():
            dir_path = (base_dir / p).resolve()
        else:
            dir_path = p

        # create directory
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)

        config_dict[section][option] = str(dir_path)


def make_boolean(config_dict):
    """
    Finds strings in the dictionary like 'true' of 'False' and replaces it with boolean value
    """
    for section in config_dict:
        for option in config_dict[section]:
            if isinstance(config_dict[section][option], str):
                lower_case_value = config_dict[section][option].lower()
                if lower_case_value == 'false':
                    config_dict[section][option] = False
                if lower_case_value == 'true':
                    config_dict[section][option] = True


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

    config = configparser_to_dict(config)

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
    make_boolean(merged_with_defaults)
    return merged_with_defaults


ini_config = get_ini_config()
