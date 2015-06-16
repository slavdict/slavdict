# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_auto_20150601_2300'),
    ]

    operations = [
        migrations.AddField(
            model_name='collocation',
            name='civil_inverse',
            field=models.CharField(default='', max_length=50, verbose_name='\u0433\u0440\u0430\u0436\u0434. \u0438\u043d\u0432.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entry',
            name='civil_inverse',
            field=models.CharField(default='', max_length=50, verbose_name='\u0433\u0440\u0430\u0436\u0434. \u0438\u043d\u0432.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='entry',
            name='civil_equivalent',
            field=models.CharField(max_length=50, verbose_name='\u0433\u0440\u0430\u0436\u0434. \u043d\u0430\u043f\u0438\u0441\u0430\u043d\u0438\u0435'),
            preserve_default=True,
        ),
    ]
