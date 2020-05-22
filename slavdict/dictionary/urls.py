from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views
from . import jsonviews

urlpatterns = [
    url( r'^$', views.entry_list, name='all_entries_url' ),

    url( r'^print/$', RedirectView.as_view(url='/print/entries/')),
    url( r'^print/entries/$', views.all_entries ),
    url( r'^print/examples/$', views.all_examples ),
    url( r'^print/examples/audit/$', views.all_examples,
                                     kwargs={'mark_as_audited': True} ),
    url( r'^print/examples/unaudit/$', views.all_examples,
                                       kwargs={'mark_as_unaudited': True} ),
    url( r'^cherry-pick/$', views.all_entries, kwargs={'is_paged': True} ),

    url( r'^entries/(\d+)/$', views.single_entry, name='single_entry_url' ),
    url( r'^entries/(\d+)/intermed/$', views.single_entry,
         kwargs={'extra_context': {'show_additional_info': True, 'intermed': True}},
         name="intermediary_change_form_url"),
    url( r'^entries/(\d+)/edit/$', views.edit_entry,
         name='edit_form_url'),
    url( r'^entries/(\d+)/duplicate/$', views.duplicate_entry, name='duplicate_entry' ),
    url( r'^entries/(\d+)/get/$', jsonviews.json_entry_get ),
    url( r'^entries/save/$', jsonviews.json_entry_save ),
    url( r'^entries/merge/$', jsonviews.json_entry_merge ),
    url( r'^entries/jserror/$', jsonviews.js_error_notify ),

    url( r'^materials/$', views.materials ),
    url( r'^switch/additional-info/$', views.switch_additional_info, name='switch_info_url' ),
    url( r'^converter/$', views.antconc2ucs8_converter, name='converter' ),

    url( r'^json/singleselect/entries/urls/$', jsonviews.json_singleselect_entries_urls),
    url( r'^json/entry/meanings/$', jsonviews.json_meanings_for_entry),

    url( r'^greek/$', RedirectView.as_view(pattern_name='hellinist_examples', permanent=True)),
    url( r'^greek/find-example/$', views.hellinist_workbench, name='hellinist_examples' ),
    url( r'^greek/entries/$', views.entry_list, name='hellinist_entries',
                              kwargs={'for_hellinists': True, 'per_page': 5}),
    url( r'^json/greq/save/$', jsonviews.json_greq_save, name="jsonGreqSaveURL"),
    url( r'^json/greq/delete/$', jsonviews.json_greq_delete, name="jsonGreqDeleteURL"),
    url( r'^json/ex/save/$', jsonviews.json_ex_save, name="jsonExSaveURL"),
    url( r'^json/etym/save/$', jsonviews.json_etym_save, name="jsonEtymSaveURL"),
    url( r'^json/etym/delete/$', jsonviews.json_etym_delete, name="jsonEtymDeleteURL"),
    url( r'^json/goodness/save/$', jsonviews.json_goodness_save, name="jsonGoodnessSaveURL"),

    # TODO: Впоследствии всё это должно быть удалено.
    url( r'^adhoc/csv-import/$', views.import_csv_billet ),
    url( r'^adhoc/dump/$', views.dump ),
    url( r'^urls/$', views.useful_urls, name='usefulURLs' ),
    url( r'^urls/([^/]+)/$', views.useful_urls, name='usefuleURLsX' ),
]
