#!/usr/bin/env python
# coding: utf-8
import os
import sys

import django
sys.path.append(
    os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry
from slavdict.unicode_csv import UnicodeWriter

NOUN = u'a'
for GENDER in (u'm', u'f', u'n'):
    uw = UnicodeWriter(open('nouns_%s_meanings.csv' % GENDER, 'w'))
    for e in (e for e in Entry.objects.filter(part_of_speech=NOUN,
                            onym=u'', gender=GENDER).order('civil_equivalent')
              if e.first_volume):
        ecolumn = e.civil_equivalent + {1: u'¹', 2: u'²'}.get(e.homonym_order, u'')
        for m in list(e.meanings) + list(e.metaph_meanings):
            meaning = m.meaning.strip()
            gloss = m.gloss.strip()
            if meaning or gloss:
                uw.writerow((str(m.id), ecolumn, u'%s ⏹ %s' % (meaning, gloss)))
                if ecolumn:
                   ecolumn = u''
            for cm in m.child_meanings:
                meaning = cm.meaning.strip()
                gloss = cm.gloss.strip()
                if meaning or gloss:
                    row = (str(cm.id), ecolumn, u'• %s ⏹ %s' % (meaning, gloss))
                    uw.writerow(row)
                    if ecolumn:
                       ecolumn = u''
    uw.stream.close()
