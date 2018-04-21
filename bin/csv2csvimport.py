#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from os.path import dirname
from os.path import abspath

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')

import django
django.setup()

from slavdict import unicode_csv

csvin = open(sys.argv[1])
csvout = open(sys.argv[2], 'w')

csv_reader = unicode_csv.UnicodeReader(csvin,
        dialect=unicode_csv.calc, encoding='utf-8')
csv_writer = unicode_csv.UnicodeWriter(csvout,
        dialect=unicode_csv.calc, encoding='utf-8')

def writedata(lemma, wordforms_list, antconc_query, additional_info):
    converted_row = (
        lemma,  # Заглавное слово
        u'',  # Гражданское написание
        wordforms_list,  # Список словоформ
        antconc_query,  # Запрос для АнтКонка
        u'',  # Авторы
        additional_info,  # Комментарий к статье
        u'',  # Номер омонима
        u'',  # Смыслоразличительный ярлык омонима
        u'',  # Является ли дубликатом
    )
    csv_writer.writerow(converted_row)

converted_lemma = None
i = -1
for row in csv_reader:
    # Пропускаем первую строку, в ней должны быть заголовки:
    # Заглавное слово, Словоформы, Комментарий.
    i += 1
    if i == 0:
        converted_row = (
            u'Заглавное слово',
            u'Гражданское написание',
            u'Список словоформ',
            u'Запрос для АнтКонка',
            u'Авторы',
            u'Комментарий к статье',
            u'Номер омонима',
            u'Смыслоразличительный ярлык омонима',
            u'Является ли дубликатом',
        )
        csv_writer.writerow(converted_row)
        continue

    lemma, wordform, additional_info = row

    assert i != 1 or lemma.strip(), u'''

        Первая строка зарезервирована для заголовков,
        а вторая должна обязательно содержать данные в первом поле.

        '''
    if lemma.strip():
        if converted_lemma:
            antconc_query = ur'(^|(?<=[ \t\r\n]))('
            antconc_query += u'|'.join(
                u'[{0}{1}]{2}'.format(
                    wf[0].upper(),
                    wf[0].lower(),
                    wf[1:].replace(u'^', ur'\^'))
                for wf in wordforms)
            antconc_query += ur')(?=[ \t\r\n.,;:!])'

            wordforms_list = u', '.join(wordforms)

            writedata(converted_lemma, wordforms_list, antconc_query,
                      converted_additional_info)

        converted_lemma = lemma
        wordforms = [wordform]
        converted_additional_info = additional_info
    else:
        wordforms.append(wordform)

csvout.close()
csvin.close()
