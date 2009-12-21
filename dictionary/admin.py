# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.dictionary.models import (
    
    Entry,
    Lexeme,
    OrthographicVariant,

    Noun,
    ProperNoun,

)

class Lexeme_Inline(admin.StackedInline):
    
    model = Lexeme
    max_num = 1


class OrthVar_InLine(admin.StackedInline):
    
    model = OrthographicVariant
    extra = 2
    fieldsets = (
        (None, { 'fields': ('idem', 'frequency', 'is_headword', ('is_reconstructed', 'is_approved'), 'is_factored_out') }),
        )


class ProperNoun_Inline(admin.StackedInline):
    
    model = ProperNoun
    max_num = 1


def entry_with_orth_variants(obj):

    orth_vars = [unicode(i) for i in obj.orthographic_variants.all().order_by('-is_headword','idem')]
    delimiter = u', '
    x = delimiter.join(orth_vars)
    return u'%s (%s)' % (obj.civil_equivalent, x)

entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'


admin.site.register(
    Noun,
    inlines = (
        ProperNoun_Inline,
    ),
)
admin.site.register(
    Entry,
    inlines = (
        OrthVar_InLine,
        Lexeme_Inline,
    ),
#    list_display = (
#        entry_with_orth_variants,
#        'part_of_speech',
#    ),
#    list_filter = (
#        'part_of_speech',
#    ),
)
