import sys

from pathlib import Path


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


