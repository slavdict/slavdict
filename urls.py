# -*- coding: utf-8 -*-

from coffin.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from coffin.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from slavdict.admin import ui
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url( r'^admin/',     include(admin.site.urls) ),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls') ),
    url( r'^ui/',        include(ui.urls) ),
)

urlpatterns += patterns('',
    url( r'^$', 'slavdict.dictionary.views.entry_list', name='all_entries_url' ),
    url( r'^login/$', 'django.contrib.auth.views.login'),
    url( r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    url( r'^entries/$', 'slavdict.dictionary.views.all_entries' ),
    url( r'^entries/test/$', 'slavdict.dictionary.views.test_entries' ),
    url( r'^entries/greek-to-find/$', 'slavdict.dictionary.views.greek_to_find' ),
    url( r'^entries/(\d+)/$', 'slavdict.dictionary.views.single_entry', name='single_entry_url' ),
    url( r'^entries/(\d+)/intermed/$',
         'slavdict.dictionary.views.single_entry',
         kwargs={'extra_context': {'show_additional_info': True, 'intermed': True}},
         name="intermediary_change_form_url"),
    url( r'^entries/(\d+)/change/$', 'slavdict.dictionary.views.change_entry' ),
    url( r'^entries/last/$', 'slavdict.dictionary.views.last_entry', name='last_entry' ),

    url( r'^materials/$', direct_to_template, {'template': 'materials.html'}),
    url( r'^forum/', include('slavdict.forum.urls') ),
    url( r'^wiki/$', redirect_to, kwargs={'url': 'http://slavonic.pbworks.com/'} ),
    url( r'^switch/additional-info/$', 'slavdict.dictionary.views.switch_additional_info', name='switch_info_url' ),
    url( r'^converter/$', 'slavdict.dictionary.views.antconc2ucs8_converter', name='converter' ),
    url( r'^json/multiselect/entries/$', 'dictionary.views.json_multiselect_entries'),
    url( r'^json/singleselect/entries/urls/$', 'dictionary.views.json_singleselect_entries_urls'),
    url( r'^test/multiselect/$', direct_to_template, {'template': 'multiselect.html'}),
    url( r'^greek/$', 'dictionary.views.hellinist_workbench', name='hellinist_workbench' ),
    url( r'^json/greq/save/$', 'dictionary.views.json_greq_save', name="jsonGreqSaveURL"),
    url( r'^json/greq/delete/$', 'dictionary.views.json_greq_delete', name="jsonGreqDeleteURL"),
    url( r'^json/ex/save/$', 'dictionary.views.json_ex_save', name="jsonExSaveURL"),

    # TODO: В последствии всё это должно быть удалено.
    url( r'^adhoc/greek-found/$', 'slavdict.dictionary.views.make_greek_found' ),
    url( r'^adhoc/csv-import/$', 'slavdict.dictionary.views.import_csv_billet' ),
    url( r'^adhoc/moodle-import/$', 'slavdict.moodle_import.views.import_moodle_base' ),
    #url( r'^utils/dump/dictionary/$', 'slavdict.dumper.views.dumpdata' ),
    url( r'^utils/non-unicode-greek/$', 'slavdict.dictionary.utils.non_unicode_greek' ),
)

urlpatterns += staticfiles_urlpatterns()

try:
    import local_urls
    urlpatterns += local_urls.urlpatterns
except ImportError, AttributeError:
    pass
