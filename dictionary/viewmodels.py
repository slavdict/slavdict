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

statuses = [ {'id': 'all', 'name': u'любой'}, ] + category_values('entryStatus')

jsonAuthors = _json(authors)
jsonStatuses = _json(statuses)

tupleAuthors = _tuple(authors)
tupleStatuses = _tuple(statuses)
