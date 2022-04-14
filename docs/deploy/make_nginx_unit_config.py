import json
from pathlib import Path

from core.settings import BASE_DIR, LOG_DIR, PLUGINS_DIR


def main():
    plugins_dir = Path(PLUGINS_DIR)
    plugin_names = [
        plugin_dir.name
        for plugin_dir in plugins_dir.iterdir() if plugin_dir.is_dir() and (plugin_dir / 'urls.py').exists()
    ]

    # read nginx-unit config
    with open('nginx-unit.json') as f:
        nginx_unit_conf = json.load(f)

    # read plugin app config
    with open('nginx-unit-plugin-app.json') as f:
        plugin_app_conf_template = f.read()

    with open('nginx-unit-plugin-route.json') as f:
        plugin_route_conf_template = f.read()

    routes = list()
    applications = dict()

    for plugin_name in plugin_names:
        # if plugin has custom configuration for nginx unit app then use it
        plugin_unit_app_config_path = plugins_dir / plugin_name / 'nginx-unit-app.json'
        if plugin_unit_app_config_path.exists():
            with open(plugin_unit_app_config_path) as f:
                plugin_app_conf = json.load(f)
        else:
            plugin_app_conf = json.loads(plugin_app_conf_template.replace("{{plugin_name}}", plugin_name))

        # if plugin has custom configuration for nginx unit route then use it
        plugin_unit_route_config_path = plugins_dir / plugin_name / 'nginx-unit-route.json'
        if plugin_unit_route_config_path.exists():
            with open(plugin_unit_route_config_path) as f:
                plugin_route_conf = json.load(f)
        else:
            plugin_route_conf = json.loads(plugin_route_conf_template.replace("{{plugin_name}}", plugin_name))

        routes.append(plugin_route_conf)
        applications[plugin_name] = plugin_app_conf

    nginx_unit_conf['applications'].update(applications)
    nginx_unit_conf['routes'] = routes + nginx_unit_conf['routes']

    with open('deploy_state/conf.json', 'w') as f:
        json.dump(nginx_unit_conf, f, indent=2)


if __name__ == '__main__':
    main()

