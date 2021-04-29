# Generated by Django 2.2.20 on 2021-04-29 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0070_auto_20210213_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='part_of_speech',
            field=models.CharField(blank=True, choices=[('', ''), ('a', 'сущ.'), ('b', 'прил.'), ('c', 'мест.'), ('d', 'гл.'), ('f', 'нареч.'), ('g', 'союз'), ('h', 'предл.'), ('i', 'част.'), ('j', 'межд.'), ('k', 'числ.'), ('l', '[буква]'), ('m', 'прич.-прил.'), ('n', 'предик. нареч.')], default='', max_length=1, verbose_name='часть речи'),
        ),
    ]
