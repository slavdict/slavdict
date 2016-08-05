#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
Скрипт делает XML-выгрузку словарной базы для InDesign.

При необходимости сделать выборочную выгрузку скрипту допустимо передавать
номера статей в качестве аргументов. Каждый номер можно отделять от другого
пробелами, запятыми или запятыми с пробелами, например:

    SCRIPT 1177,123 89 945, 234
"""
import os
import re
import sys

import django
from coffin.shortcuts import render_to_string

sys.path.append(os.path.abspath('/var/www/slavdict'))
from slavdict import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import sort_key1, sort_key2


entries = []
lexemes = Entry.objects.all()
test_entries = None
if len(sys.argv) > 1:
    r = re.compile(r'\s*,\s*|\s+')
    s = u' '.join(sys.argv[1:]).strip(' ,')
    test_entries = [int(i) for i in r.split(s)]
if test_entries:
    lexemes = lexemes.filter(pk__in=test_entries)
lexemes = [e for e in lexemes
             if e.orth_vars[0].idem.startswith((u'а', u'А', u'б', u'Б'))]

for lexeme in lexemes:

    wordform = lexeme.base_vars[0].idem
    reference = None
    entries.append((wordform, reference, lexeme))
    key = sort_key1(wordform)
    for var in lexeme.base_vars[1:]:
        wordform = var.idem
        key2 = sort_key1(wordform)
        if key2 != key:
            reference = var.idem_ucs
            entries.append((wordform, reference, lexeme))

    # Варианты
    #for var in lexeme.orth_vars_refs[1:]:
    #    wordform = var.idem
    #    key2 = sort_key1(wordform)
    #    if key2 != key:
    #        reference = var.idem_ucs
    #        entries.append((wordform, reference, lexeme))

    # Названия народов
    if lexeme.nom_sg:
        wordform = lexeme.nom_sg
        reference = lexeme.nom_sg_ucs_wax[1]
        entries.append((wordform, reference, lexeme))

    # Краткие формы
    #if lexeme.short_form:
    #    wordform = lexeme.short_form
    #    reference = lexeme.short_form_ucs
    #    entries.append((wordform, reference, lexeme))

    # Причастия
    #for participle in lexeme.participles:
    #    wordform = participle.idem
    #    reference = participle.idem_ucs
    #    entries.append((wordform, reference, lexeme))

def sort_key(x):
    wordform, _, lexeme = x
    return sort_key1(wordform), lexeme.homonym_order or 0, sort_key2(wordform)

entries.sort(key=sort_key)
entries = [(reference, lexeme) for wordform, reference, lexeme in entries]

xml = render_to_string('indesign/slavdict.xml', {'entries': entries})
sys.stdout.write(xml.encode('utf-8'))
sys.exit(0)
