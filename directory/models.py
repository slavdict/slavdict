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
        verbose_name_plural = u'части речи'


class Gender(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'грамматический род'
        verbose_name_plural = u'значения грамматического рода'


class Tantum(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'tantum'
        verbose_name_plural = u'tantum'


class Onym(TermDirectory):
    
    class Meta(TermDirectory.Meta):
        verbose_name = u'тип имени собственного'
        verbose_name_plural = u'типы имени собственного'


class SyntActant(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'синтаксический актант'
        verbose_name_plural = u'синтаксические актанты'


class SubcatFrame(models.Model):

    actant1 = models.ForeignKey(
        SyntActant,
        verbose_name = u'1-й актант',
        related_name = 'actant1_set',
        )

    actant2 = models.ForeignKey(
        SyntActant,
        verbose_name = u'2-й актант',
        related_name = 'actant2_set',
        blank = True,
        null = True,
        )

    actant3 = models.ForeignKey(
        SyntActant,
        verbose_name = u'3-й актант',
        related_name = 'actant3_set',
        blank = True,
        null = True,
        )

    actant4 = models.ForeignKey(
        SyntActant,
        verbose_name = u'4-й актант',
        related_name = 'actant4_set',
        blank = True,
        null = True,
        )

    def __unicode__(self):
        
        rtn = self.actant1.abbreviation
        if self.actant2:
            rtn = u'%s, %s' % (rtn, self.actant2.abbreviation)
        if self.actant3:
            rtn = u'%s, %s' % (rtn, self.actant3.abbreviation)
        if self.actant4:
            rtn = u'%s, %s' % (rtn, self.actant4.abbreviation)
        return rtn

    class Meta:
        verbose_name = u'модель управления'
        verbose_name_plural = u'модели управления'

