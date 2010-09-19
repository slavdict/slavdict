# -*- coding: UTF-8 -*-
from django.contrib import admin

from slavdict.dictionary.models import CivilEquivalent
admin.site.register(CivilEquivalent)

from slavdict.dictionary.models import OrthographicVariant
class OrthVar_Inline(admin.StackedInline):
    model = OrthographicVariant
    extra = 0
    fieldsets = (
        (None, {
            'fields': (
                (
                'idem',
                'is_headword',
                ),
                (
                'is_reconstructed',
                'is_approved',
                'frequency',
                ),
                #'is_factored_out'
                ),
            }),
        )

from slavdict.dictionary.models import Etymology
admin.site.register(Etymology)

from slavdict.dictionary.models import ProperNoun
class ProperNoun_Inline(admin.StackedInline):
    model = ProperNoun
    max_num = 1
#    fieldsets = (
#        (None, {
#            'fields':  ('onym',),
#            'classes': ('collapse',),
#            }),
#        )

from slavdict.dictionary.models import Address
admin.site.register(Address)

from slavdict.dictionary.models import Example
class Example_Inline(admin.StackedInline):
    model = Example
    extra = 0

def entry_with_orth_variants(obj):
    orth_vars = [unicode(i) for i in obj.orthographic_variants.all().order_by('-is_headword','idem')]
    delimiter = u', '
    x = delimiter.join(orth_vars)
    return u'%s (%s)' % (obj.civil_equivalent.text, x)

entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'

def meaning_with_entry(obj):
    ent = entry_with_orth_variants(obj.entry_container)
    return u'%s %s. %s' % (
        ent,
        obj.order,
        obj.meaning,
        )

meaning_with_entry.admin_order_field = 'entry_container'
meaning_with_entry.short_description = u'значение'

from slavdict.dictionary.models import Meaning
admin.site.register(
    Meaning,
    inlines = (
        Example_Inline,
        ),
    list_display = (
        meaning_with_entry,
        ),
    )

from slavdict.dictionary.models import Entry
admin.site.register(
    Entry,
    fieldsets = (
        (None, {
            'fields': (
                'civil_equivalent',
                'part_of_speech',
                'word_forms_list',
                ),
            }),
        (u'административная инормация', {
            'fields': (
                ('editor', 'status', 'percent_status',),
                ),
            }),
        (u'для существительных', {
            'fields': (
                'genitive',
                'gender',
                'tantum',
                ),
            'classes': (
                'collapse',
                ),
            }),
        (u'для прилагательных', {
            'fields': (
                'short_form',
                'possessive',
                ),
            'classes': (
                'collapse',
                ),
            }),
        (None, {
            'fields': (
                'uninflected',
                ),
            }),
        (u'для глаголов', {
            'fields': (
                'transitivity',
                'sg1',
                'sg2',
                ),
            'classes': (
                'collapse',
                ),
            }),
        (u'деривационный источник', {
            'fields': (
                'derivation_entry',
                'derivation_entry_meaning',
                ),
            'classes': (
                'collapse',
                ),
            }),
        (u'В качестве значений ссылка', {
            'fields': ('link_to_entry', 'link_to_phu',),
            'classes': ('collapse',) } ),
        (None, {
            'fields': ('additional_info', 'antconc_query',)}),
        ),
    inlines = (
        OrthVar_Inline,
        ProperNoun_Inline,
        ),
    list_display = (
        entry_with_orth_variants,
        'part_of_speech',
        'editor',
        'status',
        ),
    list_filter = (
        'part_of_speech',
        'editor',
        'status',
        ),
    save_on_top = True,
)

from slavdict.dictionary.models import SynonymGroup
admin.site.register(SynonymGroup)

from slavdict.dictionary.models import PhraseologicalUnit
admin.site.register(PhraseologicalUnit)
