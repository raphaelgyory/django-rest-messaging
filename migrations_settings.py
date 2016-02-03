#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'migrations.db'),
    }
}

INSTALLED_APPS = (
    # rest_messaging
    'rest_messaging',
)

SECRET_KEY = 'django-rest-messaging'