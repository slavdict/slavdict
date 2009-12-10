# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.dictionary.models import (
    Entry,
    OrthographicVariant,
    PartOfSpeech
)

class OrthVar_InLine(admin.StackedInline):
    model = OrthographicVariant
    extra = 2
    fieldsets = (
        (None, { 'fields': ('idem', 'frequency', 'is_headword', ('is_reconstructed', 'is_approved'), 'is_factored_out') }),
        )

def entry_with_orth_variants(self):
    orth_vars = [unicode(i) for i in self.orthographic_variants.all().order_by('-is_headword','idem')]
    delimiter = u', '
    ov = delimiter.join(orth_vars)
    return u'%s (%s)' % (self.civil_equivalent, ov)
entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'

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
admin.site.register(PartOfSpeech)
