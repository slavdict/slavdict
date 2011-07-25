# -*- coding: utf-8 -*-
from django.db import models

DUMP_TYPE_CHOICES = (
    (u'D', u'dictionary'),
    (u'd', u'directory'),
    (u'u', u'users')
)

class Dump(models.Model):
    dump_time = models.DateTimeField(u'время создания дампа', auto_now=True)
    dump_file = models.FilePathField(u'имя файла')
    dump_type = models.CharField(choices=DUMP_TYPE_CHOICES, max_length=1)