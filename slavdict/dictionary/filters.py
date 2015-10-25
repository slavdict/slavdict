# -*- coding: utf-8 -*-
import re

from django.db.models import Count
from django.db.models import Q

from slavdict.custom_user.models import CustomUser
from slavdict.dictionary.models import CollocationGroup
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Etymology
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import MeaningContext

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

    # Автор статьи
    value = form['author'] or 'all'
    if value=='all':
        pass
    elif value=='none':
        FILTER_PARAMS['authors__isnull'] = True
    elif value=='few':
        entries = entries.annotate(Count('authors'))
        FILTER_PARAMS['authors__count__gt'] = 1
    elif value.isdigit():
        author = CustomUser.objects.get(pk=int(value))
        entries = author.entry_set.all()
    else:
        PARSING_ERRORS.append('author')


    def _set_enumerable_param(param, none_value, model_property=None):
        """ none_value := "NULL" | "EMPTY_STRING" | "DOESNT_HAVE"
        определяет имеется ли среди значений UI-виджета значение 'none'
        и, если да, то соответствует ли ему в базе пустая строка или NULL.
        """
        assert (none_value == "NULL" or none_value == "EMPTY_STRING"
                or none_value == "DOESNT_HAVE"), u'Неверное значение параметра'

        model_property = model_property or param
        value = form[param] or 'all'
        if value=='all':
            pass
        elif value=='none':
            if none_value=='NULL':
                FILTER_PARAMS[model_property + '__isnull'] = True
            else:
                FILTER_PARAMS[model_property] = ''
        elif value.isdigit():
            FILTER_PARAMS[model_property] = int(value)
        elif len(value) == 1 and value.isalpha():
            FILTER_PARAMS[model_property] = value
        else:
            PARSING_ERRORS.append(param)

    # Статус статьи
    _set_enumerable_param('status', none_value='DOESNT_HAVE')

    # Часть речи
    _set_enumerable_param('pos', none_value='EMPTY_STRING',
                           model_property='part_of_speech')

    # Род
    _set_enumerable_param('gender', none_value='EMPTY_STRING')

    # Число
    _set_enumerable_param('tantum', none_value='EMPTY_STRING')

    # Тип имени собственного
    _set_enumerable_param('onym', none_value='EMPTY_STRING')

    # Каноническое имя
    _set_enumerable_param('canonical_name', none_value='DOESNT_HAVE')

    # Притяжательность
    _set_enumerable_param('possessive', none_value='DOESNT_HAVE')

    # Омонимы
    if form['homonym']:
        FILTER_PARAMS['homonym_order__isnull'] = False

    # Есть примечание
    if form['additional_info']:
        FILTER_EXCLUDE_PARAMS['additional_info'] = ''

    # Есть этимологии
    if form['etymology']:
        etyms = Etymology.objects.values_list('entry')
        FILTER_PARAMS['id__in'] = set(item[0] for item in set(etyms))

    # Есть орфографические и т.п. варианты
    if form['variants']:
        entries = entries.annotate(orthvar_num=Count('orthographic_variants'))
        FILTER_PARAMS['orthvar_num__gt'] = 1

    # Статьи с словосочетаниями
    if form['collocations']:
        good_entries = set(cg.host_entry.id for cg in CollocationGroup.objects.all() if cg and cg.host_entry)
        if 'id__in' in FILTER_PARAMS:
            FILTER_PARAMS['id__in'] = \
                    FILTER_PARAMS['id__in'].intersection(good_entries)
        else:
            FILTER_PARAMS['id__in'] = good_entries

    # Статьи с контекстами значений
    if form['meaningcontexts']:
        good_entries = set(cg.host_entry.id for cg in MeaningContext.objects.all())
        if 'id__in' in FILTER_PARAMS:
            FILTER_PARAMS['id__in'] = \
                    FILTER_PARAMS['id__in'].intersection(good_entries)
        else:
            FILTER_PARAMS['id__in'] = good_entries

    # Статьи-дубликаты
    if form['duplicate']:
        FILTER_PARAMS['duplicate'] = True

    # Неизменяемое
    if form['uninflected']:
        FILTER_PARAMS['uninflected'] = True

    assert not PARSING_ERRORS, u'Недопустимые значения параметров: %s' % PARSING_ERRORS

    entries = entries.filter(**FILTER_PARAMS)
    entries = entries.exclude(**FILTER_EXCLUDE_PARAMS)
    entries = entries.order_by(*SORT_PARAMS)

    return entries


def get_examples(form):
    examples = Example.objects
    entries = None
    FILTER_PARAMS = {}
    SORT_PARAMS = []
    PARSING_ERRORS = []

    # Сортировка
    DEFAULT_SORT = 'addr'
    sortdir = form['hwSortdir']
    sortbase = form['hwSortbase']
    sort = sortdir + sortbase
    if not sort:
        sort = form['hwSort'] or DEFAULT_SORT
    VALID_SORT_PARAMS = {
        'id': ('id',),
        '-id': ('-id',),
        'addr': ('address_text', 'id'),
        '-addr': ('-address_text', '-id'),
        'txt': ('ts_example', 'id'),
        '-txt': ('-ts_example', '-id'),
        }
    if sort in VALID_SORT_PARAMS:
        SORT_PARAMS = VALID_SORT_PARAMS[sort]
    else:
        PARSING_ERRORS.append('sort')

    # Автор статьи
    value = form['hwAuthor'] or 'all'
    if value == 'all':
        pass
    elif value == 'none':
        entries = Entry.objects.filter(authors__isnull=True)
    elif value.isdigit():
        author = CustomUser.objects.get(pk=int(value))
        entries = author.entry_set.all()
    else:
        PARSING_ERRORS.append('hwAuthor')

    # Статьи начинаются с
    prfx = form['hwPrfx']
    if prfx:
        entries = Entry.objects if entries is None else entries
        entries = entries.filter(civil_equivalent__istartswith=prfx)

    # Адреса начинаются на
    address = form['hwAddress']
    if address:
        FILTER_PARAMS['address_text__istartswith'] = address

    # Текст иллюстраций
    example = form['hwExample']
    if example:
        RE = re.compile(u'[^абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+')
        example = u''.join(re.split(RE, example.lower()))
        FILTER_PARAMS['ts_example__contains'] = example

    # Статус греческих параллелей
    greq_status = form['hwStatus'] or 'L'
    if greq_status == 'all':
        pass
    elif greq_status.isalpha() and len(greq_status) == 1:
        FILTER_PARAMS['greek_eq_status'] = greq_status
    else:
        PARSING_ERRORS.append('hwStatus')

    assert not PARSING_ERRORS, u'Недопустимые значения параметров: %s' % PARSING_ERRORS

    # slavdict.dictionary.models.Entry.status
    good_statuses = [
            'g', # поиск греч.
            'f', # завершена
            'e', # редактируется
            'a', # утверждена
            ]
    bad_statuses = [
            'c', # создана
            'w', # в работе
            ]
    # Примеры не должны попадать к грецисту, если статья имеет статус "создана" или
    # "в работе", за исключением тех случаев когда у примера выставлен
    # статус греческих параллелей "необходимы для определения значения" (M)
    # или "срочное" (U).
    if greq_status not in (u'M', u'U'):
        entries = Entry.objects if entries is None else entries
        entries = entries.exclude(status__in=bad_statuses)

    if entries is not None:
        if entries.exists():
            examples = examples.filter(
                Q(meaning__entry_container__in=entries) |
                Q(meaning__parent_meaning__entry_container__in=entries) |
                Q(meaning__collogroup_container__base_meaning__entry_container__in=entries)
                )
        else:
            examples = examples.none()

    examples_ids = form.get('hwExamplesIds')
    if examples_ids:
        examples_ids = re.compile(r'[\s,]+').split(examples_ids)
        # Когда примеры раздавались для проверки в напечатанном виде, перед
        # каждым примером указывался составной номер вида ``N-ID``. N -- номер
        # примера по порядку в распечатанном списке, ID -- идентификатор
        # примера в базе данных. Если пользователь указывает в фильтре
        # составные номера, то нам необходимо учесть только идентификаторы,
        examples_ids = [eid.split('-')[-1] for eid in examples_ids]
        examples_ids = [int(eid) for eid in examples_ids if eid.isdigit()]
        if examples_ids:
            # Если переданы идентификаторы примеров, все оставльные параметры
            # фильтров обнуляем.
            FILTER_PARAMS.clear()
            FILTER_PARAMS['id__in'] = examples_ids

    examples = examples.filter(**FILTER_PARAMS)
    examples = examples.order_by(*SORT_PARAMS)

    return examples
