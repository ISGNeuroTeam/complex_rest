from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class RestAdminSite(admin.AdminSite):
    site_header = 'Complex REST administration'


class RestAdminConfig(AdminConfig):
    default_site = 'core.override_admin.RestAdminSite'
