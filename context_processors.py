# -*- coding: utf-8 -*-
from django.conf import settings

def jslibs(request):
    return { 'JSLIBS': settings.JSLIBS }
