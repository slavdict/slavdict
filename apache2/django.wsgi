import sys
import os
import os.path

sys.path.insert(0, '/home/hitrov/djcode/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cslav_dict.settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
