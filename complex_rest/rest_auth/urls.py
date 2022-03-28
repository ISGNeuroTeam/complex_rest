from rest_framework.routers import DefaultRouter
from django.urls import re_path

from .views import UserViewSet, Login, Logout, IsLoggedIn

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    re_path(r'^login/?$', Login.as_view(), name='login'),
    re_path(r'^isloggedin/?$', IsLoggedIn.as_view()),
    re_path(r'^logout/?$', Logout.as_view()),
]

urlpatterns += router.urls
