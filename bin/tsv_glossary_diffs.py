#!/usr/bin/env python
# coding: utf-8

import os
import sys
from os.path import dirname
from os.path import abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')

import django
django.setup()

from collections import defaultdict
import re

from slavdict.dictionary.models import civilrus_convert
from slavdict.dictionary.models import Entry

LETTER = sys.argv[1].decode('utf-8')  # Буква, для которой осуществляется поиск
    # различий в словнике базы и словнике из файла
FILENAME = sys.argv[2]  # Файл со словником в формате "словоформа\tчастотность"

OUTPUT_FILENAME = sys.argv[3]  # tsv-файл, в который будут записаны
    # все словоформы на выбранную букву, которые не встретились в базе.
VS_FILENAME = sys.argv[4]  # tsv-файл, в который будут записаны все
    # словоформы на выбранную букву, которые присутствуют в базе.

glossary_freq = open(FILENAME).read().decode('utf-8').strip().split('\n')
glossary_freq = [l.split('\t') for l in glossary_freq if l.strip()]
glossary_freq = [(s[:1].lower() + s[1:], int(n)) for (s, n) in glossary_freq]
glossary_freq_upd = []
continue_flag = False
i = 0
while i + 1 < len(glossary_freq):
    wordform0, freq0 = glossary_freq[i]
    wordform1, freq1 = glossary_freq[i + 1]
    if wordform0 == wordform1:
        # Подразумевается, что подряд два одинаковых слова могут
        # встретиться только один раз, так как в словнике все слова
        # уникальны с учетом регистра.
        glossary_freq_upd.append((wordform0, freq0 + freq1))
        i += 2
    else:
        glossary_freq_upd.append((wordform0, freq0))
        i += 1
if i + 1 == len(glossary_freq):
    glossary_freq_upd.append(glossary_freq[-1])
glossary_freq = glossary_freq_upd

glossary = [s for (s, n) in glossary_freq]
xindices = set()

civil_glossary = [civilrus_convert(wordform) for wordform in glossary]
similar_forms_map = defaultdict(list)
for i, civil_form in enumerate(civil_glossary):
    similar_forms_map[civil_form].append(i)

def find_form(form, glossary):
    try:
        xindices.add(glossary.index(form))
    except ValueError:
        pass

RE = re.compile(r'[,;\s]+')
def get_wordform_list(entry):
    wordforms = []
    if entry.word_forms_list.strip():
        wordforms = RE.split(entry.word_forms_list.strip())
    wordforms.extend([entry.genitive, entry.short_form,
                      entry.sg1, entry.sg2, entry.nom_sg])
    return wordforms

slavdict_glossary = []

for e in Entry.objects.all():
    if e.civil_equivalent.lower().startswith(LETTER):
        for ov in e.orth_vars.all():
            find_form(ov.idem, glossary)
            find_form(civilrus_convert(ov.idem), civil_glossary)
        for wordform in get_wordform_list(e):
            wordform = wordform.strip()
            if wordform and not wordform.startswith(u'-'):
                find_form(wordform, glossary)
                find_form(civilrus_convert(wordform), civil_glossary)
        slavdict_glossary.append((e.orth_vars.first().idem, e.civil_equivalent))

def write_tsv(filename, slovnik, total_n, removed_n):
  with open(filename, 'w') as f:
    f.write(u'Словоформ в АнтКонке:\t{0}\n'.format(total_n)
                                           .encode('utf-8'))
    f.write(u'Отсеяны по данным из базы:\t{0}\n'.format(removed_n)
                                                .encode('utf-8'))
    f.write(u'Осталось после отсева:\t{0}\n'.format(total_n - removed_n)
                                            .encode('utf-8'))
    f.write('\t\n')
    f.write(u'Словоформа\tЧастотность\n'.encode('utf-8'))
    for (wordform, N) in slovnik:
        f.write(u'{0}\t{1}\n'.format(wordform, N).encode('utf-8'))

civil_xindicies = set()
for i, civil_form in enumerate(civil_glossary):
    if i in xindices:
        assert i in similar_forms_map[civil_form]
        civil_xindicies.update(similar_forms_map[civil_form])
xindices.update(civil_xindicies)

new_glossary_freq = []
for i, x in enumerate(glossary_freq):
    if i not in xindices:
        new_glossary_freq.append(x)

new_glossary_freq.sort(key=lambda x: civilrus_convert(x[0]))
slavdict_glossary.sort(key=lambda x: x[1])

write_tsv(OUTPUT_FILENAME, new_glossary_freq, len(glossary), len(xindices))
with open(VS_FILENAME, 'w') as f:
    for lemma, civil_representaion in slavdict_glossary:
        f.write(lemma.encode('utf-8'))
        f.write('\n')
