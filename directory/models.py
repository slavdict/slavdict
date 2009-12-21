# -*- coding: UTF-8 -*-
from django.db import models

class TermDirectory(models.Model):
    
    name = models.CharField(
        u'название',
        max_length=20,
        )

    abbreviation = models.CharField(
        u'сокращение',
        max_length=8,
        )

    def __unicode__(self):
        return u'%s [%s]' % (self.name, self.abbreviation)

    class Meta:
        abstract = True
        ordering = ('name',)


class PartOfSpeech(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'часть речи'
        verbose_name_plural = u'список частей речи'


class Gender(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'грамматический род'
        verbose_name_plural = u'cписок значений грамматического рода'


class Tantum(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'tantum'
        verbose_name_plural = u'tantum'


class Onym(TermDirectory):
    
    class Meta(TermDirectory.Meta):
        verbose_name = u'тип имени собственного'
        verbose_name_plural = u'справочник типов имени собственного'



