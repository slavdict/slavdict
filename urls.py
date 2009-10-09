# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

test = {
    'template': 'base.html',
    'extra_context': {
        'title': u'Проверка',
        'content': u'Тестовое содержимое страницы. Ура, сайт работает!'
        }
    }

urlpatterns = patterns('',
    url( r'^admin/',     include('admin.site.urls')),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

urlpatterns += patterns('',
    url( r'^$',          direct_to_template,     test),
    url( r'^forum/$',    include('cslav_dict.forum.urls')),
)

