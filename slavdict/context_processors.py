# -*- coding: utf-8 -*-
from django.conf import settings

def staticfiles(request):
    return { 'JSLIBS': settings.JSLIBS,
             'STATIC_RESOURCES_VERSION': settings.STATIC_RESOURCES_VERSION }
