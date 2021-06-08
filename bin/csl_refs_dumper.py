#!/usr/bin/env python
"""
Выгрузка базы ссылок и аннотаций для портала "Цсл язык сегодня"

Можно менять папку, куда будут выгружаться все данные. Все данные
в папке перед выгрузкой будут удалены:

    SCRIPT --output-dir=/path/to/my/dir

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

if len(sys.argv) == 2 and sys.argv[1].startswith('--output-dir='):
    OUTPUT_DIR = sys.argv[1].split('=')[1]

if os.path.exists(OUTPUT_DIR) and os.path.isdir(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
if not os.path.exists(OUTPUT_DIR):
    os.mkdirs(OUTPUT_DIR)
elif not os.path.isdir(OUTPUT_DIR):
    print('Output dir path is an existing file, not a directory', file=sys.stderr)
    sys.exit(1)

ANNOTATIONS_DIR = OUTPUT_DIR + '/annotations'
TAGTREE_FILE = OUTPUT_DIR + '/filterData.js'
dirs = (OUTPUT_DIR, ANNOTATIONS_DIR)

URL_PATTERN = './словарь/статьи/%s'


def csl_url(entry):
    return URL_PATTERN % entry.id


CSI = '\033['
HIDE_CURSOR = CSI + '?25l'
SHOW_CURSOR = CSI + '?25h'
ERASE_LINE = CSI + '2K'
ERASE_LINEEND = CSI + '0K'


def interrupt_handler(signum, frame):
    print(SHOW_CURSOR, file=sys.stderr)
    sys.exit(0)


for directory in dirs:
    if os.path.exists(directory):
        shutil.rmtree(directory)

for directory in dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)

signal.signal(signal.SIGINT, interrupt_handler)
print(HIDE_CURSOR, file=sys.stderr)

root_template = '''export const filterData = [
{data}
];'''
group_template = '''{{ name: '{name}', items: [
{items}
]}},'''
item_template = "{{ name: '{name}', index: {index} }},"
parent_item_template = '''{{ name: '{name}', index: {index}, items: [
{items}
]}},'''


def indent(text, n=2):
    return '\n'.join(' ' * n + line for line in text.split('\n'))


def get_index_text(tag):
    index = Annotation.objects.filter(tags=tag).values_list('id', flat=True)
    index = list(index)
    return repr(index)


def get_item_text(tag):
    index_text = get_index_text(tag)
    return item_template.format(name=tag.name, index=index_text)


def get_parent_item_text(tag, subitems):
    index_text = get_index_text(tag)
    subitems_text = indent('\n'.join(subitems))
    return parent_item_template.format(name=tag.name, index=index_text,
                                       items=subitems_text)


def get_items_group_text(group_name, items):
    items_text = indent('\n'.join(items))
    return group_template.format(name=group_name, items=items_text)


def log_tag(i, N, tag_name):
    note = 'Экспорт фильтров [ %s%% ] %s\r' % (
        int(round(i / N * 100)),
        tag_name + ERASE_LINEEND)
    sys.stderr.write(note)
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

text = root_template.format(data=indent('\n'.join(categories)))
with open(TAGTREE_FILE, 'w') as f:
    f.write(text)

note = 'Экспорт фильтров завершен.' + ERASE_LINEEND + '\n'
sys.stderr.write(note)


# Выгрузка аннотаций
N = Annotation.objects.count()
for i, annotation in enumerate(Annotation.objects.all()):
    note = 'Экспорт аннотаций [ %s%% ]\r' % int(round(i / N * 100))
    sys.stderr.write(note)
    data = {}
    if annotation.title:
        data['title'] = annotation.get_title_with_author_html()
    if annotation.bib:
        data['bib'] = annotation.get_bib_html()
    if annotation.youtube_id:
        data['youtubeId'] = annotation.youtube_id
        data['videoTitle'] = annotation.get_title_html()
        data['createDate'] = annotation.create_date.isoformat()
    else:
        data['url'] = annotation.url
    if annotation.anchor:
        data['anchor'] = annotation.anchor
    if annotation.teaser:
        data['teaser'] = annotation.get_teaser_html()
    if annotation.annotation:
        data['annotation'] = annotation.get_annotation_html()
    filename = str(annotation.id) + '.json'
    path = os.path.join(ANNOTATIONS_DIR, filename)
    with open(path, 'w') as f:
        f.write(_json(data))

note = 'Экспорт аннотаций завершен.' + ERASE_LINEEND + '\n'
sys.stderr.write(note)
sys.stderr.write(ERASE_LINE)
print(SHOW_CURSOR, file=sys.stderr)
sys.exit(0)
