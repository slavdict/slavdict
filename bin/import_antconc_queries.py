import os
import re
import sys
from collections import defaultdict

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry
from slavdict.dictionary.utils import antconc_wordform_query
from slavdict.dictionary.utils import civilrus_convert
from slavdict.dictionary.utils import resolve_titles

path = os.path.expanduser('~/Documents/slavdict_slovnik')
filename = 'vocabulary.csv'
diff_filename = 'vocabulary_diff.csv'

filepath = os.path.join(path, filename)
diff_filepath = os.path.join(path, diff_filename)


class Row:
    def __init__(self, columns):
        print(columns)
        (self.lemma, self.civil, self.wordforms, self.query, self.author,
         self.comment, self.homonym_number, self.homonym_gloss,
         self.dup) = columns


def load_data(filepath):
    data = []
    with open(filepath) as f:
        f.readline()
        for line in f.readlines():
            row = Row(re.split(r'","', line.strip()[1:-1]))
            data.append(row)
    return data


def write_diff(voc, entries):
    with open(diff_filepath, 'w') as f:
        f.write(','.join('"%s"' % title for title in [
            'Заглавное слово', 'Гражданское написание', 'Список словоформ',
            'Запрос для АнтКонка', 'Авторы', 'Комментарий к статье',
            'Номер омонима', 'Смыслоразличительный ярлык омонима',
            'Является ли дубликатом']))
        f.write('\n')
        for item in voc:
            if item.civil not in entries:
                f.write(','.join('"%s"' % value for value in [
                    item.lemma, item.civil, item.wordforms, item.query,
                    item.author, item.comment,
                    item.homonym_number, item.homonym_gloss, item.dup]))
                f.write('\n')


def add_form(form, entry, data):
    civil = civilrus_convert(form)
    civil_without_er = civil.replace('ъ', '')
    data[civil].append(entry)
    if civil_without_er != civil:
        data[civil_without_er].append(entry)


entries = defaultdict(list)
for e in Entry.objects.all():
    for ov in e.orth_vars:
        add_form(ov.idem, e, entries)
    for ethn in e.ethnonyms:
        add_form(ethn[0], e, entries)
    for sf in e.short_forms:
        add_form(sf[0], e, entries)
    for participle in e.participles:
        add_form(participle.idem, e, entries)

voc = load_data(filepath)
write_diff(voc, entries)
