# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import HttpResponse

@login_required
@user_passes_test(lambda u: u.is_superuser)
def dumpdata(request):
    output = call_command('dumpdata', 'dictionary', format='xml', indent=4)
    response = HttpResponse(output, mimetype="application/xml")
    response['Content-Disposition'] = 'attachment; filename=.dictionary--%s---%s.xml' % (
        datetime.datetime.strftime(datetime.datetime.now(), format='%Y.%m.%d--%H.%M'),
        14,
        )
    return response
