# -*- coding: UTF-8 -*-
from django.contrib import admin
from cslav_dict.dictionary.models import (
    DictEntry,
    OrthographicVariant,
)

class OrthVar_InLine(admin.StackedInline):
    model = OrthographicVariant
    extra = 2

admin.site.register(
    DictEntry,
    inlines = (
        OrthVar_InLine,
    )
)
