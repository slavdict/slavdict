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

from slavdict.dictionary.models import CollocationGroup

uw = csv.writer(open('cg_meanings.csv', 'w'))
for cg in (cg for cg in CollocationGroup.objects.all()
              if cg.host_entry.is_in_volume(1)):
    cgcolumn = '; '.join(c.collocation for c in cg.collocations)
    for m in list(cg.meanings) + list(cg.metaph_meanings):
        meaning = m.meaning.strip()
        gloss = m.gloss.strip()
        if meaning or gloss:
            uw.writerow((str(m.id), cgcolumn, '%s ⏹ %s' % (meaning, gloss)))
            if cgcolumn:
               cgcolumn = ''
