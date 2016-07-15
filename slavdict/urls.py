# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView

from slavdict.admin import ui
admin.autodiscover()

urlpatterns = patterns('',
    url( r'^admin/',     include(admin.site.urls) ),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls') ),
    url( r'^ui/',        include(ui.urls) ),
    url( r'^login/$', 'django.contrib.auth.views.login'),
    url( r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)

urlpatterns += patterns('slavdict.dictionary',
    url( r'^$', 'views.entry_list', name='all_entries_url' ),

    url( r'^print/$', RedirectView.as_view(url='/print/entries/')),
    url( r'^print/entries/$', 'views.all_entries' ),
    url( r'^print/examples/$', 'views.all_examples' ),
    url( r'^print/examples/audit/$', 'views.all_examples',
                                      kwargs={'mark_as_audited': True} ),
    url( r'^print/examples/unaudit/$', 'views.all_examples',
                                        kwargs={'mark_as_unaudited': True} ),
    url( r'^cherry-pick/$', 'views.all_entries', kwargs={'is_paged': True} ),

    url( r'^entries/(\d+)/$', 'views.single_entry', name='single_entry_url' ),
    url( r'^entries/(\d+)/intermed/$', 'views.single_entry',
         kwargs={'extra_context': {'show_additional_info': True, 'intermed': True}},
         name="intermediary_change_form_url"),
    url( r'^entries/(\d+)/edit/$', 'views.edit_entry',
         name='edit_form_url'),
    url( r'^entries/(\d+)/get/$', 'jsonviews.json_entry_get' ),
    url( r'^entries/save/$', 'jsonviews.json_entry_save' ),
    url( r'^entries/jserror/$', 'jsonviews.js_error_notify' ),

    url(r'^materials/$', 'views.direct_to_template',
                         kwargs={'template': 'materials.html'}),
    url( r'^switch/additional-info/$', 'views.switch_additional_info', name='switch_info_url' ),
    url( r'^converter/$', 'views.antconc2ucs8_converter', name='converter' ),

    url( r'^json/singleselect/entries/urls/$', 'jsonviews.json_singleselect_entries_urls'),

    url( r'^greek/$', 'views.hellinist_workbench', name='hellinist_workbench' ),
    url( r'^json/greq/save/$', 'jsonviews.json_greq_save', name="jsonGreqSaveURL"),
    url( r'^json/greq/delete/$', 'jsonviews.json_greq_delete', name="jsonGreqDeleteURL"),
    url( r'^json/ex/save/$', 'jsonviews.json_ex_save', name="jsonExSaveURL"),
    url( r'^json/goodness/save/$', 'jsonviews.json_goodness_save', name="jsonGoodnessSaveURL"),

    url( r'^urls/$', 'views.useful_urls', name="usefulURLs"),
    url( r'^urls/([^/]+)/$', 'views.useful_urls', name="usefulURLsX"),

    # TODO: В последствии всё это должно быть удалено.
    url( r'^adhoc/csv-import/$', 'views.import_csv_billet' ),
    url( r'^adhoc/dump/$', 'views.dump' ),
)

urlpatterns += staticfiles_urlpatterns()
