# -*- coding: utf-8 -*-
"""
WSGI config for slavdict project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import sys
PATH = '/var/www/slavdict'
if PATH not in sys.path:
    sys.path.append(PATH)

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
