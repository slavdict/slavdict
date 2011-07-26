# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import HttpResponse

from dumper.models import Dump
from dictionary.models import Entry
import dumper.gauge as Gauge

default_datetime = datetime.datetime(year=1961, month=4, day=12, hour=9, minute=7)

try:
    Gauge.LATEST_DUMP['dictionary'] = Dump.objects.filter(dump_type=u'D').latest('dump_time')
except Dump.DoesNotExist:
    Gauge.LATEST_DUMP['dictionary'] = default_datetime

try:
    Gauge.LATEST_CHANGE['dictionary'] = Entry.objects.latest('mtime')
except Entry.DoesNotExist:
    Gauge.LATEST_CHANGE['dictionary'] = default_datetime
#output = call_command('dumpdata', 'dictionary', format='xml', indent=4)


from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Entry, dispatch_uid="dict_save_monitor")
def dict_save_monitor(sender, **kwargs):
    Gauge.LATEST_CHANGE['dictionary'] = datetime.datetime.now()
    print datetime.datetime.strftime(Gauge.LATEST_CHANGE['dictionary'], format='%Y.%m.%d %H:%M:%S')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def dumpdata(request):
    response = HttpResponse(output, mimetype="application/xml")
    response['Content-Disposition'] = 'attachment; filename=.dictionary--%s---%s.xml' % (
        datetime.datetime.strftime(datetime.datetime.now(), format='%Y.%m.%d--%H.%M'),
        14,
        )
    return response
