# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_untitled_exists'),
    ]

    operations = [
        migrations.AddField(
            model_name='collocationgroup',
            name='phraseological',
            field=models.BooleanField(default=False, verbose_name='\u0444\u0440\u0430\u0437\u0435\u043e\u043b\u043e\u0433\u0438\u0437\u043c'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='collocation',
            name='civil_equivalent',
            field=models.CharField(max_length=350, verbose_name='\u0433\u0440\u0430\u0436\u0434\u0430\u043d\u0441\u043a\u043e\u0435 \u043d\u0430\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='collocation',
            name='civil_inverse',
            field=models.CharField(max_length=350, verbose_name='\u0433\u0440\u0430\u0436\u0434. \u0438\u043d\u0432.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='collocation',
            name='collocation',
            field=models.CharField(max_length=200, verbose_name='\u0441\u043b\u043e\u0432\u043e\u0441\u043e\u0447\u0435\u0442\u0430\u043d\u0438\u0435'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='part_of_speech',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u0447\u0430\u0441\u0442\u044c \u0440\u0435\u0447\u0438', blank=True, choices=[(b'', b''), (b'a', '\u0441\u0443\u0449.'), (b'b', '\u043f\u0440\u0438\u043b.'), (b'c', '\u043c\u0435\u0441\u0442.'), (b'd', '\u0433\u043b.'), (b'e', '[\u043f\u0440\u0438\u0447.]'), (b'f', '\u043d\u0430\u0440\u0435\u0447.'), (b'g', '\u0441\u043e\u044e\u0437'), (b'h', '\u043f\u0440\u0435\u0434\u043b.'), (b'i', '\u0447\u0430\u0441\u0442.'), (b'j', '\u043c\u0435\u0436\u0434.'), (b'k', '[\u0447\u0438\u0441\u043b\u043e]'), (b'l', '[\u0431\u0443\u043a\u0432\u0430]'), (b'm', '\u043f\u0440\u0438\u0447.-\u043f\u0440\u0438\u043b.')]),
            preserve_default=True,
        ),
    ]
