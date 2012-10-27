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
    {'id': 'all',  'name': u'Все авторы'},
    {'id': 'none', 'name': u'Статьи без автора'} ] + [

    {'id': str(u.id), 'name': u.__unicode__()}
    for u in CustomUser.objects.filter(groups__name=u'authors')
]

genders = [
    {'id': 'all',  'name': u'любой'},
    {'id': 'none', 'name': u'где род не указан'},
] + category_values('gender')

pos = [
    {'id': 'all',  'name': u'любая'},
    {'id': 'none', 'name': u'где часть речи не указана'},
] + category_values('partOfSpeech')

sortdir = (
    {'id': '', 'name': u'по возрастанию'},
    {'id': '-','name': u'по убыванию'},
)

sortbase = (
    {'id': 'alph', 'name': u'гражданского написания'},
    {'id': 't',    'name': u'времени изменения'},
)

statuses = [ {'id': 'all', 'name': u'любой'}, ] + category_values('entryStatus')

jsonAuthors = _json(authors)
jsonGenders = _json(genders)
jsonPos = _json(pos)
jsonSortbase = _json(sortbase)
jsonSortdir = _json(sortdir)
jsonStatuses = _json(statuses)

tupleAuthors = _tuple(authors)
tupleGenders = _tuple(genders)
tuplePos = _tuple(pos)
tupleSortbase = _tuple(sortbase)
tupleSortdir = _tuple(sortdir)
tupleStatuses = _tuple(statuses)
