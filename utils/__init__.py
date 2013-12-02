# -*- coding: utf-8 -*-
__all__ = ('p', 's')

from slavdict.dictionary.models import Example

def p(x):
    for e in Example.objects.all():
        if x in e.address_text:
            print e.address_text

def s(x, y, without_mtime=True):
    for e in Example.objects.all():
        if x in e.address_text:
            e.address_text = e.address_text.replace(x, y)
            e.save(without_mtime=without_mtime)
