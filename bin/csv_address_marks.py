#!/usr/bin/env python
# coding: utf-8
import os
import re
import sys

import django
sys.path.append(
    os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Example
from slavdict.unicode_csv import UnicodeWriter

def write_csv(filename, examples):
    uw = UnicodeWriter(open(filename, 'w'))
    NON_MARK_CHARS = ur'[\s\ \u00A0,0-9\.;:\-\u2011\!\(\)\[\]\?—–«»…]+'
    register = {}
    for e in (e for e in examples if e.host_entry.volume(1)):
        for mark in re.split(NON_MARK_CHARS, e.address_text):
            if mark in register:
                register[mark] = (register[mark][0] + 1, e)
            else:
                register[mark] = (1, e)
    for mark, (number, e) in sorted(register.items()):
        row = (
            mark,
            str(number),
            e.address_text,
            str(e.id),
            e.host_entry.civil_equivalent,
        )
        uw.writerow(row)
    uw.stream.close()

write_csv('address_marks.csv', Example.objects.all())
