# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.dictionary.models import (
    
    Entry,
    OrthographicVariant,

    Lexeme,
    ProperNoun,
    Etymology,

)

class Entry_Inline(admin.StackedInline):
    model = Entry
    max_num = 1
    
class OrthVar_InLine(admin.StackedInline):
    model = OrthographicVariant
    extra = 1
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

admin.site.register(Etymology)

class ProperNoun_Inline(admin.StackedInline):
    model = ProperNoun
    max_num = 1
#    fieldsets = (
#        (None, {
#            'fields':  ('onym',),
#            'classes': ('collapse',),
#            }),
#        )


def entry_with_orth_variants(obj):
    orth_vars = [unicode(i) for i in obj.orthographic_variants.all().order_by('-is_headword','idem')]
    delimiter = u', '
    x = delimiter.join(orth_vars)
    return u'%s (%s)' % (obj.civil_equivalent, x)

entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'


admin.site.register(
    Lexeme,
    fieldsets = (
        (None, {
            'fields': (
                'uninflected',
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
                ),
            'classes': (
                'collapse',
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
        ),
    inlines = (
        ProperNoun_Inline,
        ),
)
admin.site.register(
    Entry,
    inlines = (
        OrthVar_InLine,
        ),
    list_display = (
        entry_with_orth_variants,
        'part_of_speech',
        ),
    list_filter = (
        'part_of_speech',
        ),
)

