#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
Скрипт делает выгрузку словарной базы для портала "Цсл язык сегодня"

При необходимости сделать выборочную выгрузку скрипту допустимо передавать
номера статей в качестве аргументов. Каждый номер можно отделять от другого
пробелами, запятыми или запятыми с пробелами, например:

    SCRIPT 1177,123 89 945, 234
"""
import collections
import itertools
import os
import re
import shutil
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

OUTPUT_DIR = '../csl/.temp/slavdict_generated'
ENTRIES_DIR = OUTPUT_DIR + '/entries'
FULL_IX = OUTPUT_DIR + '/full_index'
PART_IX = OUTPUT_DIR + '/partial_index'
dirs = (OUTPUT_DIR, ENTRIES_DIR, FULL_IX, PART_IX):

URL_PATTERN = u'./словарь/статьи/%s'
READY_VOLUMES = (1, 2)
READY_VOLUMES_LETTERS = reduce(lambda x, y: x + y, (VOLUME_LETTERS[volume]
    for volume in READY_VOLUMES if volume in VOLUME_LETTERS), ())
HINTS_NUMBER = 7

def csl_url(entry):
    return URL_PATTERN % entry.id

print
print 'Volumes:', u', '.join(str(volume) for volume in READY_VOLUMES)
print 'Letters:', u', '.join(letter for letter in READY_VOLUMES_LETTERS)
print 'Output Folder:', ENTRIES_DIR
print 'Url Pattern:', URL_PATTERN % '<EntryID>'
print

def in_ready_volumes(wordform):
    return wordform.lstrip(u' =')[:1].lower() in READY_VOLUMES_LETTERS

for directory in dirs:
    if os.path.exists(directory):
        shutil.rmtree(directory)

for directory in dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)



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

# Объединение статей по начальным буквам
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

# Вывод статей
for letter, entries in letter_parts:
    for reference, entry in entries:
        if not reference:
            html = render_to_string('csl/entry.html', { 'entry': entry,
                'csl_url': csl_url })
            filename = os.path.join(ENTRIES_DIR, str(entry.id))
            with open(filename, 'wb') as f:
                f.write(html.encode('utf-8'))


# Вывод указателя статей

KEY_ENTRY_ID = 'i'
KEY_ENTRY = 'e'
KEY_HOMONYM_ORDER = 'o'
KEY_HOMONYM_GLOSS = 'g'
KEY_PART_OF_SPEECH = 'p'
KEY_REFEREE = 'r'

KEY_INDEX = 'i'
KEY_MATCH = 'm'
KEY_HINTS = 'h'

def get_hint(entry):
    hint =  {
        KEY_ENTRY_ID: entry.id,  # id лексемы в базе
        KEY_ENTRY: entry.base_vars[0].idem_ucs,  # Заглавное слово
    }
    if entry.homonym_order:
        hint[KEY_HOMONYM_ORDER] = entry.homonym_order  # Номер омонима
        hint[KEY_PART_OF_SPEECH] = entry.get_part_of_speech_display()  # Часть речи
    if entry.homonym_gloss.strip():
        hint[KEY_HOMONYM_GLOSS] = entry.homonym_gloss.strip()  # Комментарий к омониму
    return hint

def get_reference_hint(reference, lexeme):
    hint = {
        KEY_ENTRY: reference,
    }
    if isinstance(lexeme, Entry):
        hint[KEY_REFEREE] = get_hint(lexeme)
    else:
        referenced_lexemes = lexeme['referenced_lexemes']
        referee_hint = get_hint(referenced_lexemes[0])
        if (len(referenced_lexemes) > 1
                and all(e.homonym_order for e in referenced_lexemes)):
            referee_hint[KEY_HOMONYM_ORDER] = u',\u00a0'.join(
                    str(e.homonym_order) for e in referenced_lexemes if e)
        hint[KEY_REFEREE] = referee_hint
    return hint

def already_in(hints, new_hint):
    for hint in hints:
        SAME_ENTRY = new_hint[KEY_ENTRY] == hint[KEY_ENTRY]
        SAME_HOMONYM = (KEY_HOMONYM_ORDER in new_hint
                and KEY_HOMONYM_ORDER in hint
                and new_hint[KEY_HOMONYM_ORDER] == hint[KEY_HOMONYM_ORDER])
        NON_HOMONYM = (KEY_HOMONYM_ORDER not in new_hint
                and KEY_HOMONYM_ORDER not in hint)
        if SAME_ENTRY and (SAME_HOMONYM or NON_HOMONYM):
            return True

partial_index = {}
full_index = collections.defaultdict(list)()
for wordform, reference, lexeme in entries2:
    slug = convert_for_index(wordform)
    ix_layer_pointer = partial_index
    for i, char in enumerate(slug):
        prefix = slug[:i + 1]
        if char not in ix_layer_pointer:
            ix_layer_pointer[char] = {
               KEY_INDEX: {},  # index: Следующий уровень индекса
               KEY_HINTS: [],  # hints: Первые N результатов, для подсказок при поиске
               KEY_MATCH: slug  # match: Совпадение в начале слова
            }
        if reference:
            hint = get_reference_hint(reference, lexeme)
        else:
            hint = get_hint(lexeme)
        hints = ix_layer_pointer[char][KEY_HINTS]
        if not already_in(hints, hint) and len(hints) < HINTS_NUMBER:
            hints.append(hint)
        results = full_index[slug]
        if not already_in(results, hint):
            results.append(hint)
        ix_layer_pointer = ix_layer_pointer[char][KEY_INDEX]


sys.exit(0)
