# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0008_orthvar_parent_and_use'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='untitled_exists',
            field=models.BooleanField(default=False, verbose_name='\u0412\u0430\u0440\u0438\u0430\u043d\u0442 \u0431\u0435\u0437 \u0442\u0438\u0442\u043b\u0430 \u043f\u0440\u0435\u0434\u0441\u0442\u0430\u0432\u043b\u0435\u043d\n            \u0432 \u0442\u0435\u043a\u0441\u0442\u0430\u0445'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='gender',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u0440\u043e\u0434', blank=True, choices=[(b'm', '\u043c.'), (b'f', '\u0436.'), (b'n', '\u0441.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='substantivus_type',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u0444\u043e\u0440\u043c\u0430 \u0441\u0443\u0431\u0441\u0442\u0430\u043d\u0442\u0438\u0432\u0430', blank=True, choices=[(b'a', '\u0441.\xa0\u0435\u0434.'), (b'b', '\u0441.\xa0\u043c\u043d.'), (b'c', '\u043c.\xa0\u0435\u0434.'), (b'd', '\u043c.\xa0\u043c\u043d.'), (b'e', '\u0436.\xa0\u0435\u0434.'), (b'f', '\u0436.\xa0\u043c\u043d.')]),
            preserve_default=True,
        ),
    ]
