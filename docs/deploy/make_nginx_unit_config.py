import json
from pathlib import Path

from core.settings import BASE_DIR, LOG_DIR, PLUGINS_DIR, STATIC_ROOT, STATIC_URL, MEDIA_URL, MEDIA_ROOT
from core.load_plugins import get_plugins_names

def main():
    plugins_dir = Path(PLUGINS_DIR)
    plugin_names = get_plugins_names(plugins_dir)

    # make nginx configs only for plugins with 'urls.py
    plugin_names = [
        plugin_name for plugin_name in plugin_names if (plugins_dir / plugin_name / 'urls.py').exists()
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

    # add static and media uri

    routes.extend(
        [
            {
                "match": {
                    "uri": [
                        f"{STATIC_URL}*",
                    ]
                },

                "action": {
                    "share": str(STATIC_ROOT.parent) + "/$uri"
                }
            },
            {
                "match": {
                    "uri": [
                        f"{MEDIA_URL}*",
                    ]
                },
                "action": {
                    "share": str(MEDIA_ROOT.parent) + "/$uri"
                }
            }
        ]
    )

    nginx_unit_conf['applications'].update(applications)
    nginx_unit_conf['routes'] = routes + nginx_unit_conf['routes']

    with open('deploy_state/conf.json', 'w') as f:
        json.dump(nginx_unit_conf, f, indent=2)


if __name__ == '__main__':
    main()

