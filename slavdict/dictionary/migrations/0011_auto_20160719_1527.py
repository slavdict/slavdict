# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-19 15:27


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0010_phraseological_widecolloc'),
    ]

    operations = [
        migrations.AddField(
            model_name='collocationgroup',
            name='hidden',
            field=models.BooleanField(default=False, editable=False, help_text='\u041d\u0435 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c\n            \u0441\u043b\u043e\u0432\u043e\u0441\u043e\u0447\u0435\u0442\u0430\u043d\u0438\u0435 \u0432 \u0441\u0442\u0430\u0442\u044c\u0435.', verbose_name='\u0421\u043a\u0440\u044b\u0442\u044c \u0441\u043b\u043e\u0432\u043e\u0441\u043e\u0447\u0435\u0442\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='collocation',
            name='order',
            field=models.SmallIntegerField(blank=True, default=10, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
    ]
