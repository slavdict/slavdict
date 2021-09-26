# Generated by Django 2.2.24 on 2021-09-25 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0080_auto_20210925_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='part_of_speech',
            field=models.CharField(blank=True, choices=[('', ''), ('a', 'сущ.'), ('b', 'прил.'), ('c', 'мест.'), ('d', 'гл.'), ('f', 'нареч.'), ('g', 'союз'), ('h', 'предл.'), ('i', 'част.'), ('j', 'межд.'), ('k', 'числ.'), ('l', '[буква]'), ('m', 'прич.-прил.'), ('n', 'предик. нареч.'), ('e', 'предик. прил.'), ('o', 'транслит.')], default='', max_length=1, verbose_name='часть речи'),
        ),
    ]
