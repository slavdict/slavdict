# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0011_auto_20160719_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='meaning',
            name='is_valency',
            field=models.BooleanField(default=False, verbose_name='\u041c\u043e\u0434\u0435\u043b\u044c \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='onym',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u0442\u0438\u043f \u0438\u043c\u0435\u043d\u0438 \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u043e\u0433\u043e', blank=True, choices=[(b'', '\u043d\u0435 \u0438\u043c\u044f \u0441\u043e\u0431\u0441\u0442.'), (b'a', '\u0438\u043c\u044f'), (b'b', '\u0442\u043e\u043f\u043e\u043d\u0438\u043c'), (b'c', '\u043d\u0430\u0440\u043e\u0434/\u043e\u0431\u0449\u043d\u043e\u0441\u0442\u044c \u043b\u044e\u0434\u0435\u0439'), (b'd', '[\u0434\u0440\u0443\u0433\u043e\u0435]')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='metaphorical',
            field=models.BooleanField(default=False, verbose_name='\u0433\u0438\u043c\u043d\u043e\u0433\u0440.\u043c\u0435\u0442\u0430\u0444\u043e\u0440\u0430'),
            preserve_default=True,
        ),
    ]
