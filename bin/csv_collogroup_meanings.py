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

from slavdict.dictionary.models import CollocationGroup
from slavdict.unicode_csv import UnicodeWriter

uw = UnicodeWriter(open('cg_meanings.csv', 'w'))
for cg in (cg for cg in CollocationGroup.objects.all()
              if cg.host_entry.first_volume):
    cgcolumn = u'; '.join(c.collocation for c in cg.collocations)
    for m in list(cg.meanings) + list(cg.metaph_meanings):
        meaning = m.meaning.strip()
        gloss = m.gloss.strip()
        if meaning or gloss:
            uw.writerow((str(m.id), cgcolumn, u'%s ⏹ %s' % (meaning, gloss)))
            if cgcolumn:
               cgcolumn = u''
