# -*- coding: utf-8 -*-
from dictionary.models import Entry

def get_entries(form):
    entries = Entry.objects
    FILTER_PARAMS = {}
    FILTER_EXCLUDE_PARAMS = {}
    SORT_PARAMS = []
    PARSING_ERRORS = []

    # Сортировка
    DEFAULT_SORT = '-t'
    sortdir = form['sortdir']
    sortbase = form['sortbase']
    sort = sortdir + sortbase
    if not sort:
        sort = form['sort'] or DEFAULT_SORT
    VALID_SORT_PARAMS = {
        'alph': ('civil_equivalent', 'homonym_order'),
        '-alph': ('-civil_equivalent', '-homonym_order'),
        't': ('mtime', 'id'),
        '-t': ('-mtime', '-id'),
        }
    if sort in VALID_SORT_PARAMS:
        SORT_PARAMS = VALID_SORT_PARAMS[sort]
    else:
        PARSING_ERRORS.append('sort')

    # Статьи начинаются с
    find = form['find']
    if find:
        FILTER_PARAMS['civil_equivalent__istartswith'] = find


    def _set_enumerable_param(param, model_property=None):
        model_property = model_property or param
        value = form[param] or 'all'
        if value=='all':
            pass
        elif value=='none':
            FILTER_PARAMS[model_property + '__isnull'] = True
        elif value.isdigit():
            FILTER_PARAMS[model_property] = int(value)
        else:
            PARSING_ERRORS.append(param)

    # Автор статьи
    _set_enumerable_param('author', 'editor')

    # Статус статьи
    _set_enumerable_param('status')

    # Часть речи
    _set_enumerable_param('pos', 'part_of_speech')

    # Род
    _set_enumerable_param('gender')

    # Число
    _set_enumerable_param('tantum')

    # Тип имени собственного
    _set_enumerable_param('onym')

    # Каноническое имя
    _set_enumerable_param('canonical_name')

    # Притяжательность
    _set_enumerable_param('possessive')

    # Омонимы
    if form['homonym']:
        FILTER_PARAMS['homonym_order__isnull'] = False

    # Есть примечание
    if form['additional_info']:
        FILTER_EXCLUDE_PARAMS['additional_info'] = ''

    # Есть этимологии
    if form['etymology']:
        etyms = Etymology.objects.values_list('entry')
        FILTER_PARAMS['id__in'] = [item[0] for item in set(etyms)]

    # Статьи-дубликаты
    if form['duplicate']:
        FILTER_PARAMS['duplicate'] = True

    # Неизменяемое
    if form['uninflected']:
        FILTER_PARAMS['uninflected'] = True

    if PARSING_ERRORS:
        raise NameError('Недопустимые значения параметров: %s' % PARSING_ERRORS)

    entries = entries.filter(**FILTER_PARAMS)
    entries = entries.exclude(**FILTER_EXCLUDE_PARAMS)
    entries = entries.order_by(*SORT_PARAMS)

    return entries
