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

# #############################

class Entry(models.Model):
    
    civil_equivalent = models.CharField(
        u'гражданское написание',
        max_length = 40,
        )
    
    # orthographic_variants

    def __unicode__(self):
        return self.civil_equivalent

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'словарные статьи'


class Lexeme(models.Model):

    entry = models.OneToOneField(Entry)

    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        verbose_name = u'часть речи',
        )

    def __unicode__(self):
        return u'<Lexeme %s>' % self.id

    class Meta:
        verbose_name = u'лексема'
        verbose_name_plural = u'лексемы'


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
    
    lexeme = models.OneToOneField(
        Lexeme,
        u'лексема',
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
    
    def __unicode__(self):
        return u'<Noun %s>' % self.id

    class Meta:
        verbose_name = u'существительное'


class Onym(TermDirectory):
    
    class Meta(TermDirectory.Meta):
        verbose_name = u'тип имени собственного'
        verbose_name_plural = u'справочник типов имени собственного'


class ProperNoun(Noun):

    onym = models.ForeignKey(
        Onym,
        u'тип имени собственного',
        )

    # counterpart 
        

class Meaning(models.Model):
    
    meaning = models.TextField()
    # greek_equivalent
   
class Example(models.Model):
    
    example = models.TextField()
    # address # нужно учесть диапазоны вроде: 12-13 стихи
    translation = models.TextField()
    meanings = models.ManyToManyField(Meaning)



