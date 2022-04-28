import typing

from django.urls import path as _django_path


def build_django_path(url: str, handler: typing.Callable):
    return _django_path(url, handler)


path = build_django_path
