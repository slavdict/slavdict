# -*- coding: UTF-8 -*-

from django.db import models

class PartOfSpeach(models.Model):
    
    name = models.CharField(max_length=20)
    abbreviation = models.CharField(max_length=8)

class InflectionClass(models.Model):
    
    pass

class DictEntry(models.Model):
    
    civil_equivalent = models.CharField(max_length=40)
    # orthographic_variants
    # part_of_speech

class OrthographicVariant(models.Model):
    
    # словарная статья, к которой относиться данный орф. вариант
    dict_entry          = models.ForeignKey(DictEntry)
    
    # сам орфографический вариант
    word                = models.CharField(max_length=40)
    
    # является ли данное слово реконструкцией (реконструированно, так как не встретилось в корпусе)
    is_reconstructed    = models.BooleanField()

    # в связке с полем реконструкции (is_reconstructed)
    # показывает, утверждена ли реконструкция или нет
    is_approved         = models.BooleanField()

    # является ли данный орфографический вариант основным
    is_headword         = models.BooleanField()

    # является ли орф. вариант только общей частью словоформ 
    # (напр., "вонм-" для "вонми", "вонмем" и т.п.)
    # на конце автоматически добавляется дефис, заносить в базу без дефиса
    is_factored_out     = models.BooleanField()

    # частота встречаемости орфографического варианта
    # ? для факторизантов не важна ?
    frequency           = models.PositiveInteger()

class Meaning(models.Model):
    
    meaning = models.TextField()
    # greek_equivalent
   
class Example(models.Model):
    
    example = models.TextField()
    # address # нужно учесть диапазоны вроде: 12-13 стихи
    translation = models.TextField()
    meanings = models.ManyToManyField(Meaning)


class Gender(models.Model):
    
    name = models.CharField(max_length=15)
    abbreviation = models.CharField(max_length=4)

class Tantum(models.Model):

    name = models.CharField(max_length=20)
    abbreviation = models.CharField(max_length=7)

class Noun(InflectionClass):
    
    gender = models.ForeignKey(Gender)
    tantum = models.ForeignKey(Tantum)
    genitive = models.CharField(max_length=7, help_text=u'введите окончание без начального дефиса')

    
