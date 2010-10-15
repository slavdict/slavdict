# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib import admin
from slavdict.directory.models import (

    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    Transitivity,
    SyntArgument,
    SubcatFrame,
    Language,
    EntryStatus,

)

admin.site.register(PartOfSpeech)
admin.site.register(Gender)
admin.site.register(Tantum)
admin.site.register(Onym)
admin.site.register(Transitivity)
admin.site.register(SyntArgument)
admin.site.register(SubcatFrame)
admin.site.register(Language)
admin.site.register(EntryStatus)

from slavdict.directory.models import ValueTag
class ValueTag_Inline(admin.StackedInline):
    model = ValueTag
    extra = 1

from slavdict.directory.models import TagLibrary
class AdminTagLibrary(admin.ModelAdmin):
    inlines = (ValueTag_Inline,)
    class Media:
        css = {"all": (settings.MEDIA_URL + "fix_admin2.css",)}

admin.site.register(TagLibrary, AdminTagLibrary)

from slavdict.directory.models import CategoryValue
class CategoryValue_Inline(admin.StackedInline):
    model = CategoryValue
    extra = 1

class AdminCategoryValue(admin.ModelAdmin):
    list_display = ('category', 'order', 'tag', 'slug')
    list_display_links = list_display
    class Media:
        css = {"all": (settings.MEDIA_URL + "fix_admin2.css",)}

admin.site.register(CategoryValue, AdminCategoryValue)

from slavdict.directory.models import Category
class AdminCategory(admin.ModelAdmin):
    inlines = (CategoryValue_Inline,)
    list_display = ('tag', 'slug')
    list_display_links = list_display
    class Media:
        css = {"all": (settings.MEDIA_URL + "fix_admin2.css",)}

admin.site.register(Category, AdminCategory)
