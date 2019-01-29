# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-29 23:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0042_auto_20190109_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meaning',
            name='special_case',
            field=models.CharField(blank=True, choices=[(b'', b''), ('\u0418\u043c\u0435\u043d\u0430', ((b'a', '\u043a\u0430\u043d\u043e\u043d\u0438\u0447.'), (b'h', '\u0438\u043c\u044f \u0441\u043e\u0431\u0441\u0442\u0432.'), (b'i', '\u0442\u043e\u043f\u043e\u043d\u0438\u043c'))), ('\u0427\u0430\u0441\u0442\u0438 \u0440\u0435\u0447\u0438', ((b'f', '\u043d\u0430\u0440\u0435\u0447.'), (b'm', '\u0441\u043e\u044e\u0437'), (b'b', '\u043f\u0440\u0435\u0434\u043b.'), (b'c', '\u0447\u0430\u0441\u0442.'), (b'g', '\u043c\u0435\u0436\u0434.'))), ('\u0424\u043e\u0440\u043c\u044b \u0441\u043b\u043e\u0432\u0430', ((b'd', '\u0434\u0430\u0442.'), (b'k', '\u043c\u043d.'), (b'e', '\u0442\u0432\u043e\u0440. \u0435\u0434. \u0432 \u0440\u043e\u043b\u0438 \u043d\u0430\u0440\u0435\u0447.'), (b'l', '\u0432 \u0440\u043e\u043b\u0438 \u043d\u0430\u0440\u0435\u0447.'), (b'n', '\u0432 \u0440\u043e\u043b\u0438 \u043f\u0440\u0438\u043b.'), (b'o', '\u0432 \u0440\u043e\u043b\u0438 \u0447\u0430\u0441\u0442.'))), ('\u0414\u0440\u0443\u0433\u043e\u0435', ((b'j', '\u043f\u0440\u0435\u0438\u043c\u0443\u0449.'), (b'p', '\u043f\u043e\u043b\u0443\u0432\u0441\u043f\u043e\u043c.'), (b'q', '\u0431\u0435\u0437\u043b.')))], default=b'', max_length=1, verbose_name='\u043e\u0441\u043e\u0431\u044b\u0435 \u0441\u043b\u0443\u0447\u0430\u0438'),
        ),
    ]
