from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views as v
from . import jsonviews as jv

AI_KWARGS = {'name': 'switch_info_url'}
AUDIT_KWARGS = {'kwargs': {'mark_as_audited': True}}
DUP_KWARGS = {'name': 'duplicate_entry'}
INTERMED_KWARGS = {'kwargs': {'extra_context': {
    'show_additional_info': True,
    'intermed': True}}, 'name': 'intermediary_change_form_url'}
GREEK_ENTRIES_KWARGS = {'name': 'hellinist_entries', 'kwargs': {
    'for_hellinists': True, 'per_page': 5}}
GREEK_REDIR_KWARGS = {'pattern_name': 'hellinist_examples', 'permanent': True}
HELEX_KWARGS = {'name': 'hellinist_examples'}
UNAUDIT_KWARGS = {'kwargs': {'mark_as_unaudited': True}}

urlpatterns = [
    url(r'^$', v.entry_list, name='all_entries_url'),

    url(r'^print/$', RedirectView.as_view(url='/print/entries/')),
    url(r'^print/entries/$', v.all_entries),
    url(r'^print/examples/$', v.all_examples),
    url(r'^print/examples/audit/$', v.all_examples, **AUDIT_KWARGS),
    url(r'^print/examples/unaudit/$', v.all_examples, **UNAUDIT_KWARGS),
    url(r'^cherry-pick/$', v.all_entries, kwargs={'is_paged': True}),

    url(r'^entries/(\d+)/$', v.single_entry, name='single_entry_url'),
    url(r'^entries/(\d+)/intermed/$', v.single_entry, **INTERMED_KWARGS),
    url(r'^entries/(\d+)/edit/$', v.edit_entry, name='edit_form_url'),
    url(r'^entries/(\d+)/duplicate/$', v.duplicate_entry, **DUP_KWARGS),
    url(r'^entries/(\d+)/get/$', jv.json_entry_get),
    url(r'^entries/save/$', jv.json_entry_save),
    url(r'^entries/merge/$', jv.json_entry_merge),
    url(r'^entries/jserror/$', jv.js_error_notify),

    url(r'^materials/$', v.materials),
    url(r'^switch/additional-info/$', v.switch_additional_info, **AI_KWARGS),
    url(r'^converter/$', v.antconc2ucs8_converter, name='converter'),

    url(r'^json/ss/entries/urls/$', jv.json_singleselect_entries_urls),
    url(r'^json/entry/meanings/$', jv.json_meanings_for_entry),

    url(r'^greek/$', RedirectView.as_view(**GREEK_REDIR_KWARGS)),
    url(r'^greek/find-example/$', v.hellinist_workbench, **HELEX_KWARGS),
    url(r'^greek/entries/$', v.entry_list, **GREEK_ENTRIES_KWARGS),
    url(r'^json/greq/save/$', jv.json_greq_save, name="jsonGreqSaveURL"),
    url(r'^json/greq/delete/$', jv.json_greq_delete, name="jsonGreqDeleteURL"),
    url(r'^json/ex/save/$', jv.json_ex_save, name="jsonExSaveURL"),
    url(r'^json/etym/save/$', jv.json_etym_save, name="jsonEtymSaveURL"),
    url(r'^json/etym/delete/$', jv.json_etym_delete, name="jsonEtymDeleteURL"),

    # TODO: Впоследствии всё это должно быть удалено.
    url(r'^adhoc/csv-import/$', v.import_csv_billet),
    url(r'^adhoc/dump/$', v.dump),
    url(r'^urls/$', v.useful_urls, name='usefulURLs'),
    url(r'^urls/([^/]+)/$', v.useful_urls, name='usefuleURLsX'),
]
