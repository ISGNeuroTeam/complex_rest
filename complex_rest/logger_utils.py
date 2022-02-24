import configparser
import copy
import super_logger
from pathlib import Path
import logging
from typing import Dict, List, Union, Callable

default_separate_logs_level = 'DEBUG'
default_common_logs_level = 'ERROR'


class LoggersInfo:
    """Structure to keep track of separate logs and common logs option of loggers for one plugin"""
    def __init__(self, separate_logs: str, common_logs: str, loggers_lst: List[Dict[str, Union[bool, int, str]]]):
        self.separate_logs = separate_logs
        self.common_logs = common_logs
        self.loggers_lst = loggers_lst


def get_one_plugin_config(handlers: List[str], plugins_loggers: Dict[str, Dict[str, Union[int, str]]],
                          LOG_ROTATION: bool) -> LoggersInfo:
    """
    Adds one default logger type to the plugin in form of structure with config
    and default level for separate log file and common log file
    """

    config = {
        "type": 'HR',
        "file": plugins_loggers[handlers[0]]['filename'],
        "level": plugins_loggers[handlers[0]]['level'],
        "message_format": "@_time:%Y-%m-%d %H:%M:%S@ |@name@| <@message@> [@level@] {@extra@}",
        "standard_attributes": {
            "name": "name",
            "levelname": "level",
            "module": "module",
            "filename": "filename",
            "lineno": "line",
            "funcName": "func",
            "processName": "proc",
            "process": "PID",
            "message": "message",
            "exception": "exception",
            "created": "_time",
            "extra": "extra"
        }
    }
    if LOG_ROTATION:
        config["rotation"] = True
    return LoggersInfo(default_separate_logs_level, default_common_logs_level, [config])


def convert_to_superlogger_conf(plugins_loggers: Dict[str, Dict[str, Union[int, str]]],
                                plugins_log_handlers: Dict[str, Dict[str, Union[int, bool, List[str]]]],
                                PLUGINS: List[str], LOG_ROTATION: bool) -> Dict[str, LoggersInfo]:
    """
    Converts default plugin logging config to default super logging config
    returns a dictionary
    key: plugin name
    value: LoggersInfo containing super logger configuration for one logger
    and default level for separate log file and common log file
    """
    loggers_for_plugins = {}
    for plugin in PLUGINS:
        loggers_for_plugins[plugin] = get_one_plugin_config(plugins_log_handlers[plugin]['handlers'], plugins_loggers,
                                                            LOG_ROTATION)
    return loggers_for_plugins


def override_root_logger() -> None:
    """
    This function is responsible for adding handlers and level to root logger (not super root logger)
    it is done to see logs from external libraries in super logger format
    """
    super_root_logger = super_logger.getLogger()
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        root_logger.handlers = super_root_logger.handlers
        root_logger.level = super_root_logger.level


def set_minimal_separate_log_level(loggers_lst: List[Dict], separate_logs_level: str) -> None:
    """
    separate log level has priority over loggers level in super logger,
    hence minimal level of loggers will be set to separate logs level.
    if logger level is DEBUG and separate logs level is INFO, logger level will be set to INFO
    """
    for logger in loggers_lst:
        if super_logger.logging_levels[logger['level']] < super_logger.logging_levels[separate_logs_level]:
            logger['level'] = separate_logs_level


def add_root_handlers(loggers_lst: List[Dict], base_loggers: List[Dict], common_logs_level: str) -> None:
    """
    Add super root logger handlers to every plugin specifying common logs level
    Inheritance and propagate True cannot be used due to common logs level restriction
    """
    for logger in base_loggers:
        logger['level'] = common_logs_level
        loggers_lst.append(logger)


def superlogging_config_func(logging_settings: Dict[str, Union[List, LoggersInfo]]) -> None:
    """
    Will be used as logging_config_func in DJANGO configure_logging instead of logging.config.dictConfig
    this behaviour is specified by LOGGING_CONFIG in base.py
    """
    super_logger.getLogger().setLogger({"loggers": logging_settings["loggers"]})
    override_root_logger()
    for settings in logging_settings:
        if settings != "loggers":
            plugin_logger = super_logger.getLogger(settings)
            plugin_logger.propagate = False  # because root handlers will be added manually to specify different level
            set_minimal_separate_log_level(logging_settings[settings].loggers_lst,
                                           logging_settings[settings].separate_logs)
            add_root_handlers(logging_settings[settings].loggers_lst, logging_settings["loggers"],
                              logging_settings[settings].common_logs)
            plugin_logger.setLogger({"loggers": logging_settings[settings].loggers_lst})


def merge_dicts(d_primary: Dict, d_secondary: Dict) -> Dict:
    """
    Merge two dicts with priority of first and type-checking.
    If two dicts has the same key, the value for merged dict will be choosen by the following rules:
    if the type of the value is the same, d_primary value will be choosen, d_secondary value otherwise.
    d_secondary is considered as "default".

    For example, you have 2 dicts with some keys are crossing:
    >>> d1 = {'one': 1, 'two': 2.0, 'three': 3}
    >>> d2 = {'one': 1, 'two': 3, 'three': 0}
    >>> merge_dicts(d1, d2)
    Wrong parameter "two": 2.0. Got type <class 'float'>, but <class 'int'> expected. Using default.
    {'one': 1, 'two': 3, 'three': 3}
    """
    for key in d_primary:
        if key in d_secondary:
            if isinstance(d_secondary[key], dict):
                d_secondary[key] = merge_dicts(d_primary[key], d_secondary[key])
            else:
                if type(d_secondary[key]) == type(d_primary[key]):
                    d_secondary[key] = d_primary[key]
        else:
            d_secondary.update(
                {key: d_primary[key]}
            )

    return d_secondary


def transform_str_to_bool(**kwargs) -> Dict:
    """transforms str 'true' or str 'false' values to bool True and bool False respectively"""
    for k, v in kwargs.items():
        if v.lower() == 'true' or v.lower() == 'false':
            kwargs[k] = v.lower() == 'true'
    return kwargs


def extract_logging_configurations_dict_from_ini(config_filename: Path) -> Dict[str, Union[str, List[Dict]]]:
    """
    Plugins config are currently in ini format
    This function is passed as parameter to update_from_plugin_conf to parse ini config ang extract logging information
    """
    config_dict = dict()
    config = configparser.ConfigParser(interpolation=None)  # otherwise, it will affect message format
    config.optionxform = str  # to preserve case sensitivity of the attributes
    config.read(config_filename)
    if 'logging' in config.sections():
        config_dict['separate_logs'] = config['logging'].get('separate_logs', default_separate_logs_level)
        config_dict['common_logs'] = config['logging'].get('common_logs', default_common_logs_level)
    logger_no = 1
    config_dict['loggers'] = []
    while f'logger{logger_no}' in config.sections():
        if f'standard_attributes{logger_no}' in config.sections():
            config_dict['loggers'].append({**transform_str_to_bool(**config[f'logger{logger_no}']),
                                           'standard_attributes': dict(config[f'standard_attributes{logger_no}'])})
        else:
            config_dict['loggers'].append({**transform_str_to_bool(**config[f'logger{logger_no}'])})
        logger_no += 1
    return config_dict


def update_from_plugin_conf(loggers_for_plugins: Dict[str, LoggersInfo], PLUGINS_DIR: str,
                            get_config_func: Callable[[Path],  Dict[str, Union[str, List[Dict]]]]) -> Dict[str, LoggersInfo]:
    """
    Override default logger type and add more logger types if specified in
    <PLUGINS_DIR>/<plugin_name>/<plugin_name>.conf
    """
    for plugin_name in loggers_for_plugins:
        config_file = Path(PLUGINS_DIR) / plugin_name / f'{plugin_name}.conf'
        if config_file.is_file():
            conf_dict = get_config_func(config_file)  # function to parse config and extract logging information
            loggers_for_plugins[plugin_name].common_logs = conf_dict.get('common_logs', default_common_logs_level)
            loggers_for_plugins[plugin_name].separate_logs = conf_dict.get('separate_logs', default_separate_logs_level)
            if conf_dict.get('loggers', None):
                default_conf = loggers_for_plugins[plugin_name].loggers_lst.pop(0)
                logger_no = 1
                try:
                    for conf in conf_dict['loggers']:
                        loggers_for_plugins[plugin_name].loggers_lst.append(merge_dicts(conf, copy.deepcopy(default_conf)))
                        logger_no += 1
                except TypeError as e:  # in case of conf_dict['loggers'] is not iterable
                    loggers_for_plugins[plugin_name].loggers_lst.append(default_conf)  # rollback
                    print(f'WARNING something wrong in logging configuration for plugin {plugin_name}')
                    print(e)
                    print(f'Using default config for logger number {logger_no}...')
    return loggers_for_plugins
