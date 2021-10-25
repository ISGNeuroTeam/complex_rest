"""
production settings
"""
import os

from django.core.management.utils import get_random_secret_key
from .base import *

DEBUG = False

# put secret key in secret_key file for the first launch
secret_key_file = BASE_DIR / 'secret_key'

if secret_key_file.exists():
    SECRET_KEY = secret_key_file.read_text()
else:
    SECRET_KEY = get_random_secret_key()
    secret_key_file.write_text(SECRET_KEY)
