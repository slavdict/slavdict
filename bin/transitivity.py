# -*- coding: utf-8 -*-
from itertools import chain

from slavdict.dictionary.models import *

def transitivity(arg):
    if isinstance(arg, int):
        e = Entry.objects.get(pk=arg)
    elif isinstance(arg, Entry):
        e = arg
    else:
        print 'wrong argument:', arg
        return

    if not e.is_part_of_speech('verb'):
        print u'Лексема не является глаголом.'
        return

    for meaning in e.meanings:
        print
        print e.civil_equivalent
        if meaning.transitivity:
            print u'\t' + meaning.get_transitivity_display()
        else:
            print u'\t[переходность не задана]'
        print u'\t%s' % meaning.meaning, u'|', meaning.gloss

        for ex in chain(meaning.examples,
                *(m.examples for m in meaning.child_meanings)):
            print u'\t\t* %s' % ex.example

        x = raw_input(u'\nЧто с переходностью? '
            u'Перех./неперех./смешанный [t/i/l]\n'
            u'(Enter = ничего не менять): '.encode('utf-8'))
        x = x.lower().strip()
        if x in (u't', u'е'):
            meaning.transitivity = u't'
            meaning.save(without_mtime=True)
        elif x in (u'i', u'ш'):
            meaning.transitivity = u'i'
            meaning.save(without_mtime=True)
        elif x in (u'l', u'д'):
            meaning.transitivity = u'i'
            meaning.save(without_mtime=True)

# vi: set ai et sw=4 ts=4 :
