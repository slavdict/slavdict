import os
import re
import sys
from collections import defaultdict

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry
from slavdict.dictionary.utils import civilrus_convert
from slavdict.dictionary.utils import get_query_orterms
from slavdict.dictionary.utils import make_query_from_orterms

path = os.path.expanduser('~/Documents/slavdict_slovnik')
filename = 'vocabulary.csv'
diff_filename = 'vocabulary_diff.csv'

filepath = os.path.join(path, filename)
diff_filepath = os.path.join(path, diff_filename)


class Row:
    def __init__(self, columns):
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
    civil = civilrus_convert(form).lower()
    civil_without_er = civil.replace('ъ', '')
    civil_without_erj = civil_without_er.replace('ь', '')
    data[civil].append(entry)
    if civil_without_er != civil:
        data[civil_without_er].append(entry)
    if civil_without_erj != civil and civil_without_erj != civil_without_er:
        data[civil_without_erj].append(entry)


def link_form(form, query_voc, main_civil):
    civil = civilrus_convert(form).lower()
    civil_without_er = civil.replace('ъ', '')
    civil_without_erj = civil_without_er.replace('ь', '')
    query_voc[civil].union(query_voc[main_civil])
    if civil_without_er != civil:
        query_voc[civil_without_er].union(query_voc[main_civil])
    if civil_without_erj != civil and civil_without_erj != civil_without_er:
        query_voc[civil_without_erj].union(query_voc[main_civil])


def get_forms(entry):
    forms = []
    for ov in e.orth_vars:
        forms.append(ov.idem)
    for ethn in e.ethnonyms:
        forms.append(ethn[0])
    for sf in e.short_forms:
        forms.append(sf[0])
    for participle in e.participles:
        forms.append(participle.idem)
    return forms


def get_query_voc(voc, entries):
    query_voc = defaultdict(set)
    for item in voc:
        civil = re.sub('[ъь]', '', item.civil.strip())
        query_voc[civil].add(item.query)
        if civil in entries:
            query_voc[civil].union(e.antconc_query for e in entries[civil])
        for e in entries[civil]:
            for form in get_forms(e):
                link_form(form, query_voc, civil)
    return query_voc


entries = defaultdict(list)
for e in Entry.objects.all():
    for form in get_forms(e):
        add_form(form, e, entries)

voc = load_data(filepath)
write_diff(voc, entries)
query_voc = get_query_voc(voc, entries)

orphans = []
for entry in Entry.objects.all():
    if not entry.antconc_query.strip():
        for form in get_forms(entry):
            civil = re.sub('[ъь]', '', civilrus_convert(form).strip())
            if civil in query_voc:
                orterms = []
                for item in query_voc[civil]:
                    orterms.extend(get_query_orterms(item))
                value = make_query_from_orterms(orterms)
                if value:
                    entry.antconc_query = value
                    entry.save()
                    print(entry.civil_equivalent, value)
                    break
        else:
            print(entry.civil_equivalent)
            orphans.append(entry)

print('Осталось статей без запросов:', len(orphans))
