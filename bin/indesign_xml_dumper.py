#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import os
import sys

import django
from coffin.shortcuts import render_to_string

sys.path.append(os.path.abspath('../slavdict'))
from slavdict import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry

entries = [e for e in Entry.objects.all()
             if e.orth_vars[0].idem.startswith((u'а', u'А', u'б', u'Б'))]
entries = [(e, render_to_string('indesign/e.xml', {'entry': e}).strip())
           for e in entries]
entries.sort(key=lambda x: x[0].orth_vars[0].idem)

for e, _ in entries:
    if e.orth_vars_refs[1:] or e.nom_sg or e.participles:

        text = e.orth_vars_refs[0].idem
        print text.encode('utf-8')

        orthvars = [o.idem for o in e.orth_vars_refs[1:]]
        participles = [p.idem for p in e.participles]
        nom_sg = [e.nom_sg] if e.nom_sg else []
        text = u'    %s\n' % u' '.join(orthvars + nom_sg + participles)
        print text.encode('utf-8')

sys.exit(0)
