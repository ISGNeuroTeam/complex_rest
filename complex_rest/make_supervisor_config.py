import configparser

from pathlib import Path
from core.settings.ini_config import get_ini_config

# get plugins dir
ini_config = get_ini_config()
plugins_dir = Path(ini_config['plugins']['plugins_dir'])


# get plugins proc.conf
processes_conf = [
    str(plugin_dir / 'proc.conf')
    for plugin_dir in plugins_dir.iterdir() if plugin_dir.is_dir() and (plugin_dir / 'proc.conf').exists()
]

# read base config
config = configparser.ConfigParser()
with open('supervisord_base.conf', 'r') as f:
    config.read_file(f)

# # create include section and put all proc.conf in include section
config.add_section('include')
config['include']['files'] = " ".join(processes_conf)

# write supervisord config
with open('supervisord.conf', 'w') as f:
    config.write(f)









