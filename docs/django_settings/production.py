"""
production settings
"""
import os
from .base import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']
