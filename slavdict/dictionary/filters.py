import re

from django.db.models import Count
from django.db.models import Q

from slavdict.custom_user.models import CustomUser
from slavdict.dictionary.forms import GREQSORTBASE_CHOICES
from slavdict.dictionary.forms import SORTBASE_CHOICES
from slavdict.dictionary.forms import SORTDIR_CHOICES
from slavdict.dictionary.models import CollocationGroup
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Etymology
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import MeaningContext

valid_greqsortbase_values = [c[0] for c in GREQSORTBASE_CHOICES]
valid_sortbase_values = [c[0] for c in SORTBASE_CHOICES]
valid_sortdir_values = [c[0] for c in SORTDIR_CHOICES]

def get_entries(form, for_hellinists):
    if for_hellinists:
        default_data = form.default_data_for_hellinists
    else:
        default_data = form.default_data
    form = form.cleaned_data
    entries = Entry.objects
    FILTER_PARAMS = {}
    FILTER_EXCLUDE_PARAMS = {}
    SORT_PARAMS = []
    PARSING_ERRORS = []

    # Сортировка
    sortdir = form.get('sortdir')
    if sortdir not in valid_sortdir_values:
        sortdir = default_data['sortdir']
    sortbase = form.get('sortbase')
    if sortbase not in valid_sortbase_values:
        sortbase = default_data['sortbase']
    sort = sortdir + sortbase
    VALID_SORT_PARAMS = {
        '+alph': ('civil_equivalent', 'homonym_order'),
        '-alph': ('-civil_equivalent', '-homonym_order'),
        '+t': ('mtime', 'id'),
        '-t': ('-mtime', '-id'),
        }
    if sort in VALID_SORT_PARAMS:
        SORT_PARAMS = VALID_SORT_PARAMS[sort]
    else:
        PARSING_ERRORS.append('sort')

    # Статьи начинаются с
    find = form.get('find')
    if find:
        FILTER_PARAMS['civil_equivalent__istartswith'] = find

    # Автор статьи
    value = form.get('author') or 'all'
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
                or none_value == "DOESNT_HAVE"), 'Неверное значение параметра'

        model_property = model_property or param
        value = form.get(param) or 'all'
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
    if form.get('homonym'):
        FILTER_PARAMS['homonym_order__isnull'] = False

    # Есть примечание
    if form.get('additional_info'):
        FILTER_EXCLUDE_PARAMS['additional_info'] = ''

    # Есть этимологии
    if form.get('etymology'):
        etyms = Etymology.objects.values_list('entry')
        FILTER_PARAMS['id__in'] = set(item[0] for item in set(etyms))

    # Без этимологии
    if form.get('etymology_sans'):
        etyms = Etymology.objects.values_list('entry')
        FILTER_EXCLUDE_PARAMS['id__in'] = set(item[0] for item in set(etyms))

    # Есть орфографические и т.п. варианты
    if form.get('variants'):
        entries = entries.annotate(orthvar_num=Count('orthographic_variants'))
        FILTER_PARAMS['orthvar_num__gt'] = 1

    # Статьи с словосочетаниями
    if form.get('collocations'):
        good_entries = set(cg.host_entry.id for cg in CollocationGroup.objects.all() if cg and cg.host_entry)
        if 'id__in' in FILTER_PARAMS:
            FILTER_PARAMS['id__in'] = \
                    FILTER_PARAMS['id__in'].intersection(good_entries)
        else:
            FILTER_PARAMS['id__in'] = good_entries

    # Статьи с контекстами значений
    if form.get('meaningcontexts'):
        good_entries = set(mc.host_entry.id
                           for mc in MeaningContext.objects.all()
                           if mc.show_in_dictionary)
        if 'id__in' in FILTER_PARAMS:
            FILTER_PARAMS['id__in'] = \
                    FILTER_PARAMS['id__in'].intersection(good_entries)
        else:
            FILTER_PARAMS['id__in'] = good_entries

    # Статьи-дубликаты
    if form.get('duplicate'):
        FILTER_PARAMS['duplicate'] = True

    # Неизменяемое
    if form.get('uninflected'):
        FILTER_PARAMS['uninflected'] = True

    assert not PARSING_ERRORS, 'Недопустимые значения параметров: %s' % PARSING_ERRORS

    entries = entries.filter(**FILTER_PARAMS)
    entries = entries.exclude(**FILTER_EXCLUDE_PARAMS)
    entries = entries.order_by(*SORT_PARAMS)

    return entries


def get_examples(form):
    default_data = form.default_data
    form = form.cleaned_data
    examples = Example.objects
    entries = None
    FILTER_PARAMS = {}
    FILTER_EXCLUDE_PARAMS = {'meaning_id__isnull': True}
    SORT_PARAMS = []
    PARSING_ERRORS = []

    # Сортировка
    sortdir = form.get('hwSortdir')
    if sortdir not in valid_sortdir_values:
        sortdir = default_data['hwSortdir']
    sortbase = form.get('hwSortbase')
    if sortbase not in valid_greqsortbase_values:
        sortbase = default_data['hwSortbase']
    sort = sortdir + sortbase
    VALID_SORT_PARAMS = {
        '+addr': ('address_text', 'id'),
        '-addr': ('-address_text', '-id'),
        }
    if sort in VALID_SORT_PARAMS:
        SORT_PARAMS = VALID_SORT_PARAMS[sort]
    else:
        PARSING_ERRORS.append('sort')

    # Автор статьи
    value = form.get('hwAuthor') or 'all'
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
    prfx = form.get('hwPrfx')
    if prfx:
        entries = Entry.objects if entries is None else entries
        entries = entries.filter(civil_equivalent__istartswith=prfx)

    # Адреса начинаются на
    address = form.get('hwAddress')
    if address:
        FILTER_PARAMS['address_text__istartswith'] = address

    # Текст иллюстраций
    example = form.get('hwExample')
    if example:
        RE = re.compile('[^абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+')
        example = ''.join(re.split(RE, example.lower()))
        FILTER_PARAMS['ts_example__contains'] = example

    # Статус греческих параллелей
    greq_status = form.get('hwStatus') or 'L'
    if greq_status == 'all':
        pass
    elif greq_status.isalpha() and len(greq_status) == 1:
        FILTER_PARAMS['greek_eq_status'] = greq_status
    else:
        PARSING_ERRORS.append('hwStatus')

    assert not PARSING_ERRORS, 'Недопустимые значения параметров: %s' % PARSING_ERRORS

    # slavdict.dictionary.models.Entry.status
    #good_statuses = [
    #        'g', # поиск греч.
    #        'f', # завершена
    #        'e', # редактируется
    #        'a', # утверждена
    #        ]
    bad_statuses = [
            'c', # создана
            'w', # в работе
            ]
    # Если не стоит специально галочки, примеры не должны попадать к грецисту,
    # когда статья имеет статус "создана" или "в работе", за исключением тех
    # случаев когда у примера выставлен статус греческих параллелей "необходимы
    # для определения значения" (M) или "срочное" (U).
    if not form.get('hwAllExamples') and greq_status not in ('M', 'U'):
        entries = Entry.objects if entries is None else entries
        entries = entries.exclude(status__in=bad_statuses)

    if entries is not None:
        if entries.exists():
            entries_ids = [_ for _ in entries.values_list('id', flat=True)]
            examples = examples.filter(entry_id__in=entries_ids)
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
    examples = examples.exclude(**FILTER_EXCLUDE_PARAMS)
    examples = examples.order_by(*SORT_PARAMS)

    return examples
