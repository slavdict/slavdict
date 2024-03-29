# Generated by Django 2.2.17 on 2021-02-08 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0068_entry_temp_editors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='source',
            field=models.CharField(choices=[('', ''), ('S', 'Синодальный перевод'), ('R', 'Перевод РБО'), ('U', 'Перевод ПСТГУ'), ('A', 'Адаменко В., свящ.'), ('Z', '(Безобразов) Кассиан, еп.'), ('B', 'Бируковы'), ('G', '(Говоров) Феофан, еп. — перевод Добротолюбия'), ('K', 'Кедров Н. — перевод великого канона'), ('L', 'Ловягин Е.И. — перевод канонов'), ('2', 'Ловягин И.Ф. — перевод октоиха'), ('N', 'Нахимов Н. (Зайончковский Н.Ч.)'), ('P', '(Полянский) Иустин, еп. — перевод Алфавита духовного'), ('3', 'Седакова О.А.'), ('T', '(Тимрот) Амвросий, иером.'), ('J', 'Юнгеров П.А.')], default='', max_length=1, verbose_name='Источник'),
        ),
    ]
