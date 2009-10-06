# -*- coding: UTF-8 -*-

from django.db import models

class PartOfSpeach(models.Model):
    
    name = models.CharField(max_length=20)
    abbreviation = models.CharField(max_length=8)

class InflectionClass(models.Model):
    
    pass

class DictEntry(models.Model):
    
    civil_equivalent = models.CharField(max_length=40)
    # headwords
    # part_of_speech

class Headword(models.Model):
    
    dict_entry = models.ForeignKey(DictEntry)
    headword = models.CharField(max_length=40)
    frequency = models.PositiveInteger()

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

    
