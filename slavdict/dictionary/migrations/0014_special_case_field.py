# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0013_transitivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='special_case',
            field=models.CharField(default='', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u044c\u044f \u043d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0441\u043f\u0435\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0439 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0435', blank=True, choices=[(b'', b''), (b'a', '\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043b\u0435\u043a\u0441\u0435\u043c \u043e\u0434\u043d\u043e\u0433\u043e \u0440\u043e\u0434\u0430')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='transitivity',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u044c', blank=True, choices=[(b'', ''), (b't', '\u043f\u0435\u0440\u0435\u0445.'), (b'i', '\u043d\u0435\u043f\u0435\u0440\u0435\u0445.'), (b'b', '\u043f\u0435\u0440\u0435\u0445. \u0438\xa0\u043d\u0435\u043f\u0435\u0440\u0435\u0445.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='substantivus',
            field=models.BooleanField(default=False, verbose_name='\u0432 \u0440\u043e\u043b\u0438 \u0441\u0443\u0449.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='transitivity',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u044c', blank=True, choices=[(b'', ''), (b't', '\u043f\u0435\u0440\u0435\u0445.'), (b'i', '\u043d\u0435\u043f\u0435\u0440\u0435\u0445.'), (b'b', '\u043f\u0435\u0440\u0435\u0445. \u0438\xa0\u043d\u0435\u043f\u0435\u0440\u0435\u0445.')]),
            preserve_default=True,
        ),
    ]
