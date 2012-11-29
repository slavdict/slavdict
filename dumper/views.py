# -*- coding: utf-8 -*-
import datetime, os, sys
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import HttpResponse
from coffin.shortcuts import render_to_response
from django.template import RequestContext



from dumper.models import Dump
import dumper.gauge as Gauge
from dictionary.models import Entry


default_datetime = datetime.datetime(year=1961, month=4, day=12, hour=9, minute=7)

try:
    last_dump = Dump.objects.filter(dump_type=u'D').latest('dump_time')
    Gauge.LATEST_DUMP['dictionary'] = last_dump.dump_time
except Dump.DoesNotExist:
    Gauge.LATEST_DUMP['dictionary'] = default_datetime

try:
    last_mentry = Entry.objects.latest('mtime')
    Gauge.LATEST_CHANGE['dictionary'] = last_mentry.mtime
except Entry.DoesNotExist:
    Gauge.LATEST_CHANGE['dictionary'] = default_datetime



# Функция, которая меняет показания счётчика, если сохраняется любой объект Entry.
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=Entry, dispatch_uid="dict_save_monitor")
def dict_save_monitor(sender, **kwargs):
    Gauge.LATEST_CHANGE['dictionary'] = datetime.datetime.now()



# Непосредственное осуществление дампа
from django.conf import settings
def make_dump():
    now = datetime.datetime.now()
    filename = '%s.dictionary--%s---%s.xml' % (settings.DUMP_DIR,
                datetime.datetime.strftime(now, format='%Y.%m.%d--%H.%M'),
                settings.DB_SCHEME_VERSIONS['dictionary'])
    sys.stdout = open(filename, 'w')
    call_command('dumpdata', 'dictionary', format='xml', indent=4)
    sys.stdout.close()
    sys.stdout = sys.__stdout__

    d = Dump(dump_file=filename, dump_type=u'D')
    d.save()
    Gauge.LATEST_DUMP['dictionary'] = now



def dump_job():
    if Gauge.LATEST_CHANGE['dictionary'] > Gauge.LATEST_DUMP['dictionary']:
        make_dump()



@login_required
@user_passes_test(lambda u: u.is_superuser)
def dumpdata(request):
    response = HttpResponse()
    try:
        d = Dump.objects.latest('dump_time')
        path = d.dump_file
        response = HttpResponse(mimetype="application/xml")
        response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(path)

        f = open(path)
        for line in f.readline():
            response.write(line)
        f.close()

    except Dump.DoesNotExist:
        context = { 'error': u'Пока ни одной резервной копии ещё сделано не было.' }
        render_to_response('dump.html', context, RequestContext(request))

    return response

