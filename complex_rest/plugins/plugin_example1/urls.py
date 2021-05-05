from rest.urls import path
from .views import HelloView, Persons

urlpatterns = [
    path('hello/', HelloView.as_view()),
    path('persons/', Persons.as_view())
]
