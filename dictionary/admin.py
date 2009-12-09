# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.dictionary.models import (
    DictEntry,
    OrthographicVariant,
    PartOfSpeech
)

class OrthVar_InLine(admin.StackedInline):
    model = OrthographicVariant
    extra = 2
    fields = (('is_reconstructed', 'is_approved'), ('is_headword', 'is_factored_out'), 'frequency')

admin.site.register(
    DictEntry,
    inlines = (
        OrthVar_InLine,
    )
)
admin.site.register(PartOfSpeech)
