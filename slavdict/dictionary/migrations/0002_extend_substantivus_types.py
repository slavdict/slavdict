# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meaning',
            name='substantivus_type',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u0444\u043e\u0440\u043c\u0430 \u0441\u0443\u0431\u0441\u0442\u0430\u043d\u0442\u0438\u0432\u0430', blank=True, choices=[(b'a', '\u0441\u0440.\u0435\u0434.'), (b'b', '\u0441\u0440.\u043c\u043d.'), (b'c', '\u043c.\u0435\u0434.'), (b'd', '\u043c.\u043c\u043d.'), (b'e', '\u0436.\u0435\u0434.'), (b'f', '\u0436.\u043c\u043d.')]),
            preserve_default=True,
        ),
    ]
