#!/usr/bin/env python
# coding: utf-8
import os
import sys

import django
sys.path.append(
    os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.models import Entry, PART_OF_SPEECH_MAP
from slavdict.dictionary.models import TRANSITIVITY_MAP
from slavdict.unicode_csv import UnicodeWriter

def write_csv(filename, entries):
    uw = UnicodeWriter(open(filename, 'w'))
    for e in (e for e in entries if e.first_volume):
        ecolumn = e.civil_equivalent + {1: u'¹', 2: u'²'}.get(e.homonym_order, u'')
        for m in list(e.meanings) + list(e.metaph_meanings):
            meaning = m.meaning.strip()
            gloss = m.gloss.strip()
            if meaning or gloss:
                uw.writerow((str(m.id), ecolumn, u'%s ⏹ %s' % (meaning, gloss)))
                if ecolumn:
                   ecolumn = u''
            for cm in m.child_meanings:
                meaning = cm.meaning.strip()
                gloss = cm.gloss.strip()
                if meaning or gloss:
                    row = (str(cm.id), ecolumn, u'• %s ⏹ %s' % (meaning, gloss))
                    uw.writerow(row)
                    if ecolumn:
                       ecolumn = u''
    uw.stream.close()

poss_adj = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP['adjective'],
    possessive=True).order_by('civil_equivalent')
non_poss_adj = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP[
    'adjective'], possessive=False).order_by('civil_equivalent')
part_adj = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP[
    'participle-adjective']).order_by('civil_equivalent')
pronouns = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP['pronoun']
    ).order_by('civil_equivalent')
adverbs = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP['adverb']
    ).order_by('civil_equivalent')
conjunctions = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP[
    'conjunction']).order_by('civil_equivalent')
prepositions = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP[
    'adposition']).order_by('civil_equivalent')
particles = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP['particle']
    ).order_by('civil_equivalent')
interjections = Entry.objects.filter(part_of_speech=PART_OF_SPEECH_MAP[
    'interjection']).order_by('civil_equivalent')
trans_verbs = (e for e in Entry.objects.filter(
    part_of_speech=PART_OF_SPEECH_MAP['verb']).order_by('civil_equivalent')
    if e.transitivity_from_meanings == TRANSITIVITY_MAP['transitive'])
intrans_verbs = (e for e in Entry.objects.filter(
    part_of_speech=PART_OF_SPEECH_MAP['verb']).order_by('civil_equivalent')
    if e.transitivity_from_meanings == TRANSITIVITY_MAP['intransitive'])
labile_verbs = (e for e in Entry.objects.filter(
    part_of_speech=PART_OF_SPEECH_MAP['verb']).order_by('civil_equivalent')
    if e.transitivity_from_meanings not in (TRANSITIVITY_MAP['transitive'],
        TRANSITIVITY_MAP['intransitive']))
other = Entry.objects.exclude(part_of_speech__in=[
    PART_OF_SPEECH_MAP['noun'],
    PART_OF_SPEECH_MAP['adjective'],
    PART_OF_SPEECH_MAP['pronoun'],
    PART_OF_SPEECH_MAP['verb'],
    PART_OF_SPEECH_MAP['adverb'],
    PART_OF_SPEECH_MAP['conjunction'],
    PART_OF_SPEECH_MAP['adposition'],
    PART_OF_SPEECH_MAP['particle'],
    PART_OF_SPEECH_MAP['interjection'],
    PART_OF_SPEECH_MAP['participle-adjective'],
    ]).order_by('civil_equivalent')

non_nouns = (
    (poss_adj, 'adjectives_possessive_meanings.csv'),
    (non_poss_adj, 'adjectives_non-possessive_meanings.csv'),
    (part_adj, 'participle-adjectives_meanings.csv'),
    (pronouns, 'pronouns_meanings.csv'),
    (adverbs, 'adverbs_meanings.csv'),
    (conjunctions, 'conjunctions_meanings.csv'),
    (prepositions, 'prepositions_meanings.csv'),
    (particles, 'particles_meanings.csv'),
    (interjections, 'interjections_meanings.csv'),
    (trans_verbs, 'verbs_transitive_meanings.csv'),
    (intrans_verbs, 'verbs_intransitive_meanings.csv'),
    (labile_verbs, 'verbs_labile_meanings.csv'),
    (other, 'other_meanings.csv'),
)

for entries, filename in non_nouns:
    write_csv(filename, entries)
