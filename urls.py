# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect

from django.contrib import admin
admin.autodiscover()

from slavdict.dictionary.models import Entry
entries = Entry.objects.all()

test = {
    'template': 'template1.django.html',
    'extra_context': {
            'title': u'Словарные статьи',
            'content': u'Тестовое содержимое страницы. Ура, сайт работает!',
            'entries': entries,
        }
    }

urlpatterns = patterns('',
    url( r'^admin/',     include(admin.site.urls)),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

urlpatterns += patterns('',
    url( r'^$',      direct_to_template,     test),
    url( r'^forum/', include('slavdict.forum.urls')),
    url( r'^wiki/$', redirect('http://slavonic.pbworks.com/')),
)

try:
    import local_urls
    urlpatterns += local_urls.urlpatterns
except ImportError, AttributeError:
    pass
