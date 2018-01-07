# -*- coding: utf-8 -*-
from __future__ import absolute_import  # Python 2 only

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'JSLIBS': settings.JSLIBS,
        'STATIC_RESOURCES_VERSION': settings.STATIC_RESOURCES_VERSION,
        'STATIC_URL': settings.STATIC_URL,
    })
    return env

