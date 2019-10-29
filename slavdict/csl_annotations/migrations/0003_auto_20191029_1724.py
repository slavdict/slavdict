# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-29 17:24
from __future__ import unicode_literals

from django.db import migrations, models
import slavdict.csl_annotations.models


class Migration(migrations.Migration):

    dependencies = [
        ('csl_annotations', '0002_auto_20191020_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='anchor',
            field=models.SlugField(blank=True, help_text='\n\n    \u042f\u043a\u043e\u0440\u044c, \u0447\u0442\u043e\u0431\u044b \u0441\u043e\u0441\u043b\u0430\u0442\u044c\u0441\u044f \u043d\u0430 \u0442\u0435\u043a\u0443\u0449\u0443\u044e \u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044e \u0438\u0437 \u0434\u0440\u0443\u0433\u043e\u0439 \u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u0438.<br>\n    \u0415\u0441\u043b\u0438 \u0441\u0441\u044b\u043b\u043a\u0430\u0442\u044c\u0441\u044f \u043d\u0430 \u0434\u0430\u043d\u043d\u0443\u044e \u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044e \u0438\u0437 \u0434\u0440\u0443\u0433\u043e\u0439 \u043d\u0435\u0442 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0441\u0442\u0438,<br>\n    \u0442\u043e \u043f\u043e\u043b\u0435 \u043c\u043e\u0436\u043d\u043e \u043e\u0441\u0442\u0430\u0432\u043b\u044f\u0442\u044c \u043f\u0443\u0441\u0442\u044b\u043c.<br>\n    <br>\n    \u0415\u0441\u043b\u0438 \u044f\u043a\u043e\u0440\u044c \u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u0438 \u043d\u0430 \xab\u0440\u0435\u0441\u0443\u0440\u0441 N\xbb \u0437\u0430\u0434\u0430\u043d \u0442\u0430\u043a <span\n    style="color: #070">ludogovsk8</span>, \u0442\u043e \u0441\u043e\u0441\u043b\u0430\u0442\u044c\u0441\u044f<br>\n    \u0438\u0437 \u0442\u0435\u043a\u0441\u0442\u0430 \u0434\u0440\u0443\u0433\u043e\u0439 \u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u0438 \u043d\u0430 \u043d\u0435\u0433\u043e \u043c\u043e\u0436\u043d\u043e \u0442\u0430\u043a:\n    <span style="color: #070">\u0441\u043c. [\u0440\u0435\u0441\u0443\u0440\u0441 N](#ludogovsk8)</span>.<br>\n\n', max_length=30, null=True, unique=True, verbose_name='\u044f\u043a\u043e\u0440\u044c'),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='annotation',
            field=models.TextField(blank=True, help_text='\n\n    \u041e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u043e \u0434\u043b\u044f \u043a\u043d\u0438\u0433 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439, \u0444\u0430\u043a\u0443\u043b\u044c\u0442\u0430\u0442\u0438\u0432\u043d\u043e \u0434\u043b\u044f \u0432\u0438\u0434\u0435\u043e.\n\n\n\n    <p style="font-size: xx-small; margin-bottom: 1em">\n    \u0414\u043b\u044f \u043a\u0443\u0440\u0441\u0438\u0432\u0430, \u0441\u0441\u044b\u043b\u043e\u043a \u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435\n    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">\u0440\u0430\u0437\u043c\u0435\u0442\u043a\u0443 Markdown</a>.</p>\n\n', null=True, unique=True, verbose_name='\u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='bib',
            field=slavdict.csl_annotations.models.FixedWidthTextField(blank=True, help_text='\u0414\u043b\u044f \u043a\u043d\u0438\u0433 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439.\n\n    <p style="font-size: xx-small; margin-bottom: 1em">\n    \u0414\u043b\u044f \u043a\u0443\u0440\u0441\u0438\u0432\u0430, \u0441\u0441\u044b\u043b\u043e\u043a \u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435\n    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">\u0440\u0430\u0437\u043c\u0435\u0442\u043a\u0443 Markdown</a>.</p>\n\n', max_length=2000, null=True, verbose_name='\u0431\u0438\u0431\u043b\u0438\u043e\u0433\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430'),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='teaser',
            field=models.TextField(blank=True, help_text='\u0414\u043b\u044f \u0432\u0438\u0434\u0435\u043e.\n\n    <p style="font-size: xx-small; margin-bottom: 1em">\n    \u0414\u043b\u044f \u043a\u0443\u0440\u0441\u0438\u0432\u0430, \u0441\u0441\u044b\u043b\u043e\u043a \u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435\n    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">\u0440\u0430\u0437\u043c\u0435\u0442\u043a\u0443 Markdown</a>.</p>\n\n', null=True, unique=True, verbose_name='\u0442\u0438\u0437\u0435\u0440'),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='title',
            field=slavdict.csl_annotations.models.FixedWidthTextField(blank=True, help_text='\n\n    \u041e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u043e \u0434\u043b\u044f \u0432\u0438\u0434\u0435\u043e, \u0444\u0430\u043a\u0443\u043b\u044c\u0442\u0430\u0442\u0438\u0432\u043d\u043e \u0434\u043b\u044f \u043a\u043d\u0438\u0433 \u0438 \u0441\u0442\u0430\u0442\u0435\u0439.<br>\n    \u0420\u0443\u0447\u043d\u043e\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0438\u0435 \u0430\u0432\u0442\u043e\u0440\u0441\u0442\u0432\u0430 \u0432 \u044d\u0442\u043e\u043c \u043f\u043e\u043b\u0435 \u043d\u0435 \u043f\u0440\u0438\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442\u0441\u044f, \u0442\u0430\u043a \u043a\u0430\u043a<br>\n    \u0430\u0432\u0442\u043e\u0440 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0431\u0443\u0434\u0435\u0442 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d (\u0435\u0441\u043b\u0438 \u043e\u043d \u0432\u044b\u0434\u0435\u043b\u0435\u043d \u0433\u0430\u043b\u043e\u0447\u043a\u043e\u0439 \u0432 \u043f\u043e\u043b\u0435<br>\n    \xab\u0410\u0432\u0442\u043e\u0440\xbb) \u043f\u0440\u0438 \u0432\u044b\u0432\u043e\u0434\u0435 \u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043a\u0430 \u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u0438 \u043d\u0430 \u043f\u043e\u0440\u0442\u0430\u043b\u0435.\n\n\n\n    <p style="font-size: xx-small; margin-bottom: 1em">\n    \u0414\u043b\u044f \u043a\u0443\u0440\u0441\u0438\u0432\u0430, \u0441\u0441\u044b\u043b\u043e\u043a \u0438 \u0430\u0431\u0437\u0430\u0446\u0435\u0432 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435\n    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">\u0440\u0430\u0437\u043c\u0435\u0442\u043a\u0443 Markdown</a>.</p>\n\n', max_length=200, null=True, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'),
        ),
    ]
