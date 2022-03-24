from rest_framework.routers import DefaultRouter
from django.urls import re_path

from .views import UserViewSet, Login

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    re_path(r'^login/?$', Login.as_view(), name='login'),
]

urlpatterns += router.urls
