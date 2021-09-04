#!/usr/bin/env python
import csv
import os
import sys

import django
sys.path.append(
    os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry, ONYM_MAP

def write_csv(filename, entries):
    uw = csv.writer(open(filename, 'w'))
    for e in (e for e in entries if e.is_in_volume(1)):
        ecolumn = e.civil_equivalent + {1: '¹', 2: '²'}.get(e.homonym_order, '')
        for m in list(e.meanings) + list(e.metaph_meanings):
            meaning = m.meaning.strip()
            gloss = m.gloss.strip()
            if meaning or gloss:
                uw.writerow((str(m.id), ecolumn, '%s ⏹ %s' % (meaning, gloss)))
                if ecolumn:
                   ecolumn = ''
            for cm in m.child_meanings:
                meaning = cm.meaning.strip()
                gloss = cm.gloss.strip()
                if meaning or gloss:
                    row = (str(cm.id), ecolumn, '• %s ⏹ %s' % (meaning, gloss))
                    uw.writerow(row)
                    if ecolumn:
                       ecolumn = ''
    uw.stream.close()

NOUN = 'a'
for GENDER in ('m', 'f', 'n', ''):
    filename = 'nouns_%s_meanings.csv' % GENDER
    common_nouns = Entry.objects.filter(
            part_of_speech=NOUN, onym='',
            gender=GENDER).order_by('civil_equivalent')
    write_csv(filename, common_nouns)

for ONYM in ('anthroponym', 'toponym', 'ethnonym', 'other'):
    onyms = Entry.objects \
                .filter(part_of_speech=NOUN, onym=ONYM_MAP[ONYM]) \
                .order_by('civil_equivalent')
    filename = 'nouns_meanings_%s.csv' % ONYM
    write_csv(filename, onyms)
