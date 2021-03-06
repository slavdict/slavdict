# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-12 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0049_auto_20190509_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collocationgroup',
            name='cf_entries',
            field=models.ManyToManyField(blank=True, related_name='cf_collogroup_set', to='dictionary.Entry', verbose_name='ср. (лексемы)'),
        ),
        migrations.AlterField(
            model_name='collocationgroup',
            name='cf_meanings',
            field=models.ManyToManyField(blank=True, related_name='cf_collogroup_set', to='dictionary.Meaning', verbose_name='ср. (значения)'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='authors',
            field=models.ManyToManyField(blank=True, to='custom_user.CustomUser', verbose_name='автор статьи'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='cf_collogroups',
            field=models.ManyToManyField(blank=True, related_name='cf_entry_set', to='dictionary.CollocationGroup', verbose_name='ср. (группы слововосочетаний)'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='cf_entries',
            field=models.ManyToManyField(blank=True, related_name='cf_entry_set', to='dictionary.Entry', verbose_name='ср. (лексемы)'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='cf_meanings',
            field=models.ManyToManyField(blank=True, related_name='cf_entry_set', to='dictionary.Meaning', verbose_name='ср. (значения)'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='gender',
            field=models.CharField(blank=True, choices=[('m', 'м.'), ('f', 'ж.'), ('n', 'с.'), ('d', 'м. и\xa0ж.')], default='', max_length=1, verbose_name='род'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='nom_sg',
            field=models.CharField(blank=True, default='', help_text='Только для этнонимов\n                       (например, в словарной статье АГАРЯНИН, здесь --\n                       АГАРЯНЕ).', max_length=50, verbose_name='И.мн.'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='onym',
            field=models.CharField(blank=True, choices=[('', 'не имя собст.'), ('a', 'имя'), ('b', 'топоним'), ('c', 'народ/общность людей'), ('d', '[другое]')], default='', max_length=1, verbose_name='тип имени собственного'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='part_of_speech',
            field=models.CharField(blank=True, choices=[('', ''), ('a', 'сущ.'), ('b', 'прил.'), ('c', 'мест.'), ('d', 'гл.'), ('f', 'нареч.'), ('g', 'союз'), ('h', 'предл.'), ('i', 'част.'), ('j', 'межд.'), ('k', '[число]'), ('l', '[буква]'), ('m', 'прич.-прил.'), ('n', 'предик. нареч.')], default='', max_length=1, verbose_name='часть речи'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='participle_type',
            field=models.CharField(blank=True, choices=[('a', 'действ. прич. наст. вр.'), ('b', 'действ. прич. прош. вр.'), ('c', 'страд. прич. наст. вр.'), ('d', 'страд. прич. прош. вр.')], default='', max_length=1, verbose_name='тип причастия'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='special_case',
            field=models.CharField(blank=True, choices=[('', ''), ('a', 'Несколько лексем одного рода'), ('b', '2 лексемы, муж. и жен. рода'), ('j', '2 лексемы, муж. и ср. рода'), ('c', '2 лексемы, ср. и жен. рода'), ('g', '2 лексемы, жен. и ср. рода'), ('d', '2 лексемы, жен. и только мн.'), ('e', '2 лексемы, только мн. и жен.'), ('f', '3 лексемы, 3 муж. и последний неизм.'), ('h', '4 лексемы [вихрь]'), ('i', 'Вынудить отображение пометы «неперех. и перех.» при равном кол-ве перех. и неперех. значений')], default='', max_length=1, verbose_name='Статья нуждается в специальной обработке'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='status',
            field=models.CharField(choices=[('c', 'создана'), ('w', 'в работе'), ('g', 'поиск греч.'), ('f', 'завершена'), ('e', 'редактируется'), ('a', 'утверждена')], default='c', max_length=1, verbose_name='статус статьи'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='tantum',
            field=models.CharField(blank=True, choices=[('d', 'только дв.'), ('p', 'только мн.')], default='', max_length=1, verbose_name='число'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='transitivity',
            field=models.CharField(blank=True, choices=[('', ''), ('t', 'перех.'), ('i', 'неперех.'), ('b', 'перех. и\xa0неперех.')], default='', max_length=1, verbose_name='переходность'),
        ),
        migrations.AlterField(
            model_name='etymology',
            name='language',
            field=models.CharField(choices=[('a', 'греч.'), ('b', 'ивр.'), ('c', 'аккад.'), ('d', 'арам.'), ('e', 'арм.'), ('f', 'груз.'), ('g', 'копт.'), ('h', 'лат.'), ('i', 'сир.')], default='', max_length=1, verbose_name='язык'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='cf_collogroups',
            field=models.ManyToManyField(blank=True, related_name='cf_meaning_set', to='dictionary.CollocationGroup', verbose_name='ср. (группы слововосочетаний)'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='cf_entries',
            field=models.ManyToManyField(blank=True, related_name='cf_meaning_set', to='dictionary.Entry', verbose_name='ср. (лексемы)'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='cf_meanings',
            field=models.ManyToManyField(blank=True, related_name='cf_meaning_set', to='dictionary.Meaning', verbose_name='ср. (значения)'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='special_case',
            field=models.CharField(blank=True, choices=[('', ''), ('Имена', (('a', 'канонич.'), ('h', 'имя собств.'), ('i', 'топоним'))), ('Части речи', (('f', 'нареч.'), ('s', 'предик. нареч.'), ('m', 'союз'), ('b', 'предл.'), ('c', 'част.'), ('g', 'межд.'))), ('Формы слова', (('d', 'дат.'), ('k', 'мн.'), ('e', 'твор. ед. в роли нареч.'), ('l', 'в роли нареч.'), ('n', 'в роли прил.'), ('o', 'в роли част.'))), ('Другое', (('q', 'безл.'), ('r', 'вводн.'), ('p', 'полувспом.'), ('j', 'преимущ.')))], default='', max_length=1, verbose_name='особые случаи'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='substantivus_csl',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='цсл форма'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='substantivus_type',
            field=models.CharField(blank=True, choices=[('', ''), ('a', 'с.\xa0ед.'), ('b', 'с.\xa0мн.'), ('c', 'м.\xa0ед.'), ('d', 'м.\xa0мн.'), ('e', 'ж.\xa0ед.'), ('f', 'ж.\xa0мн.')], default='', max_length=1, verbose_name='форма субстантива'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='transitivity',
            field=models.CharField(blank=True, choices=[('', ''), ('t', 'перех.'), ('i', 'неперех.'), ('b', 'перех. и\xa0неперех.')], default='', max_length=1, verbose_name='переходность'),
        ),
        migrations.AlterField(
            model_name='participle',
            name='tp',
            field=models.CharField(choices=[('1', 'действ. наст.'), ('2', 'действ. прош.'), ('3', 'страд. наст.'), ('4', 'страд. прош.')], max_length=2, verbose_name='тип причастия'),
        ),
    ]
