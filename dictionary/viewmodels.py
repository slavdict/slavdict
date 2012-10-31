# -*- coding: utf-8 -*-
import json

from custom_user.models import CustomUser
from directory.models import CategoryValue

def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',',':'))

def _tuple(x):
    return tuple((i['id'], i['name']) for i in x)

def category_values(category):
    return [
        {'id': str(item.id), 'name': item.tag}
        for item
        in CategoryValue.objects.filter(category__slug=category)
    ]

authors = [
    {'id': 'all',  'name': u'все авторы'},
    {'id': 'none', 'name': u'статьи без автора'} ] + [

    {'id': str(u.id), 'name': u.__unicode__()}
    for u in CustomUser.objects.filter(groups__name=u'authors')
]

canonical_name = (
    {'id': 'all', 'name': u'все имена'},
    {'id': '1',   'name': u'только канонические'},
    {'id': '0',   'name': u'только неканонические'},
)

genders = [
    {'id': 'all',  'name': u'любой'},
    {'id': 'none', 'name': u'где род не указан'},
] + category_values('gender')

onyms = [
    {'id': 'all',  'name': u'любой'},
    {'id': 'none', 'name': u'не имя собственное'},
] + category_values('onym')

pos = [
    {'id': 'all',  'name': u'любая'},
    {'id': 'none', 'name': u'где часть речи не указана'},
] + category_values('partOfSpeech')

possessive = (
    {'id': 'all', 'name': u''},
    {'id': '1',   'name': u'притяжательные'},
    {'id': '0',   'name': u'непритяжательные'},
)

sortdir = (
    {'id': '',  'name': u'по возрастанию'},
    {'id': '-', 'name': u'по убыванию'},
)

sortbase = (
    {'id': 'alph', 'name': u'гражданского написания'},
    {'id': 't',    'name': u'времени изменения'},
)

tantum = [
    {'id': 'all',  'name': u'любое'},
    {'id': 'none', 'name': u'где число не указано'},
] + category_values('tantum')

statuses = [ {'id': 'all', 'name': u'любой'}, ] + category_values('entryStatus')


jsonAuthors = _json(authors)
jsonCanonicalName = _json(canonical_name)
jsonGenders = _json(genders)
jsonOnyms = _json(onyms)
jsonPos = _json(pos)
jsonPossessive = _json(possessive)
jsonSortbase = _json(sortbase)
jsonSortdir = _json(sortdir)
jsonStatuses = _json(statuses)
jsonTantum = _json(tantum)

tupleAuthors = _tuple(authors)
tupleCanonicalName = _tuple(canonical_name)
tupleGenders = _tuple(genders)
tupleOnyms = _tuple(onyms)
tuplePos = _tuple(pos)
tuplePossessive = _tuple(possessive)
tupleSortbase = _tuple(sortbase)
tupleSortdir = _tuple(sortdir)
tupleStatuses = _tuple(statuses)
tupleTantum = _tuple(tantum)
