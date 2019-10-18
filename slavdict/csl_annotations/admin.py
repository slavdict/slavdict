# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import groupby

from django import forms
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe

from slavdict.csl_annotations.models import Annotation
from slavdict.csl_annotations.models import Author
from slavdict.csl_annotations.models import FixedWidthTextField
from slavdict.csl_annotations.models import Tag

admin.site.login_template = 'registration/login.html'


def get_annotation_name(self):
    return self.get_title_html() or self.get_bib_html()


def get_annotation_tags(self):
    tag_groups = []
    get_key = lambda x: x.get_category_display()
    for key, iterator in groupby(self.tags.all(), get_key):
        tags = u', '.join(u'<strong>%s</strong>' % tag.name for tag in iterator)
        tag_groups.append(u'%s: %s' % (key, tags))
    return mark_safe(u'; '.join(tag_groups))


def get_annotation_authors(self):
    return u', '.join(a for a in self.authors.all())


get_annotation_name.short_description = u'Аннотации'
get_annotation_tags.short_description = u'Ярлыки'
get_annotation_authors.short_description = u'Авторы'
Annotation._name = get_annotation_name
Annotation._tags = get_annotation_tags
Annotation._authors = get_annotation_authors


class AdminAnnotation(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            ('youtube_id', 'url'),
            'anchor',
            ('title', 'bib'),
            ('teaser', 'annotation'),
            ('tags', 'authors'),
        )}),
    )
    formfield_overrides = {
        FixedWidthTextField: {'widget': forms.Textarea(attrs={'rows': '2'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': '5'})},
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }
    ordering = ('-id',)
    list_display = ('_name', 'anchor', '_tags', '_authors')
    list_filter = ('tags', 'authors')
    search_fields = ('title', 'bib')


class AdminTag(admin.ModelAdmin):
    pass


class AdminAuthor(admin.ModelAdmin):
    formfield_overrides = {
        FixedWidthTextField: {'widget': forms.Textarea(attrs={'rows': '4'})},
    }


admin.site.register(Annotation, AdminAnnotation)
admin.site.register(Tag, AdminTag)
admin.site.register(Author, AdminAuthor)
