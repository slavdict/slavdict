# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-13 14:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0020_delete_corrupted'),
    ]

    operations = [
        migrations.AddField(
            model_name='greekequivalentforexample',
            name='aliud',
            field=models.BooleanField(default=False, verbose_name='\u0432 \u0433\u0440\u0435\u0447. \u0438\u043d\u0430\u0447\u0435'),
        ),
    ]
