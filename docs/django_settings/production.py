"""
production settings
"""
import os
from .base import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY', None)
