# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from slavdict.admin import ui
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url( r'^admin/',     include(admin.site.urls) ),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls') ),
    url( r'^ui/',        include(ui.urls) ),
)

urlpatterns += patterns('',
    url( r'^$', 'slavdict.dictionary.views.last_entry', name='last_entry' ),
    url( r'^login/$', 'django.contrib.auth.views.login'),
    url( r'^logout/$', 'django.contrib.auth.views.logout'),
    url( r'^entries/$', 'slavdict.dictionary.views.all_entries', name='all_entries_url' ),
    url( r'^entries/test/$', 'slavdict.dictionary.views.test_entries' ),
    url( r'^entries/greek-to-find/$', 'slavdict.dictionary.views.greek_to_find' ),
    url( r'^entries/(\d+)/$', 'slavdict.dictionary.views.single_entry', name='single_entry_url' ),
    url( r'^entries/(\d+)/intermed/$',
         'slavdict.dictionary.views.single_entry',
         {'extra_context': {'show_additional_info': True, 'intermed': True}},
         name="intermediary_change_form_url"),
    url( r'^entries/(\d+)/change/$', 'slavdict.dictionary.views.change_entry' ),
    url( r'^entries/(\d+)/pdf/$', 'slavdict.dictionary.views.pdf_for_single_entry', name="entry_pdf_url" ),
    url( r'^forum/', include('slavdict.forum.urls') ),
    url( r'^wiki/$', redirect_to, {'url': 'http://slavonic.pbworks.com/'} ),
    url( r'^switch/additional-info/', 'slavdict.dictionary.views.switch_additional_info', name='switch_info_url' ),
    url( r'^greek-found/', 'slavdict.dictionary.views.make_greek_found' ), # Впоследствии необходимо будет удалить.
    url( r'^csv-import/', 'slavdict.dictionary.views.import_csv_billet' ),
)

try:
    import local_urls
    urlpatterns += local_urls.urlpatterns
except ImportError, AttributeError:
    pass
