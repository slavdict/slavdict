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

MAX_DISTANCE = 5
if len(sys.argv) > 1:
    try:
        MAX_DISTANCE = int(sys.argv[1])
    except ValueError:
        print('The argument must be an integer')
        print('for Maximum Levenshtein distance value.')
print('Maximum Levenstein distance used:', MAX_DISTANCE)
print()

from slavdict.dictionary.models import Entry, levenshtein_distance

CSI = '\033['
HIDE_CURSOR = CSI + '?25l'
SHOW_CURSOR = CSI + '?25h'
ERASE_LINE = CSI + '2K'
ERASE_LINEEND = CSI + '0K'

def write_csv(filename, entries):
    uw = csv.writer(open(filename, 'w'))
    N = len(entries)
    sys.stderr.write(HIDE_CURSOR)
    for j, e in enumerate(e for e in entries
            if e.volume([1, 2]) or e.civil_equivalent.startswith('!')):
        note = 'Поиск похожих примеров [ %s%% ] %s\r' % (
                int(j / N * 100), e.civil_equivalent + ERASE_LINEEND)
        sys.stderr.write(note)

        ecolumn = e.civil_equivalent + {1: '¹', 2: '²'}.get(e.homonym_order, '')
        all_examples = e.all_examples()
        example_matches = []
        for i in range(len(all_examples) - 1):
            ex1, ex2 = all_examples[i:i+2]
            if levenshtein_distance(ex1.ts_example, ex2.ts_example) < MAX_DISTANCE:
                example_matches.append((ex1, ex2))
        if example_matches:
            uw.writerow((ecolumn, '', ''))
            for match in example_matches:
                uw.writerow(('', match[0].example, match[0].address_text))
                uw.writerow(('', match[1].example, match[1].address_text))
                uw.writerow(('','',''))
    sys.stderr.write(ERASE_LINE + SHOW_CURSOR)
    uw.stream.close()

filename = 'similar_juxtaposed_examples_%s.csv' % MAX_DISTANCE
entries = list(Entry.objects.order_by('civil_equivalent'))
write_csv(filename, entries)
