# Generated by Django 2.2.23 on 2021-10-02 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0081_auto_20210925_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='template_version',
            field=models.SmallIntegerField(blank=True, default=2, verbose_name='версия структуры статей'),
        ),
    ]