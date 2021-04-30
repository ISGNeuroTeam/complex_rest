from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import UserViewSet, Login

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
]

urlpatterns += router.urls
