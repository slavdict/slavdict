# -*- coding: utf-8 -*-


from django.db import models, migrations

def make_inverse(apps, schema_editor):
    Entry = apps.get_model('dictionary', 'Entry')
    for entry in Entry.objects.all():
        entry.civil_inverse = entry.civil_equivalent[::-1]
        entry.save()
    Collocation = apps.get_model('dictionary', 'Collocation')
    for collocation in Collocation.objects.all():
        collocation.civil_inverse = collocation.civil_equivalent[::-1]
        collocation.save()

def remove_inverse(apps, schema_editor):
    Entry = apps.get_model('dictionary', 'Entry')
    for entry in Entry.objects.all():
        entry.civil_inverse = ''
        entry.save()
    Collocation = apps.get_model('dictionary', 'Collocation')
    for collocation in Collocation.objects.all():
        collocation.civil_inverse = ''
        collocation.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_auto_20150616_0706'),
    ]

    operations = [
        migrations.RunPython(make_inverse, remove_inverse),
    ]
