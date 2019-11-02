# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import groupby

from django import forms
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from slavdict.csl_annotations.models import Annotation
from slavdict.csl_annotations.models import Author
from slavdict.csl_annotations.models import FixedWidthTextField
from slavdict.csl_annotations.models import Tag
from slavdict.csl_annotations.models import TagGroup
from slavdict.csl_annotations.models import TAG_COLORS

admin.site.login_template = 'registration/login.html'


def get_annotation_name(self):
    if self.title:
        return self.get_title_with_author_html()
    return self.get_bib_html()


def get_annotation_tags(self):
    tag_groups = []
    get_category = lambda x: (x.category, x.get_category_display())
    for (catval, catname), iterator in groupby(self.tags.all(), get_category):
        tags = u'; '.join(u'<strong>%s</strong>' % tag.name for tag in iterator)
        text = u'%s: %s' % (catname, tags)
        html = u'<span style="color: %s">%s</span>' % (TAG_COLORS[catval], text)
        tag_groups.append(html)
    return mark_safe(u'; '.join(tag_groups))


def get_annotation_authors(self):
    return u', '.join(unicode(a) for a in self.authors.all())


get_annotation_name.short_description = u'Аннотация'
get_annotation_tags.short_description = u'Бирки'
get_annotation_authors.short_description = u'Авторы'
Annotation._name = get_annotation_name
Annotation._tags = get_annotation_tags
Annotation._authors = get_annotation_authors


def get_tag_groups(self):
    groups = self.groups.all()
    text = u'; '.join(group.name for group in groups) if groups else u''
    return mark_safe(text)


get_tag_groups.short_description = u'Коллекция бирок'
Tag._groups = get_tag_groups


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
    list_display = ('anchor', '_name', '_tags', '_authors')
    list_display_links = ('_name',)
    list_filter = (
        'tags', 'authors',
        ('create_date', DateTimeRangeFilter),
    )
    search_fields = ('title', 'bib')

    def save_related(self, request, form, formsets, change):
        super(AdminAnnotation, self).save_related(request, form, formsets, change)
        additional_tags = []
        tags = form.instance.tags.all()
        for tag in tags:
            while tag.parent:
                tag = tag.parent
                if tag not in tags:
                    additional_tags.append(tag)
        if additional_tags:
            form.instance.tags.add(*additional_tags)

    class Media:
        js = ("fix_admin.js",)


class AdminTagGroup(admin.ModelAdmin):
    pass


class AdminTag(admin.ModelAdmin):
    list_display = ('__unicode__', 'order', '_groups')
    list_editable = ('order',)
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }


class AdminAuthor(admin.ModelAdmin):
    formfield_overrides = {
        FixedWidthTextField: {'widget': forms.Textarea(attrs={'rows': '4'})},
    }


admin.site.register(Annotation, AdminAnnotation)
admin.site.register(Tag, AdminTag)
admin.site.register(TagGroup, AdminTagGroup)
admin.site.register(Author, AdminAuthor)
