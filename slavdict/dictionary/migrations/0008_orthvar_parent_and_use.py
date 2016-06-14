# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0007_example_audited_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='orthographicvariant',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='dictionary.OrthographicVariant', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orthographicvariant',
            name='use',
            field=models.CharField(default='', help_text='\n                    \u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0442\u043e\u043c, \u0441 \u043a\u0430\u043a\u0438\u043c\u0438 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f\u043c\u0438 \u0434\u0430\u043d\u043d\u044b\u0439 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\n                    \u0441\u0432\u044f\u0437\u0430\u043d. \u0420\u0430\u0437\u043d\u044b\u0435 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u044b \u043d\u0430\u043f\u0438\u0441\u0430\u043d\u0438\u044f \u043c\u043e\u0433\u0443\u0442 \u043a\u043e\u0440\u0440\u0435\u043b\u0438\u0440\u043e\u0432\u0430\u0442\u044c\n                    \u0441 \u0440\u0430\u0437\u043d\u044b\u043c\u0438 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f\u043c\u0438, \u043a\u0430\u043a \u0432 \u0441\u043b\u0443\u0447\u0430\u0435 \u0441\u043b\u043e\u0432 \u0431\u043e\u0433\u044a/\u0431\u0433~\u044a,\n                    \u0430\u0433\u0433~\u043b\u044a/\u0430\u0433\u0433\u0435\u043b\u044a.', max_length=50, verbose_name='\u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u0435'),
            preserve_default=True,
        ),
    ]
