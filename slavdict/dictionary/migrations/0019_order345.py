# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-07 13:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0018_auto_20170531_0918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collocation',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='collocationgroup',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='etymology',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='greekequivalentforexample',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='meaningcontext',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='orthographicvariant',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='participle',
            name='order',
            field=models.SmallIntegerField(blank=True, default=345, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
    ]