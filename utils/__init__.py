# -*- coding: utf-8 -*-
__all__ = ('p', 's', 'd')

import re

from slavdict.dictionary.models import Example

def p(x):
    counter = 0
    for e in Example.objects.all():
        if re.search(x, e.address_text):
            print e.address_text
            counter += 1
    print u'Найдено адресов: %i' % counter

def s(x, y, without_mtime=True):
    counter = 0
    for e in Example.objects.all():
        if re.search(x, e.address_text):
            e.address_text = re.sub(x, y, e.address_text)
            e.save(without_mtime=without_mtime)
            counter += 1
    print u'Исправлено адресов: %i' % counter

def d(x, y, without_mtime=True):
    counter = 0
    for e in Example.objects.all():
        if re.search(x, e.address_text):
            dummy = re.sub(x, y, e.address_text)
            print '%s --> %s' % (e.address_text, dummy)
            counter += 1
    print u'Будет исправлено адресов: %i' % counter
