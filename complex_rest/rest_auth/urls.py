from rest_framework.routers import DefaultRouter
from django.urls import re_path

from .views import (
    UserViewSet, GroupViewSet, RoleViewSet, GroupUserViewSet, GroupRoleViewSet, Login, Logout, IsLoggedIn,
    PermitViewSet, ActionView, SecurityZoneViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'groups/(?P<group_id>[^/.]+)/users/?', GroupUserViewSet, basename='group_users')
router.register(r'groups/(?P<group_id>[^/.]+)/roles/?', GroupRoleViewSet, basename='group_roles')
router.register(r'permits', PermitViewSet, basename='permit')
router.register(r'security_zones', SecurityZoneViewSet, basename='security_zone')


urlpatterns = [
    re_path(r'^login/?$', Login.as_view(), name='login'),
    re_path(r'^isloggedin/?$', IsLoggedIn.as_view()),
    re_path(r'^logout/?$', Logout.as_view()),
    re_path(r'^actions/?$', ActionView.as_view()),
    re_path(r'^actions/(?P<plugin_name>[\w_-]+)/?$', ActionView.as_view())
]

urlpatterns += router.urls
