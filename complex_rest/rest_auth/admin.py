from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, GroupAdmin

from .models import Group, Permission, Role, Plugin, KeyChain, Action, Permit, SecurityZone, User, ActionsToPermit


class BaseAdmin(admin.ModelAdmin):
    exclude = ('created_at', 'deleted_at', 'updated_at')

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


class RoleAdmin(BaseAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permits',)


class A2PInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['action'].queryset = Action.objects.filter(plugin__name=self.instance.action.plugin.name)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "action":
            kwargs["queryset"] = Action.objects.filter(plugin__name=self.instance.action.plugin.name)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class A2PInline(admin.TabularInline):

    form = A2PInlineForm
    model = ActionsToPermit
    fk_name = 'permit'
    extra = 0


class RolesInline(admin.TabularInline):

    model = Role.permits.through
    extra = 0


class PermitAdmin(BaseAdmin):
    inlines = [
        A2PInline,
        RolesInline
    ]
    list_display = ('__str__',)



admin.site.unregister(DjangoGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Permission)

admin.site.register(Role, RoleAdmin)
admin.site.register(Plugin, BaseAdmin)
admin.site.register(KeyChain, BaseAdmin)
admin.site.register(Action, BaseAdmin)
admin.site.register(Permit, PermitAdmin)
admin.site.register(SecurityZone, BaseAdmin)
admin.site.register(ActionsToPermit, BaseAdmin)
