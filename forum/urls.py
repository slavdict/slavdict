# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns += patterns('forum.views',
    url( r'^$',       direct_to_template,     test),
    url( r'^topic/$', 'show_topic'),
)

