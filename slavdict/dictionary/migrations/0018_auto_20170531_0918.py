# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0017_auto_20160910_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='special_case',
            field=models.CharField(default='', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u044c\u044f \u043d\u0443\u0436\u0434\u0430\u0435\u0442\u0441\u044f \u0432 \u0441\u043f\u0435\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0439 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0435', blank=True, choices=[(b'', b''), (b'a', '\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043b\u0435\u043a\u0441\u0435\u043c \u043e\u0434\u043d\u043e\u0433\u043e \u0440\u043e\u0434\u0430'), (b'b', '2 \u043b\u0435\u043a\u0441\u0435\u043c\u044b, \u043c\u0443\u0436. \u0438 \u0436\u0435\u043d. \u0440\u043e\u0434\u0430'), (b'c', '2 \u043b\u0435\u043a\u0441\u0435\u043c\u044b, \u0441\u0440. \u0438 \u0436\u0435\u043d. \u0440\u043e\u0434\u0430'), (b'd', '2 \u043b\u0435\u043a\u0441\u0435\u043c\u044b, \u0436\u0435\u043d. \u0438 \u0442\u043e\u043b\u044c\u043a\u043e \u043c\u043d.'), (b'e', '2 \u043b\u0435\u043a\u0441\u0435\u043c\u044b, \u0442\u043e\u043b\u044c\u043a\u043e \u043c\u043d. \u0438 \u0436\u0435\u043d.'), (b'f', '3 \u043b\u0435\u043a\u0441\u0435\u043c\u044b, 3 \u043c\u0443\u0436. \u0438 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u043d\u0435\u0438\u0437\u043c.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meaning',
            name='special_case',
            field=models.CharField(default=b'', max_length=1, verbose_name='\u043e\u0441\u043e\u0431\u044b\u0435 \u0441\u043b\u0443\u0447\u0430\u0438', blank=True, choices=[(b'', b''), (b'a', '\u043a\u0430\u043d\u043e\u043d\u0438\u0447.'), (b'b', '\u043f\u0440\u0435\u0434\u043b.'), (b'c', '\u0447\u0430\u0441\u0442.'), (b'd', '\u0434\u0430\u0442.'), (b'e', '\u0442\u0432\u043e\u0440. \u0435\u0434. \u0432 \u0440\u043e\u043b\u0438 \u043d\u0430\u0440\u0435\u0447.'), (b'f', '\u043d\u0430\u0440\u0435\u0447.'), (b'g', '\u043c\u0435\u0436\u0434.'), (b'h', '\u0438\u043c\u044f \u0441\u043e\u0431\u0441\u0442\u0432.'), (b'i', '\u0442\u043e\u043f\u043e\u043d\u0438\u043c'), (b'j', '\u043f\u0440\u0435\u0438\u043c\u0443\u0449.'), (b'k', '\u043c\u043d.'), (b'l', '\u0432 \u0440\u043e\u043b\u0438 \u043d\u0430\u0440\u0435\u0447.')]),
            preserve_default=True,
        ),
    ]
