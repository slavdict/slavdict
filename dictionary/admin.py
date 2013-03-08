# encoding: UTF-8
import copy

from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect

from slavdict.admin import ui

admin.site.login_template = ui.login_template

def staff_has_add_permission(self, request):
    return request.user.is_staff

def staff_has_change_permission(self, request, obj=None):
    return request.user.is_staff

def superuser_has_delete_permission(self, request, obj=None):
    return request.user.is_superuser

def staff_has_delete_permission(self, request, obj=None):
    return request.user.is_staff


def _orth_vars(obj):
    orth_vars = [unicode(i) for i in obj.orthographic_variants.all().order_by('id')]
    delimiter = u', '
    return delimiter.join(orth_vars)

def _collocations(obj):
    collocations = [unicode(i) for i in obj.collocation_set.all().order_by('id')]
    delimiter = u', '
    return delimiter.join(collocations)

def entry_with_orth_variants(obj):
    if obj.homonym_order:
        h = u' %s' % unicode(obj.homonym_order)
    else:
        h = u''
    x = _orth_vars(obj)
    e = obj.civil_equivalent
    if e:
        result = u'%s%s (%s%s)' % (x, h, e, h)
    else:
        result = u'%s%s' % (x, h)
    return result

entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'

def meaning_with_entry(obj):
    econtainer = obj.entry_container
    if econtainer:
        ent = entry_with_orth_variants(econtainer)
    else:
        cgcontainer = obj.collogroup_container
        if cgcontainer:
            ent = _collocations(cgcontainer)
        else:
            ent = u'(БЕСХОЗНОЕ ЗНАЧЕНИЕ)'
    return u'%s [%s] %s' % (ent, obj.id, obj.meaning)

meaning_with_entry.admin_order_field = 'entry_container'
meaning_with_entry.short_description = u'значение'

def example_with_entry(obj):
    return u'%s [%s] %s' % (meaning_with_entry(obj.meaning), obj.id, obj.example)

def meaning_for_example(obj):
    m = obj.meaning
    return u'%s [%s]%s' % (m.meaning, m.id, u'*' if m.metaphorical else u'')

def entry_for_example(obj):
    m = obj.meaning
    e = m.entry_container
    if e:
        r = entry_with_orth_variants(e)
        i = u' [%s]' % e.id
    else:
        cg = m.collogroup_container
        if cg:
            r = _collocations(cg)
        else:
            r = u'(БЕСХОЗНОЕ ЗНАЧЕНИЕ)'
        i = u''
    return u'%s%s' % (r, i)




from slavdict.dictionary.models import OrthographicVariant
class OrthVar_Inline(admin.StackedInline):
    model = OrthographicVariant
    extra = 0
    fieldsets = (
        (None, {
            'fields': (('idem', 'no_ref_entry'),),
            }),
        )




from slavdict.dictionary.models import Etymology
ETYMOLOGY_FIELDSETS = (
    (u'Является этимоном для др. этимона',
        {'fields': ('etymon_to', 'questionable'),
        'classes': ('collapse',)}
        ),
    (None,
        {'fields': (
            'language',
            ('text', 'unitext', 'corrupted'),
            'translit',
            'meaning',
            'gloss',
            'unclear',
            'mark',
            'source')}
        ),
    (u'Примечание к этимологии',
        {'fields': ('additional_info',),
        'classes': ('collapse',)}
        ),
    )
class Etymology_Inline(admin.StackedInline):
    model = Etymology
    extra = 0
    fieldsets = ETYMOLOGY_FIELDSETS




class EtymologyForCollocation_Inline(admin.StackedInline):
    model = Etymology
    extra = 1
    fieldsets = ETYMOLOGY_FIELDSETS




from slavdict.dictionary.models import GreekEquivalentForExample
class GreekEquivalentForExample_Inline(admin.StackedInline):
    model = GreekEquivalentForExample
    extra = 0
    fieldsets = (
        (None, {
            'fields': (
                ('unitext', 'corrupted'),
                'mark',
                'source',
                'initial_form',
                ),
            }),
        (u'Примечание к параллели',
            {'fields': ('additional_info',),
            'classes': ('collapse',)}
            ),
        )





from slavdict.dictionary.models import Example

funcTemp = lambda self: meaning_for_example(self)
funcTemp.admin_order_field = 'meaning'
funcTemp.short_description = u'Значение'
Example.meaning_for_example = funcTemp

funcTemp = lambda self: entry_for_example(self)
funcTemp.admin_order_field = 'meaning'
funcTemp.short_description = u'Лексема / Словосоч.'
Example.entry_for_example = funcTemp

EXAMPLE_FIELDSETS = (
        (None, {'fields': (('example', 'context'), 'address_text', 'greek_eq_status')}),
        (u'Примечание к примеру', {'fields': ('additional_info',), 'classes': ('collapse',)}),
    )

class Example_Inline(admin.StackedInline):
    model = Example
    extra = 1
    fieldsets = EXAMPLE_FIELDSETS
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }

class AdminExample(admin.ModelAdmin):
    inlines = (GreekEquivalentForExample_Inline,)
    raw_id_fields = ('meaning',)
    fieldsets = ((None, {'fields': ('meaning',), 'classes': ('hidden',)}),) + EXAMPLE_FIELDSETS
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }
    ordering = ('-id',)
    list_display = ('entry_for_example', 'meaning_for_example', 'id', 'example', 'address_text', 'greek_eq_status')
    list_display_links = ('id', 'example')
    list_editable = ('greek_eq_status', 'address_text')
    list_filter = ('greek_eq_status',)
    search_fields = (
        'example',
        'address_text',
        'meaning__meaning',
        'meaning__gloss',
        'meaning__entry_container__civil_equivalent',
        'meaning__entry_container__orthographic_variants__idem',
        'meaning__collogroup_container__collocation_set__civil_equivalent',
        'meaning__collogroup_container__collocation_set__collocation',
        )
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminExample.has_add_permission = staff_has_add_permission
AdminExample.has_change_permission = staff_has_change_permission
AdminExample.has_delete_permission = staff_has_delete_permission

admin.site.register(Example, AdminExample)
ui.register(Example, AdminExample)




from slavdict.dictionary.models import MeaningContext
class MeaningContext_Inline(admin.StackedInline):
    model = MeaningContext
    extra = 0
    fieldsets = ((None, {'fields': ('context', ('left_text', 'right_text'),)}),)




from slavdict.dictionary.models import Meaning
Meaning.__unicode__=lambda self:meaning_with_entry(self)
class AdminMeaning(admin.ModelAdmin):
    inlines = (
        MeaningContext_Inline,
        Example_Inline,
        )
    raw_id_fields = (
        'entry_container',
        'collogroup_container',
        'link_to_entry',
        'link_to_collogroup',
        'link_to_meaning',
        'cf_entries',
        'cf_collogroups',
        'cf_meanings'
    )
    fieldsets = (
            (u'То, к чему значение относится',
                {'fields': (('entry_container', 'collogroup_container'), 'parent_meaning'),
                 'classes': ('hidden',)}),
            (u'См.',
                {'fields': (('link_to_entry', 'link_to_collogroup'), 'link_to_meaning'),
                'classes': ('collapse',)}),
            (u'Ср.',
                {'fields': (('cf_entries', 'cf_collogroups'), 'cf_meanings'),
                'classes': ('collapse',)}),
            (u'В роли сущ.',
                {'fields': ('substantivus', 'substantivus_type'),
                'classes': ('collapse',)}),
            (None,
                {'fields': ('metaphorical', 'meaning', 'gloss')}),
            (None, { 'fields': tuple(), 'classes': ('blank',) }),
            (u'Примечание к значению',
                {'fields': ('additional_info',),
                'classes': ('collapse',)}),
        )
    save_on_top = True
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})},
        }
    filter_horizontal = ('cf_entries', 'cf_collogroups', 'cf_meanings')
    ordering = ('-id',)
    list_display = ('id', '__unicode__')
    list_display_links = list_display
    search_fields = (
        'entry_container__civil_equivalent',
        'entry_container__orthographic_variants__idem',
        'collogroup_container__collocation_set__civil_equivalent',
        'collogroup_container__collocation_set__collocation',
        'meaning',
        'gloss',
        )
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminMeaning.has_add_permission = staff_has_add_permission
AdminMeaning.has_change_permission = staff_has_change_permission
AdminMeaning.has_delete_permission = staff_has_delete_permission

class AdminMeaningUI(AdminMeaning):
    pass
AdminMeaningUI.fieldsets = copy.deepcopy(AdminMeaning.fieldsets)
AdminMeaningUI.fieldsets = AdminMeaningUI.fieldsets[0:1] + AdminMeaningUI.fieldsets[3:]

admin.site.register(Meaning, AdminMeaning)
ui.register(Meaning, AdminMeaningUI)




from slavdict.dictionary.models import Participle
class Participle_Inline(admin.StackedInline):
    model = Participle
    extra = 1
    fieldsets = ((None, { 'fields': ('tp', 'idem') }),)




from slavdict.dictionary.models import Entry
Entry.__unicode__ = lambda self: entry_with_orth_variants(self)
class AdminEntry(admin.ModelAdmin):
    raw_id_fields = (
        'derivation_entry',
        'link_to_entry',
        'link_to_collogroup',
        'link_to_meaning',
        'cf_entries',
        'cf_collogroups',
        'cf_meanings',
    )
    fieldsets = (
        (None, {
            'fields': (('reconstructed_headword', 'questionable_headword'),),
            }),
        (None, {
            'fields': ('civil_equivalent',),
            }),
        (u'Омонимия', {
            'fields': ('homonym_order', 'homonym_gloss'),
            'classes': ('collapse',) } ),
        (None, {
            'fields': ('part_of_speech',),
            }),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (None, { # Для сущ. и прил.
            'fields': ('uninflected',),
            'classes': ('hidden noun adjective',) } ),
        (None, { # Для сущ.
            'fields': ('genitive', 'gender', 'tantum'),
            'classes': ('hidden noun',) } ),
        (None, { # Для имен собств.
            'fields': ('onym', 'canonical_name', 'nom_sg'),
            'classes': ('hidden noun',) } ),
        (None, { # Для прил.
            'fields': ('short_form', 'possessive'),
            'classes': ('hidden adjective',) } ),
        (None, { # Для глаг.
            'fields': ('sg1', 'sg2'),
            'classes': ('hidden verb',) } ),
        (None, { # Для прич.
            'fields': ('participle_type',),
            'classes': ('hidden participle',) } ),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (None, { 'fields': ('derivation_entry',) }),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (u'См.',
            {'fields': ('link_to_entry', 'link_to_collogroup', 'link_to_meaning'),
            'classes': ('collapse',)}),
        (u'Ср.',
            {'fields': ('cf_entries', 'cf_collogroups', 'cf_meanings'),
            'classes': ('collapse',)}),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (u'Примечание к статье', {
            'fields':  ('additional_info',),
            'classes': ('collapse',) }),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (None, { 'fields': ('status',) }),
        )
    inlines = (
        OrthVar_Inline,
        Participle_Inline,
        Etymology_Inline,
        )
    list_display = (
        'id',
        'civil_equivalent',
        '__unicode__',
        'duplicate',
        'editor',
        'status',
        'part_of_speech',
        )
    list_display_links = (
        'id',
        'civil_equivalent',
        '__unicode__',
        )
    list_filter = (
        'editor',
        'status',
        'part_of_speech',
        'uninflected',
        'gender',
        'tantum',
        'onym',
        'canonical_name',
        'possessive',
        'transitivity',
        'participle_type',
        )
    list_editable = (
        'duplicate',
        'editor',
        'status',
        )
    search_fields = ('civil_equivalent',)# 'orthographic_variants__idem')
    # При переходе к моделям, соотносящимся с основной как "много к одному"
    # в результатах поиска возможны дубликаты.
    # См. http://code.djangoproject.com/ticket/15839

    filter_horizontal = ('cf_entries', 'cf_collogroups', 'cf_meanings')
    ordering = ('-id',)
    save_on_top = True
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminEntry.has_add_permission = staff_has_add_permission
AdminEntry.has_change_permission = staff_has_change_permission
AdminEntry.has_delete_permission = superuser_has_delete_permission


class AdminEntryADMIN(AdminEntry):
    pass

AdminEntryADMIN.fieldsets = copy.deepcopy(AdminEntry.fieldsets)
AdminEntryADMIN.fieldsets[-1][1]['fields'] = ('editor', 'status', 'antconc_query')

class AdminEntryUI(AdminEntry):
    pass

AdminEntryUI.fieldsets = AdminEntry.fieldsets[:14] + AdminEntry.fieldsets[16:]

admin.site.register(Entry, AdminEntryADMIN)
ui.register(Entry, AdminEntryUI)




from slavdict.dictionary.models import Collocation
#class AdminCollocation(admin.ModelAdmin):
#    inlines = (EtymologyForCollocation_Inline,)
#    fieldsets = (
#            (None, {'fields': ('collocation', 'civil_equivalent')}),
#        )
#    class Media:
#        css = {"all": ("fix_admin.css",)}
#        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
#    def response_add(self, request, obj, post_url_continue='/'):
#        post_url_continue = obj.host_entry.get_absolute_url()
#        return HttpResponseRedirect(post_url_continue + 'intermed/')
#    def response_change(self, request, obj):
#        post_url_continue = obj.host_entry.get_absolute_url()
#        return HttpResponseRedirect(post_url_continue + 'intermed/')
#
#AdminCollocation.has_add_permission = staff_has_add_permission
#AdminCollocation.has_change_permission = staff_has_change_permission
#AdminCollocation.has_delete_permission = staff_has_delete_permission
#
#admin.site.register(Collocation, AdminCollocation)
#ui.register(Collocation, AdminCollocation)

class Collocation_Inline(admin.StackedInline):
    model = Collocation
    extra = 1
    fieldsets = (
            (None, {'fields': ('collocation', 'civil_equivalent')}),
        )




from slavdict.dictionary.models import CollocationGroup
CollocationGroup.__unicode__=lambda self: _collocations(self)
class AdminCollocationGroup(admin.ModelAdmin):
    inlines = (Collocation_Inline,)
    raw_id_fields = (
        'base_meaning',
        'base_entry',
        'link_to_entry',
        'link_to_meaning',
        'cf_entries',
        'cf_meanings',
    )
    fieldsets = (
            (None,
                {'fields': (('base_meaning', 'base_entry'),),
                'classes': ('hidden',)}),
            (u'См.',
                {'fields': ('link_to_entry', 'link_to_meaning'),
                'classes': ('collapse',)}),
            (u'Ср.',
                {'fields': ('cf_entries', 'cf_meanings'),
                'classes': ('collapse',)}),
        )
    ordering = ('-id',)
    filter_horizontal = ('cf_entries', 'cf_meanings')
    list_display = ('id', '__unicode__')
    list_display_links = list_display
    search_fields = ('collocation_set__civil_equivalent', 'collocation_set__collocation')
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminCollocationGroup.has_add_permission = staff_has_add_permission
AdminCollocationGroup.has_change_permission = staff_has_change_permission
AdminCollocationGroup.has_delete_permission = staff_has_delete_permission

class AdminCollocationGroupUI(AdminCollocationGroup):
    pass
AdminCollocationGroupUI.fieldsets = copy.deepcopy(AdminCollocationGroup.fieldsets)
AdminCollocationGroupUI.fieldsets = AdminCollocationGroupUI.fieldsets[0:1]

admin.site.register(CollocationGroup, AdminCollocationGroup)
ui.register(CollocationGroup, AdminCollocationGroupUI)
