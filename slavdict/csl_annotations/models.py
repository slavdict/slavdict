# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import markdown
from url_or_relative_url_field.fields import URLOrRelativeURLField

from django.db import models
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.utils.safestring import mark_safe


class FixedWidthTextField(CharField):
    pass


TAG_CATEGORIES = (
    ('a', u'Этап'),
    ('e', u'Регион'),
    ('i', u'Тексты'),
    ('m', u'Книга'),
    ('q', u'Материал'),
    ('u', u'Инструменты'),
)


class Author(models.Model):
    first_name = CharField(u'имя', max_length=20)
    second_name = CharField(u'отчество', max_length=30, blank=True)
    last_name = CharField(u'фамилия', max_length=30)
    title = FixedWidthTextField(u'титулы/регалии', max_length=500, blank=True)

    def __unicode__(self):
        return u'%s %s.' % (self.last_name, self.first_name[:1])

    class Meta:
        verbose_name = u'автор'
        verbose_name_plural = u'авторы'
        ordering = ('last_name', 'first_name', 'second_name')


class TagGroup(models.Model):
    name = CharField(u'название', max_length=50)
    parent_tag = ForeignKey('Tag', verbose_name=u'родительская бирка',
                            help_text=u'Бирка, к которой относится группа.')
    def __unicode__(self):
        return u'[%s] %s' % (self.parent_tag.name, self.name)

    class Meta:
        verbose_name = u'коллекция бирок'
        verbose_name_plural = u'коллекции бирок'


class Tag(models.Model):
    name = CharField(u'бирка', max_length=50)
    category = CharField(u'категрия', choices=TAG_CATEGORIES, max_length=1)
    groups = ManyToManyField(TagGroup, verbose_name=u'группа', blank=True)
    parent = ForeignKey('self', verbose_name=u'бирка-родитель', blank=True,
                        null=True)
    order = models.PositiveSmallIntegerField(
            u'порядок', default=10, help_text=u'Порядок в рамках категории')

    def __unicode__(self):
        tag = self
        hierarchy = [tag]
        while tag.parent:
            tag = tag.parent
            hierarchy.append(tag)
        hierarchy.reverse()
        hierarchy_text = u' > '.join(tag.name for tag in hierarchy)
        return u'[%s] %s' % (self.get_category_display(), hierarchy_text)

    class Meta:
        verbose_name = u'бирка'
        verbose_name_plural = u'бирки'
        ordering = ('category', 'order', 'id')


MOSTLY_FOR_VIDEOS = u'Обязательно для видео, факультативно для книг и статей'
MOSTLY_FOR_TEXTS = u'Обязательно для книг и статей, факультативно для видео'
FOR_TEXTS = u'Для книг и статей'
FOR_VIDEOS = u'Для видео'
ANCHOR_HELP = u'''

    Якорь, чтобы сослаться на текущую аннотацию из другой аннотации.<br>
    Если ссылкаться на данную аннотацию из другой нет необходимости,<br>
    то поле можно оставлять пустым.

'''
YOUTUBE_ID_NAME = u'ID видео'
YOUTUBE_ID_HELP = u'''

    Идентификатор видео на YouTube. Например, если ссылка на видео выглядит<br>
    так <i>https://www.youtube.com/watch?v=zDRRSVplgXM&t=10s</i>,
    то идентификтор<br>будет выглядеть вот так <i>zDRRSVplgXM</i>.

'''
URL_HELP = u'''

    Указывать любые ссылки кроме ютьюбовских.<br>
    Ссылки на youtube указывать в поле «%s»<br>
    в виде идентификаторов видео.

''' % YOUTUBE_ID_NAME


class Annotation(models.Model):
    title = FixedWidthTextField(u'название', max_length=200, blank=True,
                                null=True, help_text=MOSTLY_FOR_VIDEOS)
    bib = FixedWidthTextField(u'библиографическая ссылка', max_length=2000,
                              blank=True, null=True, help_text=FOR_TEXTS)
    annotation = models.TextField(u'аннотация', blank=True, null=True,
                                  unique=True, help_text=MOSTLY_FOR_TEXTS)
    teaser = models.TextField(u'тизер', blank=True, help_text=FOR_VIDEOS,
                              null=True, unique=True)
    authors = ManyToManyField(Author, verbose_name=u'авторы', blank=True)
    tags = ManyToManyField(Tag, verbose_name=u'тэги')
    anchor = models.SlugField(u'якорь', max_length=30, blank=True, null=True,
                              help_text=ANCHOR_HELP, unique=True)
    url = URLOrRelativeURLField(u'ссылка на ресурс', max_length=1000,
                                blank=True, help_text=URL_HELP,
                                null=True, unique=True)
    youtube_id = CharField(YOUTUBE_ID_NAME, max_length=20, blank=True,
                           help_text=YOUTUBE_ID_HELP, null=True, unique=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True)

    def get_title_html(self):
        html = markdown.markdown(self.title) if self.title else u''
        return mark_safe(html)

    def get_bib_html(self):
        html = markdown.markdown(self.bib) if self.bib else u''
        return mark_safe(html)

    def get_annotation_html(self):
        html = markdown.markdown(self.annotation) if self.annotation else u''
        return mark_safe(html)

    def get_teaser_html(self):
        html = markdown.markdown(self.teaser) if self.teaser else u''
        return mark_safe(html)

    def save(self, *args, **kwargs):
        for fieldname in ('title', 'bib', 'annotation', 'teaser',
                          'anchor', 'url', 'youtube_id'):
            if not getattr(self, fieldname):
                setattr(self, fieldname, None)
        super(Annotation, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title or self.bib

    class Meta:
        verbose_name = u'аннотация'
        verbose_name_plural = u'аннотации'
