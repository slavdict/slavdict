# -*- coding: utf-8 -*-
from django.db import models

class Dump(models.Model):
    dump_time = models.DateTimeField(u'время создания дампа', auto_now=True)
    dump_file = models.FileField(u'имя файла')