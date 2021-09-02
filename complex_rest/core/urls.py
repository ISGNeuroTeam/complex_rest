"""complex_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pathlib import Path
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from core.load_plugins import get_api_version


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(('rest_auth.urls', 'rest_auth'), namespace='auth')),
]

# add plugins urls if they exist except plugin examples when not debug
urlpatterns += [
    path(f'{plugin.lower()}/v{get_api_version(plugin)}/', include(plugin + '.urls'))
    for plugin in settings.PLUGINS
    if (Path(settings.PLUGINS_DIR) / plugin / 'urls.py').exists()
    if settings.DEBUG or 'plugin_example' not in plugin
]
