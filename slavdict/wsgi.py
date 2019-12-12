import sys
PATH = '/var/www/slavdict'
if PATH not in sys.path:
    sys.path.append(PATH)

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
