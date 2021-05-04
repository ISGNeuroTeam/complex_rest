from rest.urls import path
from .views import hello, random_dataframe


urlpatterns = [
    path('hello/', hello),
    path('random_dataframe/', random_dataframe)
]
