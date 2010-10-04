# -*- coding: UTF-8 -*-
from django.conf import settings
from django import forms
from django.db import models
from django.contrib import admin


def entry_with_orth_variants(obj):
    orth_vars = [unicode(i) for i in obj.orthographic_variants.all().order_by('-is_main_variant','idem')]
    delimiter = u', '
    x = delimiter.join(orth_vars)
    try:
        e = obj.civil_equivalent.text
    except:
        e = u''
    return u'%s (%s)' % (e, x)

entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'

def meaning_with_entry(obj):
    container = obj.entry_container
    if not container:
        container = obj.collocation_container
    if container:
        ent = entry_with_orth_variants(container)
    else:
        ent = u'(БЕСХОЗНОЕ ЗНАЧЕНИЕ)'
    return u'%s [%s] %s' % (ent, obj.id, obj.meaning)

meaning_with_entry.admin_order_field = 'entry_container'
meaning_with_entry.short_description = u'значение'

def example_with_entry(obj):
    return u'%s [%s] %s' % (meaning_with_entry(obj.meaning), obj.id, obj.example)


from slavdict.dictionary.models import CivilEquivalent
admin.site.register(CivilEquivalent)

from slavdict.dictionary.models import OrthographicVariant
class OrthVar_Inline(admin.StackedInline):
    model = OrthographicVariant
    extra = 1
    fieldsets = (
        (None, {
            'fields': (('idem', 'is_reconstructed'),),
            }),
        )

from slavdict.dictionary.models import Etymology
class Etymology_Inline(admin.StackedInline):
    model = Etymology
    extra = 0
    fieldsets = (
        (u'Дочерняя этимология',
            {'fields': ('parent_etymology',),
            'classes': ('collapse',)}
            ),
        (None,
            {'fields': ('language', ('text', 'translit'), ('meaning', 'gloss'), ('unclear_etymology', 'mark'))}
            ),
        (u'Доп. инфо.',
            {'fields': ('additional_info',),
            'classes': ('collapse',)}
            ),
        )

from slavdict.dictionary.models import GreekEquivalentForMeaning
class GreekEquivalentForMeaning_Inline(admin.StackedInline):
    model = GreekEquivalentForMeaning
    extra = 0
    fieldsets = (
        (None, {
            'fields': (('text', 'mark'),),
            }),
        )

from slavdict.dictionary.models import GreekEquivalentForExample
class GreekEquivalentForExample_Inline(admin.StackedInline):
    model = GreekEquivalentForExample
    extra = 0
    fieldsets = (
        (None, {
            'fields': (('text', 'mark', 'position'),),
            }),
        )

from slavdict.dictionary.models import ProperNoun
class ProperNoun_Inline(admin.StackedInline):
    model = ProperNoun
    extra = 0
    max_num = 1




from slavdict.dictionary.models import Example
Example.__unicode__=lambda self:example_with_entry(self)

EXAMPLE_FIELDSETS = (
        (None, {'fields': (('example', 'address_text'),)}),
        (u'Доп. инфо.', {'fields': ('additional_info',), 'classes': ('collapse',)}),
    )

class Example_Inline(admin.StackedInline):
    model = Example
    extra = 1
    fieldsets = EXAMPLE_FIELDSETS
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }

class AdminExample(admin.ModelAdmin):
    inlines = (GreekEquivalentForExample_Inline,)
    fieldsets = ((None, {'fields': ('meaning',)}),) + EXAMPLE_FIELDSETS
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }
    ordering = ('-id',)
    class Media:
        css = {"all": (settings.MEDIA_URL + "fix_admin.css",)}

admin.site.register(Example, AdminExample)




from slavdict.dictionary.models import MeaningContext
class MeaningContext_Inline(admin.StackedInline):
    model = MeaningContext
    extra = 0

from slavdict.dictionary.models import Meaning
Meaning.__unicode__=lambda self:meaning_with_entry(self)
class AdminMeaning(admin.ModelAdmin):
    inlines = (
        Example_Inline,
        GreekEquivalentForMeaning_Inline,
        MeaningContext_Inline,
        )
    fieldsets = (
            (u'То, к чему значение относится',
                {'fields': (('entry_container', 'collocation_container'),)}),
            (u'Если является подзначением',
                {'fields': ('parent_meaning',),
                'classes': ('collapse',)}),
            (u'Если вместо значения ссылка',
                {'fields': ('link_to_meaning', ('link_to_entry', 'link_to_collocation')),
                'classes': ('collapse',)}),
            (None,
                {'fields': ('metaphorical', ('meaning', 'gloss'))}),
            (u'Доп. инфо.',
                {'fields': ('additional_info',),
                'classes': ('collapse',)}),
        )
    save_on_top = True
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }
    ordering = ('-id',)

    class Media:
        css = {"all": (settings.MEDIA_URL + "fix_admin.css",)}

admin.site.register(Meaning, AdminMeaning)


from slavdict.dictionary.models import Entry
Entry.__unicode__=lambda self: entry_with_orth_variants(self)
class AdminEntry(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('part_of_speech', 'editor'),),
            }),
        (u'Для сущ.', {
            'fields': (('genitive', 'gender', 'tantum'),),
            'classes': ('collapse',) } ),
        (u'Для прил.', {
            'fields': (('short_form', 'possessive'),),
            'classes': ('collapse',) } ),
        (None, {
            'fields': ('uninflected',),}),
        (u'Для глаг.', { 'fields': (('sg1', 'sg2'),), 'classes': ('collapse',) } ),
        (u'Образовано от', { 'fields': ( 'derivation_entry',), 'classes': ( 'collapse',), }),
        (u'Вместо значений ссылка', {
            'fields': (('link_to_entry', 'link_to_collocation'),),
            'classes': ('collapse',) } ),
        (u'Доп. инфо.', {
            'fields':  ('additional_info',),
            'classes': ('collapse',) }),
        (u'Адм. инфо.', {
            'fields': (('status', 'percent_status', 'grequiv_status'),),
            'classes': ('collapse',) }),
        )
    inlines = (
        OrthVar_Inline,
        Etymology_Inline,
        ProperNoun_Inline,
        )
    list_display = (
        'civil_equivalent',
        entry_with_orth_variants,
        'part_of_speech',
        'editor',
        'id',
        )
    list_filter = (
        'editor',
        )
    ordering = ('-id',)
    save_on_top = True
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }

    class Media:
        css = {"all": (settings.MEDIA_URL + "fix_admin.css",)}

admin.site.register(Entry, AdminEntry)

from slavdict.dictionary.models import SynonymGroup
admin.site.register(SynonymGroup)


CollocationVariant_Inline = OrthVar_Inline
CollocationVariant_Inline.verbose_name = u'словосочетание'
CollocationVariant_Inline.verbose_name_plural = u'Группа словосочетаний'

from slavdict.dictionary.models import Collocation
Collocation.__unicode__=lambda self: entry_with_orth_variants(self)
admin.site.register(
    Collocation,
    inlines = (CollocationVariant_Inline,),
    fieldsets = (
            (None,
                {'fields': ('base_meaning',)}),
            (u'Если вместо значений ссылка',
                {'fields': ('link_to_entry',),
                'classes': ('collapse',)}),
        ),
    ordering = ('-id',),
    )
