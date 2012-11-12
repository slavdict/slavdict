import newrelic.agent
newrelic.agent.initialize('/usr/local/etc/newrelic.ini')

import os
import sys

sys.path.append('/var/www/')
sys.path.append('/var/www/slavdict/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'slavdict.settings'
#os.environ["CELERY_LOADER"] = "django"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
application = newrelic.agent.wsgi_application()(application)
