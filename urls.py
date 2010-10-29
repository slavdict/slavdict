# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from django.shortcuts import redirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url( r'^admin/',     include(admin.site.urls) ),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls') ),
)

urlpatterns += patterns('',
    url( r'^$', 'slavdict.dictionary.views.last_entry', name='last_entry' ),
    url( r'^entries/$', 'slavdict.dictionary.views.all_entries', name='all_entries_url' ),
    url( r'^entries/(\d+)/$', 'slavdict.dictionary.views.single_entry', name='single_entry_url' ),
    url( r'^forum/', include('slavdict.forum.urls') ),
    url( r'^wiki/$', redirect_to, {'url': 'http://slavonic.pbworks.com/'} ),
    url( r'^switch/additional-info/', 'slavdict.dictionary.views.switch_additional_info', name='switch_info_url' ),
)

try:
    import local_urls
    urlpatterns += local_urls.urlpatterns
except ImportError, AttributeError:
    pass
