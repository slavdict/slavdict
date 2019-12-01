#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
Выгрузка базы ссылок и аннотаций для портала "Цсл язык сегодня"

"""
import os
import shutil
import signal
import sys

import django

sys.path.append(os.path.abspath('/var/www/slavdict'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.csl_annotations.models import Annotation
from slavdict.csl_annotations.models import Tag
from slavdict.csl_annotations.models import TAG_CATEGORIES
from slavdict.dictionary.viewmodels import _json

OUTPUT_DIR = '../csl/.temp/refs'
ANNOTATIONS_DIR = OUTPUT_DIR + '/annotations'
TAGTREE_FILE = OUTPUT_DIR + '/filterData.js'
dirs = (OUTPUT_DIR, ANNOTATIONS_DIR)

URL_PATTERN = u'./словарь/статьи/%s'


def csl_url(entry):
    return URL_PATTERN % entry.id


CSI = '\033['
HIDE_CURSOR = CSI + '?25l'
SHOW_CURSOR = CSI + '?25h'
ERASE_LINE = CSI + '2K'
ERASE_LINEEND = CSI + '0K'


def interrupt_handler(signum, frame):
    print >> sys.stderr, SHOW_CURSOR
    sys.exit(0)


for directory in dirs:
    if os.path.exists(directory):
        shutil.rmtree(directory)

for directory in dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)

signal.signal(signal.SIGINT, interrupt_handler)
print >> sys.stderr, HIDE_CURSOR

root_template = u'''export const filterData = [
{data}
];'''
group_template = u'''{{ name: '{name}', items: [
{items}
]}},'''
item_template = u"{{ name: '{name}', index: {index} }},"
parent_item_template = u'''{{ name: '{name}', index: {index}, items: [
{items}
]}},'''


def indent(text, n=2):
    return u'\n'.join(u' ' * n + line for line in text.split('\n'))


def get_index_text(tag):
    index = Annotation.objects.filter(tags=tag).values_list('id', flat=True)
    index = list(index)
    return repr(index)


def get_item_text(tag):
    index_text = get_index_text(tag)
    return item_template.format(name=tag.name, index=index_text)


def get_parent_item_text(tag, subitems):
    index_text = get_index_text(tag)
    subitems_text = indent(u'\n'.join(subitems))
    return parent_item_template.format(name=tag.name, index=index_text,
                                       items=subitems_text)


def get_items_group_text(group_name, items):
    items_text = indent(u'\n'.join(items))
    return group_template.format(name=group_name, items=items_text)


def log_tag(i, N, tag_name):
    note = u'Экспорт фильтров [ %s%% ] %s\r' % (
        int(round(i / float(N) * 100)),
        tag_name + ERASE_LINEEND)
    sys.stderr.write(note.encode('utf-8'))
    return i + 1


categories = []
N = Tag.objects.count()
i = 0
for category, category_name in TAG_CATEGORIES:
    items = []
    for tag in Tag.objects.filter(
            category=category, groups__isnull=True, parent__isnull=True):
        subitems = []
        for sub_tag in tag.tag_set.filter(groups__isnull=True):
            subitems.append(get_item_text(sub_tag))
            i = log_tag(i, N, sub_tag.name)
        for tag_group in tag.taggroup_set.all():
            group_items = []
            for sub_tag in tag.tag_set.filter(groups=tag_group):
                group_items.append(get_item_text(sub_tag))
                i = log_tag(i, N, sub_tag.name)
            group = get_items_group_text(tag_group.name, group_items)
            subitems.append(group)
        if subitems:
            item_text = get_parent_item_text(tag, subitems)
        else:
            item_text = get_item_text(tag)
        items.append(item_text)
        i = log_tag(i, N, tag.name)
    categories.append(get_items_group_text(category_name, items))
text = root_template.format(data=indent(u'\n'.join(categories)))

with open(TAGTREE_FILE, 'wb') as f:
    f.write(text.encode('utf-8'))

sys.stderr.write(ERASE_LINE)
print >> sys.stderr, SHOW_CURSOR
sys.exit(0)
