# -*- coding: UTF-8 -*-
from django.db import models
from cslav_dict.directory.models import (
    
    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    Transitivity,
    SubcatFrame,
    Language,

    )

class CivilEquivalent(models.Model):
    
    text = models.CharField(
        u'гражданское написание',
        max_length = 40,
        unique = True,
        )

    def __unicode__(self):
        return self.text
    
    class Meta:
        verbose_name = u'эквивалент в гражданском написании'
        verbose_name_plural = u'слова в гражданском написании'


class Entry(models.Model):
    
    civil_equivalent = models.ForeignKey(
        CivilEquivalent,
        verbose_name = u'гражданское написание',
        )
    
    # orthographic_variants

    # lexeme (посредник к граматическим формам и свойствам)
    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        verbose_name = u'часть речи',
        )
    
    uninflected = models.BooleanField(
        u'неизменяемое',
        )
    
    # только для существительных
    tantum = models.ForeignKey(
        Tantum,
        blank = True,
        null = True,
        )

    gender = models.ForeignKey(
        Gender,
        verbose_name = u'грам. род',
        blank = True,
        null = True,
        )

    genitive = models.CharField(
        u'окончание Р.п.',
        max_length = 3,
        help_text = u'само окончание без дефиса в начале',
        blank = True,
        )
    # proper_noun

    # только для прилагательных
    short_form = models.CharField(
        u'краткая форма',
        max_length = 20,
        blank = True,
        )

    # только для глаголов
    transitivity = models.ForeignKey(
        Transitivity,
        verbose_name = u'переходность',
        blank = True,
        null = True,
        )

    sg1 = models.CharField(
        u'форма 1sg',
        max_length = 20,
        blank = True,
        )
    
    sg2 = models.CharField(
        u'форма 2sg',
        max_length = 20,
        blank = True,
        )

    def __unicode__(self):
        return self.civil_equivalent.text

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
        

class Etymology(models.Model):

    language = models.ForeignKey(
        Language,
        verbose_name = u'язык',
        )

    text = models.CharField(
        u'языковой эквивалент',
        max_length = 40,
        blank = True,
        )

    translit = models.CharField(
        u'траслит.',
        max_length = 40,
        )

    meaning = models.CharField(
        u'перевод',
        max_length = 70,
        )

    def __unicode__(self):
        return self.translit

    class Meta:
        verbose_name = u'этимология слова'
        verbose_name_plural = u'этимология слов'


class ProperNoun(models.Model):

    entry = models.ForeignKey(Entry)

    onym = models.ForeignKey(
        Onym,
        verbose_name = u'тип имени собственного',
        )

    unclear_ethymology = models.BooleanField(
        u'этимология неясна',
        )
    
    etymology = models.ManyToManyField(
        Etymology,
        verbose_name = u'этимология',
        blank = True,
        null = True,
        )

    def __unicode__(self):
        return u'<Имя собственное %s>' % self.id

    class Meta:
        verbose_name = u'имя собственное'
        verbose_name_plural = u'имена собственные'


class Meaning(models.Model):
    
    entry = models.ForeignKey(Entry)

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
        blank = True,
        )

    subcat_frames = models.ManyToManyField(
        SubcatFrame,
        verbose_name = u'модель управления',
        blank = True,
        null = True,
        )

    def __unicode__(self):
        
        return self.meaning

    class Meta:
        
        verbose_name = u'значение'
        verbose_name_plural = u'значения'


class Address(models.Model):
    
    address = models.CharField(
        u'адрес',
        max_length = 15,
        )

    def __unicode__(self):
        return u'(%s)' % self.address

    class Meta:
        verbose_name = u'адрес'
        verbose_name_plural = u'адреса'


class Example(models.Model):
    
    example = models.TextField(
        u'пример',
        )

    address = models.ForeignKey( 
        Address,
        verbose_name = u'адрес',
        )

    translation = models.TextField(
        u'перевод',
        blank = True,
        )

    meaning = models.ForeignKey(Meaning)
    # TODO: это должно быть поле ManyToMany,
    # а не FK. Соответственно, оно должно
    # иметь название во мн.ч. (meaning*s*)

    # greek_equivalent

    def __unicode__(self):
        
        return u'%s %s' % (self.address, self.example)

    class Meta:
        
        verbose_name = u'пример'
        verbose_name_plural = u'примеры'


