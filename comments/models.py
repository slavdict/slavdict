# encoding: utf-8
from django.db import models
from tinymce import models as tinymce_models


class Comment(models.Model):

    entry = models.ForeignKey('dictionary.Entry')

    text = tinymce_models.HTMLField( # models.TextField(
        u'текст комментария',
        )

    date = models.DateTimeField(
        u'время добавления комментария',
        auto_now_add = True,
        editable = False,
        )
