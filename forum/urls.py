# -*- coding: utf-8 -*-

from coffin.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

test = {
    'template': 'base.html',
    'extra_context': {
        'title': u'Проверка',
        'content': u'Форум!!!'
        }
    }

urlpatterns = patterns('',
    url( r'^$',       direct_to_template,     test),
    url( r'^topic/$', 'show_topic'),
)

