from django.urls import path
from .api import hello, simple_hello

urlpatterns = [
    path('hello/', hello),
    path('simple_hello', simple_hello)
]
