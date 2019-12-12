# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0016_meaning_special_cases'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meaning',
            name='special_case',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u043e\u0441\u043e\u0431\u044b\u0435 \u0441\u043b\u0443\u0447\u0430\u0438', blank=True, choices=[(b'', b''), (b'a', '\u043a\u0430\u043d\u043e\u043d\u0438\u0447.'), (b'b', '\u043f\u0440\u0435\u0434\u043b.'), (b'c', '\u0447\u0430\u0441\u0442.'), (b'd', '\u0432 \u0440\u043e\u043b\u0438 \u043f\u0440\u0438\u0442\u044f\u0436. \u043c\u0435\u0441\u0442.'), (b'e', '\u0442\u0432\u043e\u0440. \u0435\u0434. \u0432 \u0440\u043e\u043b\u0438 \u043d\u0430\u0440\u0435\u0447.'), (b'f', '\u043d\u0430\u0440\u0435\u0447.'), (b'g', '\u043c\u0435\u0436\u0434.'), (b'h', '\u0438\u043c\u044f \u0441\u043e\u0431\u0441\u0442\u0432.'), (b'i', '\u0442\u043e\u043f\u043e\u043d\u0438\u043c'), (b'j', '\u043f\u0440\u0435\u0438\u043c\u0443\u0449.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='substantivus_csl',
            field=models.CharField(default=b'', max_length=60, verbose_name='\u0446\u0441\u043b \u0444\u043e\u0440\u043c\u0430', blank=True),
            preserve_default=True,
        ),
    ]
