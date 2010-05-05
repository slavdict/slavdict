import sys
import os
import os.path

sys.path.insert(0, '/home/git')
os.environ['DJANGO_SETTINGS_MODULE'] = 'slavdict.settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
