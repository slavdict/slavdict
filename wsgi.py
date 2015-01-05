import os
import sys

import django.core.wsgi

sys.path.append('/var/www/slavdict/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'slavdict.settings'

application = django.core.wsgi.get_wsgi_application()
