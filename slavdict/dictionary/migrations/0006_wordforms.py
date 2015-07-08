# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_auto_20150616_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transcription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transcription', models.CharField(default='', max_length=50, verbose_name='\u0442\u0440\u0430\u043d\u0441\u043a\u0440\u0438\u043f\u0446\u0438\u044f', blank=True)),
                ('order', models.SmallIntegerField(default=0, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WordForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idem', models.CharField(max_length=50, verbose_name='\u0441\u043b\u043e\u0432\u043e\u0444\u043e\u0440\u043c\u0430')),
                ('civil_equivalent', models.CharField(max_length=50, verbose_name='\u0433\u0440\u0430\u0436\u0434\u0430\u043d\u0441\u043a\u043e\u0435 \u043d\u0430\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('civil_inverse', models.CharField(max_length=50, verbose_name='\u0433\u0440\u0430\u0436\u0434. \u0438\u043d\u0432.', blank=True)),
                ('order', models.SmallIntegerField(default=20, verbose_name='\u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f', blank=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('reconstructed', models.BooleanField(default=False, verbose_name='\u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442 \u0432 \u043a\u043e\u0440\u043f\u0443\u0441\u0435')),
                ('questionable', models.BooleanField(default=False, verbose_name='\u0440\u0435\u043a\u043e\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u044f \u043d\u0435\u043d\u0430\u0434\u0451\u0436\u043d\u0430')),
                ('number', models.CharField(help_text='\u0434\u043b\u044f \u0441\u0443\u0449., \u043f\u0440\u0438\u043b., \u043f\u0440\u0438\u0447. \u0438 \u0433\u043b.', max_length=1, verbose_name='\u0447\u0438\u0441\u043b\u043e', choices=[(b'1', '\u0435\u0434.\u0447.'), (b'2', '\u0434\u0432.\u0447.'), (b'8', '\u043c\u043d.\u0447.')])),
                ('case', models.CharField(help_text='\u0434\u043b\u044f \u0441\u0443\u0449., \u043f\u0440\u0438\u043b \u0438 \u043f\u0440\u0438\u0447.', max_length=1, verbose_name='\u043f\u0430\u0434\u0435\u0436', choices=[(b'v', '\u0417\u0432\u0430\u0442.'), (b'n', '\u0418\u043c.'), (b'g', '\u0420\u043e\u0434.'), (b'd', '\u0414\u0430\u0442.'), (b'a', '\u0412\u0438\u043d.'), (b'i', '\u0422\u0432\u043e\u0440.'), (b'p', '\u041f\u0440\u0435\u0434\u043b.')])),
                ('gender', models.CharField(help_text='\u0434\u043b\u044f \u043f\u0440\u0438\u043b. \u0438 \u043f\u0440\u0438\u0447.', max_length=1, verbose_name='\u0440\u043e\u0434', choices=[(b'm', '\u043c.'), (b'f', '\u0436.'), (b'n', '\u0441\u0440.')])),
                ('shortness', models.CharField(help_text='\u0434\u043b\u044f \u043f\u0440\u0438\u043b. \u0438 \u043f\u0440\u0438\u0447.', max_length=1, verbose_name='\u043a\u0440\u0430\u0442\u043a\u043e\u0441\u0442\u044c', choices=[(b's', '\u043a\u0440\u0430\u0442\u043a\u0430\u044f \u0444\u043e\u0440\u043c\u0430'), (b'f', '\u043f\u043e\u043b\u043d\u0430\u044f \u0444\u043e\u0440\u043c\u0430')])),
                ('comparison', models.CharField(help_text='\u0434\u043b\u044f \u043f\u0440\u0438\u043b., \u043f\u0440\u0438\u0447. \u0438 \u043d\u0430\u0440.', max_length=1, verbose_name='\u0441\u0442\u0435\u043f\u0435\u043d\u044c \u0441\u0440\u0430\u0432\u043d\u0435\u043d\u0438\u044f', choices=[(b'p', '\u043f\u043e\u043b\u043e\u0436\u0438\u0442.'), (b'c', '\u043a\u043e\u043c\u043f\u0430\u0440.'), (b's', '\u043f\u0440\u0435\u0432\u043e\u0441\u0445.')])),
                ('voice', models.CharField(help_text='\u0434\u043b\u044f \u0433\u043b. \u0438 \u043f\u0440\u0438\u0447.', max_length=1, verbose_name='\u0437\u0430\u043b\u043e\u0433', choices=[(b'a', '\u0430\u043a\u0442\u0438\u0432.'), (b'p', '\u043f\u0430\u0441\u0441\u0438\u0432.')])),
                ('mood', models.CharField(help_text='\u0442\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u0433\u043b.', max_length=1, verbose_name='\u043d\u0430\u043a\u043b\u043e\u043d\u0435\u043d\u0438\u0435', choices=[(b'f', '\u0438\u043d\u0444\u0438\u043d\u0438\u0442\u0438\u0432'), (b'i', '\u0438\u0437\u044a\u044f\u0432\u0438\u0442.'), (b'c', '\u0441\u043e\u0441\u043b\u0430\u0433\u0430\u0442.'), (b'm', '\u043f\u043e\u0432\u0435\u043b\u0438\u0442.')])),
                ('person', models.CharField(help_text='\u0434\u043b\u044f \u0433\u043b., \u043c\u0435\u0441\u0442. \u0441\u0443\u0449. \u0438 \u043c\u0435\u0441\u0442. \u043f\u0440\u0438\u043b.', max_length=1, verbose_name='\u043b\u0438\u0446\u043e', choices=[(b'1', '1-\u0435 \u043b\u0438\u0446\u043e'), (b'2', '2-\u0435 \u043b\u0438\u0446\u043e'), (b'3', '3-\u0435 \u043b\u0438\u0446\u043e')])),
                ('entry', models.ForeignKey(blank=True, to='dictionary.Entry', null=True)),
            ],
            options={
                'ordering': ('order', 'id'),
                'verbose_name': '\u0441\u043b\u043e\u0432\u043e\u0444\u043e\u0440\u043c\u0430',
                'verbose_name_plural': '\u0441\u043b\u043e\u0432\u043e\u0444\u043e\u0440\u043c\u044b',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='transcription',
            name='wordform',
            field=models.ForeignKey(to='dictionary.WordForm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='entry',
            name='nom_sg',
            field=models.CharField(default=b'', help_text='\u0422\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u044d\u0442\u043d\u043e\u043d\u0438\u043c\u043e\u0432\n                       (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, \u0432 \u0441\u043b\u043e\u0432\u0430\u0440\u043d\u043e\u0439 \u0441\u0442\u0430\u0442\u044c\u0435 \u0410\u0413\u0410\u0420\u042f\u041d\u0418\u041d, \u0437\u0434\u0435\u0441\u044c --\n                       \u0410\u0413\u0410\u0420\u042f\u041d\u0415).', max_length=50, verbose_name='\u0418.\u043c\u043d.', blank=True),
            preserve_default=True,
        ),
    ]
