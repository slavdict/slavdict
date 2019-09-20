#!/usr/bin/env python
# coding: utf-8
'''

Скрипт подготовки сырых данных для словника

Из антконка выгружается файл с частотой словоформ для того
подкорпуса, по которуму делается словник. Файл подается на вход
скрипту. Сприпт смотрит по базе встечаемость словоформ и на каждую
букву выдает один или два файла. Файл со списком словоформ,
присутствующих в базе, если на данную букву словоформы в базе
имеются. И файл словоформ не встретившихся в базе, которые,
следовательно, надо вручную лематизировать.

'''

import itertools
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

# Файл со словником в формате "словоформа\tчастотность"
FILENAME = sys.argv[1]

# Шаблон имени tsv-файла, в который будут записаны все словоформы на текущую
# букву, которые не встретились в базе. Последовательность символов {0}
# в шаблоне будет заменена на текущую букву.
NOT_IN_FILENAME = unicode(sys.argv[2])

# Шаблон имени tsv-файла, в который будут записаны все словоформы на текущую
# букву, которые присутствуют в базе. Последовательность символов {0}
# в шаблоне будет заменена на текущую букву.
IN_FILENAME = unicode(sys.argv[3])

glossary_freq = open(FILENAME).read().decode('utf-8').strip().split('\n')
glossary_freq = [l.split('\t') for l in glossary_freq if l.strip()]
glossary_freq = [
        # Если слово не всё дается заглавными буквами, то понижаем регистр
        # только начальной буквы, чтобы сохранить заглавные внутри слова,
        # соответствующие буквенным титлам.
        (s.lower() if s.isupper() else s[:1].lower() + s[1:], int(n))
        for (s, n) in glossary_freq]
glossary_freq.sort(key=lambda x: civilrus_convert(x[0]).lower())

glossary_freq_upd = []
wordform0, freq0 = glossary_freq[0][0], 0
glossary_freq_n = len(glossary_freq)
i = 0
while i < glossary_freq_n:
    wordform1, freq1 = glossary_freq[i]
    if wordform0 == wordform1:
        freq0 += freq1
    else:
        glossary_freq_upd.append((wordform0, freq0))
        wordform0, freq0 = wordform1, freq1
    i += 1
glossary_freq_upd.append((wordform0, freq0))

glossary_freq_by_letter = [
    (key, list(iterator))
    for key, iterator in itertools.groupby(
        glossary_freq_upd,
        lambda x: civilrus_convert(unicode(x[0]))[:1].lower()
    )]


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


for LETTER, glossary_freq in glossary_freq_by_letter:

    if LETTER in u'ъь':
        continue

    glossary = [s for (s, n) in glossary_freq]
    xindices = set()

    civil_glossary = [civilrus_convert(wordform) for wordform in glossary]
    similar_forms_map = defaultdict(list)
    for i, civil_form in enumerate(civil_glossary):
        similar_forms_map[civil_form].append(i)

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

    filename1 = NOT_IN_FILENAME.format(LETTER)
    filename2 = IN_FILENAME.format(LETTER)
    write_tsv(filename1, new_glossary_freq, len(glossary), len(xindices))
    if len(slavdict_glossary) > 0:
        with open(filename2, 'w') as f:
            f.write(u'Словоформы, присутствующие в базе:\n\n'.encode('utf-8'))
            for lemma, civil_representaion in slavdict_glossary:
                f.write(lemma.encode('utf-8'))
                f.write('\n')
