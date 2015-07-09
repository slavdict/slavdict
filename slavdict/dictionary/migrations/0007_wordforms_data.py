# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def sg12(apps, schema_editor):
    Entry = apps.get_model('dictionary', 'Entry')
    WordForm = apps.get_model('dictionary', 'WordForm')
    VERB = 'd'
    for e in Entry.objects.filter(part_of_speech=VERB):
        args = {
            'number': '1',
            'voice': 'a',
            'mood': 'i',
            'tense': 'p',
            'person': '1',
        }
        sg1 = WordForm(**args)

class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_wordforms'),
    ]

    operations = [
        migrations.RunPython(sg12),
    ]
