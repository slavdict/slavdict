import os
import sys

import django.core.handlers.wsgi

sys.path.append('/var/www/')
sys.path.append('/var/www/slavdict/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'slavdict.settings'

application = django.core.handlers.wsgi.WSGIHandler()
