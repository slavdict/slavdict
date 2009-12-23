# -*- coding: UTF-8 -*-
from django.db import models
from cslav_dict.directory.models import (
    
    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    SubcatFrame,

    )


class Entry(models.Model):
    
    civil_equivalent = models.CharField(
        u'гражданское написание',
        max_length = 40,
        )
    
    # orthographic_variants

    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        verbose_name = u'часть речи',
        )

    def __unicode__(self):
        return self.civil_equivalent

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'словарные статьи'


class OrthographicVariant(models.Model):
    
    # словарная статья, к которой относиться данный орф. вариант
    entry          = models.ForeignKey(
        Entry,
        verbose_name = u'словарная статья',
        related_name = 'orthographic_variants'
        )
    
    # сам орфографический вариант
    idem                = models.CharField(
        u'написание',
        max_length=40,
        )
    
    # является ли данное слово реконструкцией (реконструированно, так как не встретилось в корпусе)
    is_reconstructed    = models.BooleanField(u'является реконструкцией')

    # в связке с полем реконструкции (is_reconstructed)
    # показывает, утверждена ли реконструкция или нет
    is_approved         = models.BooleanField(u'одобренная реконструкция')

    # является ли данный орфографический вариант основным
    is_headword         = models.BooleanField(u'основной орфографический вариант')

    # является ли орф. вариант только общей частью словоформ 
    # (напр., "вонм-" для "вонми", "вонмем" и т.п.)
    # на конце автоматически добавляется дефис, заносить в базу без дефиса
    is_factored_out     = models.BooleanField(u'общая часть нескольких слов или словоформ')

    # частота встречаемости орфографического варианта
    # ? для факторизантов не важна ?
    frequency           = models.PositiveIntegerField(
        u'частота',
        blank = True,
        null  = True,
        )

    def __unicode__(self):
        return self.idem

    class Meta:
        verbose_name = u'орфографический вариант'
        verbose_name_plural = u'орфографические варианты'


class Noun(models.Model):
    
    entry = models.OneToOneField(
        Entry,
        verbose_name = u'словарная статья',
        )

    uninflected = models.BooleanField(
        u'неизменяемое',
        )
    
    plurale_tantum = models.BooleanField(
        u'plurale tantum',
        )

    singulare_tantum = models.BooleanField(
        u'singulare tantum',
        )

    gender = models.ForeignKey(
        Gender,
        verbose_name = u'грам. род',
        )

    genitive = models.CharField(
        u'окончание Р.п.',
        max_length = 3,
        help_text = u'само окончание без дефиса в начале'
        )
    
    def __unicode__(self):
        return u'<Noun %s>' % self.id

    class Meta:
        verbose_name = u'существительное'
        verbose_name_plural = u'существительные'


class ProperNoun(models.Model):

    noun = models.OneToOneField(Noun)

    onym = models.ForeignKey(
        Onym,
        verbose_name = u'тип имени собственного',
        )

    # counterpart 

    def __unicode__(self):
        return u'<Имя собственное %s>' % self.id

    class Meta:
        verbose_name = u'имя собственное'
        verbose_name_plural = u'имена собственные'
        

class Meaning(models.Model):
    
    order = models.IntegerField(
        u'номер',
        )
    
    meaning = models.TextField(
        u'значение',
        )

    metaphorical = models.BooleanField(
        u'метафорическое',
        )

    # greek_equivalent

    gloss = models.TextField(
        u'толкование',
        )

    subcat_frames = models.ManyToManyField(
        SubcatFrame,
        verbose_name = u'модель управления',
        )

    def __unicode__(self):
        
        return self.meaning

    class Meta:
        
        verbose_name = u'значение'
        verbose_name_plural = u'значения'


   
class Example(models.Model):
    
    example = models.TextField(
        u'пример',
        )

    # address # нужно учесть диапазоны вроде: 12-13 стихи

    translation = models.TextField(
        u'перевод',
        )

    meanings = models.ManyToManyField(Meaning)

    # greek_equivalent

    def __unicode__(self):
        
        return self.example

    class Meta:
        
        verbose_name = u'пример'
        verbose_name_plural = u'примеры'


