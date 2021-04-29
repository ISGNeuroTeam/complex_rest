from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, GroupAdmin
from .models import User, Group, Permission


class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'guid', 'email', 'first_name', 'last_name', 'is_staff')


admin.site.unregister(DjangoGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Permission)
