from django.urls import path
from .api import HelloView

urlpatterns = [
    path('hello/', HelloView.as_view())
]
