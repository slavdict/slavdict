# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_auto_20151018_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='example',
            name='audited_time',
            field=models.DateTimeField(verbose_name='\u041a\u043e\u0433\u0434\u0430 \u043f\u0440\u0438\u043c\u0435\u0440 \u0431\u044b\u043b \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d', null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
