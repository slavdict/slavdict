#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
Скрипт делает выгрузку словарной базы для портала "Цсл язык сегодня"

При необходимости сделать выборочную выгрузку скрипту допустимо передавать
номера статей в качестве аргументов. Каждый номер можно отделять от другого
пробелами, запятыми или запятыми с пробелами, например:

    SCRIPT 1177,123 89 945, 234
"""
import itertools
import os
import re
import sys

import django
from django.template.loader import render_to_string

sys.path.append(os.path.abspath('/var/www/slavdict'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import convert_for_index
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import resolve_titles
from slavdict.dictionary.models import sort_key1
from slavdict.dictionary.models import sort_key2
from slavdict.dictionary.models import ucs_convert
from slavdict.dictionary.models import VOLUME_LETTERS

OUTPUT_DIR = '../csl/.temp/entries'
URL_PATTERN = u'./словарь/статьи/%s'
READY_VOLUMES = (1, 2)
READY_VOLUMES_LETTERS = reduce(lambda x, y: x + y, (VOLUME_LETTERS[volume]
    for volume in READY_VOLUMES if volume in VOLUME_LETTERS), ())

def csl_url(entry):
    return URL_PATTERN % entry.id

print
print 'Volumes:', u', '.join(str(volume) for volume in READY_VOLUMES)
print 'Letters:', u', '.join(letter for letter in READY_VOLUMES_LETTERS)
print 'Output Folder:', OUTPUT_DIR
print 'Url Pattern:', URL_PATTERN % '<EntryID>'
print

def in_ready_volumes(wordform):
    return wordform.lstrip(u' =')[:1].lower() in READY_VOLUMES_LETTERS

entries1 = []
# Это список всех потенциально возможных статей для выбранных томов,
# ограниченных списком test_entries, если он задан.

lexemes = Entry.objects.all()
test_entries = None
if len(sys.argv) > 1:
    r = re.compile(r'\s*,\s*|\s+')
    s = u' '.join(sys.argv[1:]).strip(' ,')
    test_entries = [int(i) for i in r.split(s)]
if test_entries:
    print 'Entries to dump:', u', '.join(str(i) for i in test_entries)
    lexemes = lexemes.filter(pk__in=test_entries)
else:
    print 'Entries to dump: ALL for the selected volumes'
lexemes = [e for e in lexemes if e.volume(READY_VOLUMES)]
print 'Number of selected lexemes:', len(lexemes)
print

for lexeme in lexemes:

    wordform = lexeme.base_vars[0].idem
    reference = None
    entries1.append((wordform, reference, lexeme))
    key = sort_key1(wordform)

    # Разные ссылочные статьи в пределах выбранных томов

    # 1) Варианты заглавного слова
    for var in lexeme.orth_vars_refs[1:]:
        wordform = resolve_titles(var.idem)
        key2 = sort_key1(wordform)
        if key2 != key:
            reference = ucs_convert(wordform)
            entries1.append((wordform, reference, lexeme))

    # 2) Названия народов
    COMMA = ur',\s+'
    if lexeme.nom_sg:
        wordform = lexeme.nom_sg
        reference = lexeme.nom_sg_ucs_wax[1]
        for wordform, reference in zip(
                re.split(COMMA, wordform), re.split(COMMA, reference)):
            entries1.append((wordform, reference, lexeme))

    # 3) Краткие формы
    #if lexeme.short_form:
    #    wordform = lexeme.short_form
    #    reference = lexeme.short_form_ucs
    #    entries1.append((wordform, reference, lexeme))

    # 4) Причастия
    #for participle in lexeme.participles:
    #    wordform = participle.idem
    #    reference = participle.idem_ucs
    #    entries1.append((wordform, reference, lexeme))

    # 5) Особые случаи
    if lexeme.civil_equivalent == u'быти':
        wordform = u"бꙋ'дꙋчи"
        reference = ucs_convert(wordform)
        entries1.append((wordform, reference, lexeme))


if not test_entries:
    # 6) Добавляем ссылочные статьи, которые будут присутствовать в выводимых
    # томах и ссылаться на какие-то статьи из других томов.
    other_volumes = [e for e in Entry.objects.all() if not e.volume(READY_VOLUMES)]
    for lexeme in other_volumes:
        for participle in lexeme.participles:
            if participle.tp not in ('1', '2', '3', '4'):
                wordform = participle.idem
                if in_ready_volumes(wordform):
                    reference = participle.idem_ucs
                    entries1.append((wordform, reference, lexeme))

def sort_key(x):
    wordform, reference, lexeme = x
    if reference:
        ref_wordform = lexeme.base_vars[0].idem
        key = (sort_key1(wordform), -1, sort_key2(wordform),
               sort_key1(ref_wordform), lexeme.homonym_order or 0, sort_key2(ref_wordform))
    else:
        key = sort_key1(wordform), lexeme.homonym_order or 0, sort_key2(wordform)
    return key

entries1 = sorted(set(entries1), key=sort_key)

entries2 = []
# Список статей, где ссылочные статьи сгруппированы

for key, group in itertools.groupby(entries1, lambda x: x[:2]):
    wordform, reference = key
    if not in_ready_volumes(wordform):
        continue
    # Удаляем из выгрузки отсылочную статью Ассирии, т.к. она неправильно выгружается
    if wordform == u"ассѵрі'и":
        continue
    lst = list(group)
    if len(lst) < 2:
        wordform, reference, lexeme = lst[0]
        entries2.append((wordform, reference, lexeme))
    else:
        if reference is None:  # Статьи не ссылочные
            for wordform, reference, lexeme in lst:
                entries2.append((wordform, reference, lexeme))
        else:  # Статьи ссылочные
            lst = [x[2] for x in sorted(lst, key=sort_key)]
            lexeme = {
                'is_reference': True,
                'referenced_lexemes': lst,
            }
            if all(x.homonym_order for x in lst):
                lexeme['references'] = [
                            {'reference_ucs': lst[0].base_vars[0].idem_ucs,
                             'homonym_order': u',\u00a0'.join(
                                        str(i.homonym_order) for i in lst if i)
                            }]
            else:
                lexeme['references'] = [
                                    {'reference_ucs': x.base_vars[0].idem_ucs,
                                     'homonym_order': x.homonym_order or None}
                                    for x in lst],
            entries2.append((wordform, reference, lexeme))


entries3 = []
# Список статей, в том числе ссылочных, но с устранением ссылок расположенных
# вплотную к целевым статьям

for i, (wordform, reference, lexeme) in enumerate(entries2):
    checklist = set()
    for j in (i - 1, i + 1):
        if 0 <= j < len(entries2) and \
                not entries2[j][1] and not isinstance(entries2[j][2], dict):
            checklist.add(entries2[j][2].id)
    if isinstance(lexeme, Entry):
        in_checklist = lexeme.id in checklist
    elif isinstance(lexeme, dict):
        ids = [referenced_lexeme.id
               for referenced_lexeme in lexeme['referenced_lexemes']]
        in_checklist = len(ids) == 1 and ids[0] not in checklist
    if not reference or not in_checklist:
        entries3.append((wordform, reference, lexeme))

class Reference(unicode):
    def __new__(cls, string, homonym_order=None):
        instance = unicode.__new__(cls, string)
        instance.homonym_order = homonym_order
        return instance

if len(entries1) < 7:
    for wordform, ref, entry in entries1:
        print 'Antconc wf: "%s", UCS ref: "%s", Lexeme: "%s"' % (wordform, ref, entry)
    print

letter_parts = []
part_entries = []
letter = entries3[0][0].lstrip(u' =')[0].upper()
for wordform, group in itertools.groupby(entries3, lambda x: x[0]):
    lst = list(group)
    if wordform.lstrip(u' =')[0].upper() != letter:
        letter_parts.append((letter, part_entries))
        part_entries = []
        letter = wordform.lstrip(u' =')[0].upper()
    if len(lst) < 2:
        wordform, reference, lexeme = lst[0]
        part_entries.append((reference, lexeme))
    else:
        for i, (wordform, reference, lexeme) in enumerate(lst):
            if reference:
                reference = Reference(reference, homonym_order=i+1)
            else:
                lexeme.homonym_order = i + 1
            part_entries.append((reference, lexeme))
letter_parts.append((letter, part_entries))

for letter, entries in letter_parts:
    for reference, entry in entries:
        if not reference:
            html = render_to_string('csl/entry.html', {'entry': entry,
                'csl_url': csl_url })
            filename = os.path.join(OUTPUT_DIR, str(entry.id))
            with open(filename, 'wb') as f:
                f.write(html.encode('utf-8'))

sys.exit(0)
