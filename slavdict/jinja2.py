from django.conf import settings
from django.urls import reverse

from jinja2 import Environment

from .jinja_extensions.trim_spaces import additional_jinja_filters


def environment(**options):
    env = Environment(**options)
    env.filters.update(additional_jinja_filters)
    env.globals.update({
        'url': reverse,
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_RESOURCES_VERSION': settings.STATIC_RESOURCES_VERSION,
        'JSLIBS': settings.JSLIBS,
    })
    return env

