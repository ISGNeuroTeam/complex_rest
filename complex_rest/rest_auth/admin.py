from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, GroupAdmin

from .models import Group, Permission, Role, Plugin, KeyChain, Action, Permit, SecurityZone, User, ActionsToPermit

class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'guid', 'email', 'first_name', 'last_name', 'is_staff', 'phone', 'photo')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('phone', 'photo')
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('phone', 'photo')
        })
    )


admin.site.unregister(DjangoGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Permission)

admin.site.register(Role)
admin.site.register(Plugin)
admin.site.register(KeyChain)
admin.site.register(Action)
admin.site.register(Permit)
admin.site.register(SecurityZone)
admin.site.register(ActionsToPermit)
