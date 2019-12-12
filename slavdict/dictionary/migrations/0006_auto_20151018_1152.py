# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_auto_20150616_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='example',
            name='ts_example',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='nom_sg',
            field=models.CharField(default=b'', help_text='\u0422\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u044d\u0442\u043d\u043e\u043d\u0438\u043c\u043e\u0432\n                       (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, \u0432 \u0441\u043b\u043e\u0432\u0430\u0440\u043d\u043e\u0439 \u0441\u0442\u0430\u0442\u044c\u0435 \u0410\u0413\u0410\u0420\u042f\u041d\u0418\u041d, \u0437\u0434\u0435\u0441\u044c --\n                       \u0410\u0413\u0410\u0420\u042f\u041d\u0415).', max_length=50, verbose_name='\u0418.\u043c\u043d.', blank=True),
            preserve_default=True,
        ),
    ]
