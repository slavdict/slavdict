# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_extend_substantivus_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='genitive',
            field=models.CharField(max_length=50, verbose_name='\u0444\u043e\u0440\u043c\u0430 \u0420. \u043f\u0430\u0434\u0435\u0436\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='nom_sg',
            field=models.CharField(default=b'', help_text='\u0422\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u044d\u0442\u043d\u043e\u043d\u0438\u043c\u043e\u0432\n                       (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, \u0432 \u0441\u043b\u043e\u0432\u0430\u0440\u043d\u043e\u0439 \u0441\u0442\u0430\u0442\u044c\u0435 \u0410\u0413\u0410\u0420\u042f\u041d\u0415, \u0437\u0434\u0435\u0441\u044c --\n                       \u0410\u0413\u0410\u0420\u042f\u041d\u0418\u041d).', max_length=50, verbose_name='\u0418.\u0435\u0434.\u043c.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='sg1',
            field=models.CharField(help_text='\u0426\u0435\u043b\u0430\u044f \u0441\u043b\u043e\u0432\u043e\u0444\u043e\u0440\u043c\u0430 \u0438\u043b\u0438 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435. \u0412 \u0441\u043b\u0443\u0447\u0430\u0435\n                    \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u0435\u0440\u0432\u044b\u043c \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u043c \u0434\u043e\u043b\u0436\u0435\u043d \u0438\u0434\u0442\u0438 \u0434\u0435\u0444\u0438\u0441.', max_length=50, verbose_name='\u0444\u043e\u0440\u043c\u0430 1 \u0435\u0434.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='sg2',
            field=models.CharField(help_text='\u0426\u0435\u043b\u0430\u044f \u0441\u043b\u043e\u0432\u043e\u0444\u043e\u0440\u043c\u0430 \u0438\u043b\u0438 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435. \u0412 \u0441\u043b\u0443\u0447\u0430\u0435\n                    \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043f\u0435\u0440\u0432\u044b\u043c \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u043c \u0434\u043e\u043b\u0436\u0435\u043d \u0438\u0434\u0442\u0438 \u0434\u0435\u0444\u0438\u0441.', max_length=50, verbose_name='\u0444\u043e\u0440\u043c\u0430 2 \u0435\u0434.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='short_form',
            field=models.CharField(help_text='\u0415\u0441\u043b\u0438 \u0412\u044b \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442\u0435\n                           \u043d\u0435 \u0432\u0441\u0451 \u0441\u043b\u043e\u0432\u043e, \u0430 \u0442\u043e\u043b\u044c\u043a\u043e \u0435\u0433\u043e \u0447\u0430\u0441\u0442\u044c, \u043f\u0440\u0435\u0434\u0432\u0430\u0440\u044f\u0439\u0442\u0435 \u0435\u0451\n                           \u0434\u0435\u0444\u0438\u0441\u043e\u043c.', max_length=50, verbose_name='\u043a\u0440\u0430\u0442\u043a\u0430\u044f \u0444\u043e\u0440\u043c\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='status',
            field=models.CharField(default=b'c', max_length=1, verbose_name='\u0441\u0442\u0430\u0442\u0443\u0441 \u0441\u0442\u0430\u0442\u044c\u0438', choices=[(b'c', '\u0441\u043e\u0437\u0434\u0430\u043d\u0430'), (b'w', '\u0432 \u0440\u0430\u0431\u043e\u0442\u0435'), (b'g', '\u043f\u043e\u0438\u0441\u043a \u0433\u0440\u0435\u0447.'), (b'f', '\u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430'), (b'e', '\u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u0443\u0435\u0442\u0441\u044f'), (b'a', '\u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430')]),
            preserve_default=True,
        ),
    ]
