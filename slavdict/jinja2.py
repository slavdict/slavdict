# -*- coding: utf-8 -*-
from __future__ import absolute_import  # Python 2 only

from django.conf import settings
from django.urls import reverse

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'url': reverse,
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_RESOURCES_VERSION': settings.STATIC_RESOURCES_VERSION,
        'JSLIBS': settings.JSLIBS,
    })
    return env

