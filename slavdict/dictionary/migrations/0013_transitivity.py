# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0012_is_valency'),
    ]

    operations = [
        migrations.AddField(
            model_name='meaning',
            name='transitivity',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u044c', blank=True, choices=[(b'', ''), (b't', '\u043f\u0435\u0440\u0435\u0445.'), (b'i', '\u043d\u0435\u043f\u0435\u0440\u0435\u0445.'), (b'b', '\u043f\u0435\u0440\u0435\u0445./\u043d\u0435\u043f\u0435\u0440\u0435\u0445.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='transitivity',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u044c', blank=True, choices=[(b'', ''), (b't', '\u043f\u0435\u0440\u0435\u0445.'), (b'i', '\u043d\u0435\u043f\u0435\u0440\u0435\u0445.'), (b'b', '\u043f\u0435\u0440\u0435\u0445./\u043d\u0435\u043f\u0435\u0440\u0435\u0445.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='is_valency',
            field=models.BooleanField(default=False, verbose_name='\u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435'),
            preserve_default=True,
        ),
    ]
