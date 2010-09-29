# -*- coding: UTF-8 -*-
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
    extra = 0
    fieldsets = (
        (None, {
            'fields': (
                ('idem', 'is_main_variant', 'is_reconstructed'),
                ),
            }),
        )

from slavdict.dictionary.models import Etymology
class Etymology_Inline(admin.StackedInline):
    model = Etymology
    extra = 0

from slavdict.dictionary.models import GreekEquivalentForMeaning
class GreekEquivalentForMeaning_Inline(admin.StackedInline):
    model = GreekEquivalentForMeaning
    extra = 0

from slavdict.dictionary.models import GreekEquivalentForExample
class GreekEquivalentForExample_Inline(admin.StackedInline):
    model = GreekEquivalentForExample
    extra = 0

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

from slavdict.dictionary.models import Example
Example.__unicode__=lambda self:example_with_entry(self)

class Example_Inline(admin.StackedInline):
    model = Example
    extra = 0

admin.site.register(
    Example,
    inlines = (GreekEquivalentForExample_Inline,),
    )

from slavdict.dictionary.models import MeaningContext
class MeaningContext_Inline(admin.StackedInline):
    model = MeaningContext
    extra = 0

from slavdict.dictionary.models import Meaning
Meaning.__unicode__=lambda self:meaning_with_entry(self)
admin.site.register(
    Meaning,
    inlines = (
        GreekEquivalentForMeaning_Inline,
        MeaningContext_Inline,
        Example_Inline,
        ),
    fieldsets = (
            (u'То, к чему значение относится',
                {'fields': ('entry_container', 'collocation_container', 'parent_meaning'),
                'classes': ('collapse',)}),
            (u'Если вместо значения ссылка',
                {'fields': ('link_to_meaning', 'link_to_entry', 'link_to_collocation'),
                'classes': ('collapse',)}),
            (None,
                {'fields': ('metaphorical', 'meaning', 'gloss')}),
            (None,
                {'fields': ('additional_info',)}),
        ),
    )

from slavdict.dictionary.models import Entry
Entry.__unicode__=lambda self: entry_with_orth_variants(self)
admin.site.register(
    Entry,
    fieldsets = (
        (None, {
            'fields': (
                ('part_of_speech', 'civil_equivalent'),
                # 'word_forms_list',
                ),
            }),
        (u'для существительных', {
            'fields': (
                ('genitive', 'gender', 'tantum'),
                ),
            }),
        (u'для прилагательных', {
            'fields': (
                ('short_form', 'possessive'),
                ),

            }),
        (None, {
            'fields': (
                'uninflected',
                ),
            }),
        (u'для глаголов', {
            'fields': (
                ('sg1', 'sg2'),
                ),
            }),
        (u'деривационный источник', {
            'fields': (
                'derivation_entry',
                ),
            'classes': (
                'collapse',
                ),
            }),
        (u'Если вместо значений ссылка', {
            'fields': ('link_to_entry', 'link_to_collocation',),
            'classes': ('collapse',) } ),
        (None, {
            'fields': ('additional_info', 'antconc_query')}),
        (u'административная инормация', {
            'fields': (
                ('editor', 'status', 'percent_status', 'grequiv_status'),
                ),
            }),
        ),
    inlines = (
        OrthVar_Inline,
        Etymology_Inline,
        ProperNoun_Inline,
        ),
    list_display = (
        entry_with_orth_variants,
        'part_of_speech',
        'editor',
        'status',
        'grequiv_status',
        ),
    list_filter = (
        'editor',
        'status',
        'grequiv_status',
        ),
    save_on_top = True,
)

from slavdict.dictionary.models import SynonymGroup
admin.site.register(SynonymGroup)

from slavdict.dictionary.models import Collocation
Collocation.__unicode__=lambda self: entry_with_orth_variants(self)
admin.site.register(
    Collocation,
    inlines = (OrthVar_Inline,),
    fieldsets = (
            (None,
                {'fields': (('base_meaning', 'civil_equivalent'),)}),
            (u'Если вместо значений ссылка',
                {'fields': ('link_to_entry',),
                'classes': ('collapse',)}),
        ),
    )
