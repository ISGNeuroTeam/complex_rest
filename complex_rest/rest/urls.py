from typing import Union

from django.urls import path as _django_path, re_path as _django_re_path


def build_django_path(route: str, view: Union[list, tuple, callable], kwargs=None, name=None):
    return _django_path(route, view, kwargs=kwargs, name=name)


def build_django_re_path(route: str, view: Union[list, tuple, callable], kwargs=None, name=None):
    return _django_re_path(route, view, kwargs=kwargs, name=name)


path = build_django_path
re_path = build_django_re_path
