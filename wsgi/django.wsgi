# -*- coding: utf-8 -*-
import os
import sys

sys.path.append('/var/www/')
sys.path.append('/var/www/slavdict/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'slavdict.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


# Планировщик
from apscheduler.scheduler import Scheduler
import datetime
import logging
logging.basicConfig()
sched = Scheduler()
sched.start()

from slavdict.dumper import gauge as Gauge
from slavdict.dumper.views import make_dump

@sched.cron_schedule(minute='*/2')
def dump_job():
    print 'j LATEST DUMP\t', datetime.datetime.strftime(Gauge.LATEST_DUMP['dictionary'], format='%Y.%m.%d %H:%M')
    print 'j LATEST CHANGE\t', datetime.datetime.strftime(Gauge.LATEST_CHANGE['dictionary'], format='%Y.%m.%d %H:%M')

    if Gauge.LATEST_CHANGE['dictionary'] > Gauge.LATEST_DUMP['dictionary']:
        make_dump()
