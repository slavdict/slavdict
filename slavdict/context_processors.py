# -*- coding: utf-8 -*-
from django.conf import settings

def staticfiles(request):
    return { 'CSS_PATH': settings.CSS_PATH,
             'JSLIBS': settings.JSLIBS,
             'STATIC_RESOURCES_VERSION': settings.STATIC_RESOURCES_VERSION }
