import csv
import base64
import collections
import datetime
import functools
import hashlib
import io
import itertools
import operator
import random
import re
import urllib.error
import urllib.parse
import urllib.request

import markdown

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

import slavdict.csv
from slavdict.custom_user.models import CustomUser
from slavdict.dictionary import constants
from slavdict.dictionary import filters
from slavdict.dictionary import models
from slavdict.dictionary import viewmodels
from slavdict.dictionary.forms import BilletImportForm
from slavdict.dictionary.forms import FilterEntriesForm
from slavdict.dictionary.forms import FilterExamplesForm
from slavdict.dictionary.models import CollocationGroup
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Etymology
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import GreekEquivalentForExample
from slavdict.dictionary.models import Meaning
from slavdict.dictionary.models import OrthographicVariant
from slavdict.dictionary.models import TempEdit
from slavdict.dictionary.utils import civilrus_convert
from slavdict.dictionary.utils import levenshtein_distance
from slavdict.dictionary.utils import resolve_titles
from slavdict.middleware import InvalidCookieError


# Вспомогательная функция
# для сортировки списка словарных статей.
def entry_key(entry):
    return entry.civil_equivalent.lower(), entry.homonym_order or 0

def entry_key_inversed(entry):
    return entry.civil_equivalent.lower()[::-1], entry.homonym_order or 0

def params_without_page(GET):
    excluded_GET_params = ('page', 'AB')
    params = dict((param, str(value).encode('utf-8'))
                  for param, value in GET.items()
                  if param not in excluded_GET_params)
    return urllib.parse.urlencode(params)

def update_data_from_cookies(COOKIES, cookie_salt, data):
    for key, value in COOKIES.items():
        if key.endswith(cookie_salt) and value:
            key = key[:-len(cookie_salt)]
            value = value.encode('utf-8')
            value = base64.standard_b64decode(value)
            value = str(value, encoding='utf-8')
            data[key] = value

def set_cookie_from_data(response, request, cookie_salt, form):
    for param, value in list(form.cleaned_data.items()):
        cookie_name = param + cookie_salt
        value = str(value).encode('utf-8')
        value = base64.standard_b64encode(value)
        value = str(value, encoding='utf-8')
        response.set_cookie(cookie_name, value, path=request.path)
    return response

def pos_group_entry_key(entry):
    civil, homonym = entry_key(entry)
    if entry.part_of_speech in constants.PART_OF_SPEECH_ORDER:
        pos = constants.PART_OF_SPEECH_ORDER.index(entry.part_of_speech)
    else:
        pos = constants.ALWAYS_LAST_POS
    return pos, civil, homonym

def pos_group_entry_key_inversed(entry):
    civil, homonym = entry_key_inversed(entry)
    if entry.part_of_speech in constants.PART_OF_SPEECH_ORDER:
        pos = constants.PART_OF_SPEECH_ORDER.index(entry.part_of_speech)
    else:
        pos = constants.ALWAYS_LAST_POS
    return pos, civil, homonym

paginator_re = re.compile(r'(\d+)[,;:](\d+)')


@login_required
def materials(request):
    template = 'materials.html'
    context = {
        'title': 'Материалы',
        'user': request.user,
    }
    return render(request, template, context)


@login_required
def all_entries(request, is_paged=False):
    if not request.GET:
        text = '''
<style>
body {
    font-family: 'PT Sans', Arial, sans;
    max-width: 42em;
    margin: 1em auto;
}
.nobr { white-space: nowrap; }
code { color: green; }
th, td {
  padding: 0 1em 1em 0;
  vertical-align: baseline;
}
</style>

Отображение статей как бы для печати. Для фильтрации статей используйте
параметры адреса данной страницы, например:

    %s?authors=Калужнина&startswith=В

Данный запрос найдет все статьи Калужниной, начинающиеся с буквы «В».


| Допустимые параметры | Описание |
| :--- | :--- |
| `?aliud-greek` | Статьи, где есть примеры с пометой "в греч. иначе". |
| `?authors=Петрова,Корнилаева` | Статьи соответствующих авторов. Для статей без авторства используйте сочетание "без автора", для авторских статей — фамилию автора. |
| `?cgs-vs-entries` | Вместо статей отображать заглавное слово и список всех его *словосочетаний* с одним значением при каждом словосочетании. |
| `?duplicates` | статьи-дубликаты. |
| `?hide-ai` | При отображении статей не показывать рабочие примечания-комментарии. |
| `?hide-authors` | Скрывать авторство. |
| `?hide-examples` | Скрывать примеры в статьях. |
| `?hide-meanings` | Скрывать значения при статьях, отображая только заголовки. |
| `?hide-numbers` | Не нумеровать статьи. |
| `?hide-refentries` | Не отображать отсылочные статьи. |
| `?inverse` | Упорядочить статьи по обратному гражданскому написанию заглавного слова. Например, слово "вняти" будет отсортировано, как если бы это было слово "итянв". |
| `?list=1324,3345,22` | Отображать только статьи с указанными числовыми идентификаторами. |
| `?mcsl-vs-entries` | Вместо статей отображать заглавное слово и список всех значений, употреблений и пояснений, где встречается цсл текст в двойных решетках (например, `название десятой буквы церковнославянской азбуки ##=и##`). |
| `?mforms-vs-entries` | Вместо статей отображать заглавное слово и список всех его *преложно-падежных форм*, расставленных при значениях. |
| `?not-editable` | При отображении статей не влючать возможность их изменения прямо на странице. |
| `?per-page=100` | Отображать по столько-то статей на странице, по умолчанию, все. |
| `?pos-group` | Не только сортировать по алфавиту, но и группировать по частям речи. |
| `?print-layout=columns` | Способ отображения статей при отправке страницы на печать. Возможные значения: proofreading и columns. Значение proofreading используется по умолчанию, распечатываемый текст на печати отображается в одну колонку с увеличенным интерлиньяжем. При значении columns текст будет отображаться с обычным интерлиньяжем и в две колонки. |
| `?show-ai` | При отображении статей обязательно показывать рабочие примечания-комментарии. |
| `?show-sort-keys` | При отображении статей обязательно показывать ключи сортировки. Может быть полезно для вывода обратного словника. Ключи будут отображаться в отдельном столбце с выключкой влево для обычных ключей и вправо для инверсных. |
| `?startswith=Ав` | Отображать только статьи, начинающиеся на «Ав» без учета регистра символов. |
| <span class="nobr">`?status=в работе,поиск греч.`</span><br>`?status=-создана` | Отображать только статьи с перечиленными значениями поля "статус статьи". При постановке перед наименованием статуса знака минус статьи с данным статусом будут исключены из выборки. |
| `?volume=3` | Отображать только статьи из такого-то тома. `volume=0` отобразит статьи, не включенные ни в один том, `volume=all` — во всех томах, но не вне томов. |

        ''' % request.path
        html = markdown.markdown(text, extensions=['tables']).encode('utf-8')
        response = HttpResponse(html, content_type='text/html; charset=utf-8')
        return response

    PRINTLAYOUT_PROOFREADING = 'proofreading'
    PRINTLAYOUT_COLUMNS = 'columns'
    DEFAULT_PRINTLAYOUT = PRINTLAYOUT_PROOFREADING

    httpGET_ALIUD_GREEK = 'aliud-greek' in request.GET
    httpGET_AUTHORS = urllib.parse.unquote(request.GET.get('authors', ''))
    httpGET_CGSVSENTRIES = 'cgs-vs-entries' in request.GET
    httpGET_DUPLICATES = 'duplicates' in request.GET
    httpGET_HIDEAI = 'hide-ai' in request.GET
    httpGET_HIDEAUTHORS = 'hide-authors' in request.GET
    httpGET_HIDEEXAMPLES = 'hide-examples' in request.GET
    httpGET_HIDEMEANINGS = 'hide-meanings' in request.GET
    httpGET_HIDENUMBERS = 'hide-numbers' in request.GET
    httpGET_HIDEREFENTRIES = 'hide-refentries' in request.GET
    httpGET_INVERSE = 'inverse' in request.GET
    httpGET_LIST = request.GET.get('list')
    httpGET_MCSLVSENTRIES = 'mcsl-vs-entries' in request.GET
    httpGET_MFORMSVSENTRIES = 'mforms-vs-entries' in request.GET
    httpGET_NOT_EDITABLE = 'not-editable' in request.GET
    httpGET_PERPAGE = request.GET.get('per-page')
    httpGET_POS_GROUP = 'pos-group' in request.GET
    httpGET_PRINTLAYOUT = request.GET.get('print-layout', DEFAULT_PRINTLAYOUT)
    httpGET_SHOWAI = 'show-ai' in request.GET
    httpGET_SHOWSORTKEYS = 'show-sort-keys' in request.GET
    httpGET_STARTSWITH = request.GET.get('startswith')
    httpGET_STATUS = urllib.parse.unquote(request.GET.get('status', ''))
    httpGET_VOLUME = request.GET.get('volume')

    COMMA = re.compile(r'\s*\,\s*')
    SPACE = re.compile(r'\s+')
    entries = Entry.objects.exclude(volume__lt=1)

    if httpGET_AUTHORS:
        httpGET_AUTHORS = [a.strip() for a in COMMA.split(httpGET_AUTHORS)]
        httpGET_AUTHORS = [SPACE.sub(' ', a) for a in httpGET_AUTHORS]
        httpGET_AUTHORS = [a[:1].upper() + a[1:].lower() for a in httpGET_AUTHORS]
        query = Q(authors__last_name__in=httpGET_AUTHORS)
        if 'Без автора' in httpGET_AUTHORS:
            query = query | Q(authors__isnull=True)
        entries = entries.filter(query)

    if httpGET_STARTSWITH:
        httpGET_STARTSWITH = httpGET_STARTSWITH.strip().lower()
        entries = entries.filter(
                civil_equivalent__istartswith=httpGET_STARTSWITH)

    if httpGET_STATUS:
        httpGET_STATUS = COMMA.split(httpGET_STATUS)
        httpGET_STATUS = [SPACE.sub(' ', s.strip()) for s in httpGET_STATUS]
        httpGET_STATUS = [s.lower() for s in httpGET_STATUS]
        statuus = []
        exclude_statuus = []
        for status in httpGET_STATUS:
            for value, label in constants.STATUS_CHOICES:
                if status[0] == '-':
                    status = status[1:]
                    lst = exclude_statuus
                else:
                    lst = statuus
                if label.startswith(status):
                    lst.append(value)
        if exclude_statuus:
            entries = entries.exclude(status__in=exclude_statuus)
        if statuus:
            entries = entries.filter(status__in=statuus)

    if httpGET_DUPLICATES:
        entries = entries.filter(duplicate=True)

    if httpGET_LIST:
        try:
            httpGET_LIST = [int(i) for i in httpGET_LIST.split(',')]
        except ValueError:
            pass
        else:
            entries = entries.filter(pk__in=httpGET_LIST)

    if httpGET_VOLUME is not None:
        if httpGET_VOLUME == 'all':
            entries = entries.filter(volume__gt=0)
        elif httpGET_VOLUME.isdigit():
            entries = entries.filter(volume=int(httpGET_VOLUME))
        else:
            entries = entries.none()

    if httpGET_ALIUD_GREEK:
        greqex = GreekEquivalentForExample.objects.filter(aliud=True)
        entries = list(set(i.host_entry for i in greqex))
        entries.sort(key=lambda entry: entry.civil_equivalent)

    # Формирование заголовка страницы в зависимости от переданных
    # GET-параметров
    if httpGET_DUPLICATES:
        title = 'Статьи-дубликаты'
    else:
        if httpGET_AUTHORS:
            title = 'Статьи авторов %s' % ', '.join(httpGET_AUTHORS)
        else:
            title = 'Все статьи'

    if httpGET_STARTSWITH:
        title += ', начинающиеся на „{0}-“'.format(httpGET_STARTSWITH)

    if httpGET_POS_GROUP:
        if httpGET_INVERSE:
            key = pos_group_entry_key_inversed
        else:
            key = pos_group_entry_key
    else:
        if httpGET_INVERSE:
            key = entry_key_inversed
        else:
            key = entry_key
    entries = sorted(entries, key=key)
    if httpGET_PERPAGE and httpGET_PERPAGE.isdigit():
        per_page=int(httpGET_PERPAGE)
        is_paged = True
    else:
        per_page = 12
    if is_paged:
        paginator = Paginator(entries, per_page=per_page, orphans=2)
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
        try:
            page = paginator.page(pagenum)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        AB = paginator_re.match(request.GET.get('AB', ''))
        if AB:
            A, B = AB.groups()
            page.A = int(A)
            page.B = int(B)
        entries = page.object_list
    else:
        page = None

    show_additional_info = (httpGET_SHOWAI or
            'ai' in request.COOKIES and not httpGET_HIDENUMBERS)
    if httpGET_HIDEAI:
        show_additional_info = False

    context = {
        'entries': entries,
        'cgs_vs_entries': httpGET_CGSVSENTRIES,
        'hide_authors': httpGET_HIDEAUTHORS,
        'hide_examples': httpGET_HIDEEXAMPLES,
        'hide_meanings': httpGET_HIDEMEANINGS,
        'inverse_sort': httpGET_INVERSE,
        'is_paged': is_paged,
        'mforms_vs_entries': httpGET_MFORMSVSENTRIES,
        'mcsl_vs_entries': httpGET_MCSLVSENTRIES,
        'not_editable': httpGET_NOT_EDITABLE,
        'page': page,
        'params_without_page': params_without_page(request.GET),
        'print_layout': httpGET_PRINTLAYOUT,
        'show_additional_info': show_additional_info,
        'show_duplicates_warning': False if httpGET_DUPLICATES else True,
        'show_numbers': not httpGET_HIDENUMBERS,
        'show_refentries': not httpGET_HIDEREFENTRIES,
        'show_sort_keys': httpGET_SHOWSORTKEYS,
        'title': title,
        'user': request.user,
        }
    return render(request, 'all_entries.html', context)


@login_required
def all_examples(request, is_paged=False, mark_as_audited=False,
                                          mark_as_unaudited=False):
    httpGET_ADDRESS = request.GET.get('address')
    httpGET_ADDRESS_REGEX = request.GET.get('address-regex')
    httpGET_ADDRESS_GREP_V = request.GET.get('address-grep-v')
    httpGET_AUDITED = request.GET.get('audited') or ('audited' in request.GET)
    httpGET_EXCLUDE = request.GET.get('exclude')
    httpGET_HIDEAI = 'hide-ai' in request.GET
    httpGET_HIDENUMBERS = 'hide-numbers' in request.GET
    httpGET_INCLUDE_ONLY = request.GET.get('include-only')
    httpGET_SHOWAI = 'show-ai' in request.GET
    httpGET_STATUS = request.GET.get('status')
    httpGET_SUBSET_OF = request.GET.get('subset-of')

    examples = Example.objects.all().order_by('address_text')

    if httpGET_AUDITED:
        if httpGET_AUDITED == '2':
            # Отобразить и "проверенные", и "непроверенные" примеры.
            pass
        else:
            # Отобразить только "проверенные" примеры.
            examples = examples.filter(audited=True)
    else:
        # Отобразить только "НЕпроверенные" примеры.
        examples = examples.filter(audited=False)

    if httpGET_ADDRESS_REGEX:
        examples = examples.filter(address_text__iregex=httpGET_ADDRESS_REGEX)
    elif httpGET_ADDRESS:
        examples = examples.filter(address_text__istartswith=httpGET_ADDRESS)

    if httpGET_ADDRESS_GREP_V:
        examples = examples.exclude(address_text__iregex=httpGET_ADDRESS_GREP_V)

    if (httpGET_STATUS and httpGET_STATUS in
                       (status for status, name in constants.GREEK_EQ_STATUS)):
        examples = examples.filter(greek_eq_status=httpGET_STATUS)

    if httpGET_EXCLUDE:
        excludes = [int(ID)
                    for ID in [i.strip().split('-')[-1]
                               for i in httpGET_EXCLUDE.split(',')]
                    if ID.isdigit()]
        examples = examples.exclude(pk__in=excludes)

    if httpGET_INCLUDE_ONLY:
        includes = [int(ID)
                    for ID in [i.strip().split('-')[-1]
                               for i in httpGET_INCLUDE_ONLY.split(',')]
                    if ID.isdigit()]
        examples = Example.objects.filter(pk__in=includes)

    is_subset = None
    parts = []
    if httpGET_SUBSET_OF:
        superset = set(int(ID)
                       for ID in [i.strip().split('-')[-1]
                                  for i in httpGET_SUBSET_OF.split(',')]
                       if ID.isdigit())
        subset = set(example.id for example in examples)
        is_subset = subset.issubset(superset)

        unionset = sorted(superset.union(subset))
        superset, subset = sorted(superset), sorted(subset)

        cursor = -1
        kind = None  # 'both' or 'superset' or 'subset'
        for i in unionset:
            if i in superset and i in subset:
                if kind == 'both':
                    parts[cursor][1].append(i)
                else:
                    cursor += 1
                    kind = 'both'
                    parts.append((kind, [i]))
            if i in superset and not i in subset:
                if kind == 'superset':
                    parts[cursor][1].append(i)
                else:
                    cursor += 1
                    kind = 'superset'
                    parts.append((kind, [i]))
            if not i in superset and i in subset:
                if kind == 'subset':
                    parts[cursor][1].append(i)
                else:
                    cursor += 1
                    kind = 'subset'
                    parts.append((kind, [i]))


    # Формирование заголовка страницы в зависимости от переданных GET-параметров
    title = 'Примеры'
    if httpGET_ADDRESS:
        title += ', с адресом на „{0}...“'.format(httpGET_ADDRESS)

    SORT_REGEX = re.compile(r'[\s\.\,\;\:\-\(\)\!]+', re.UNICODE)
    def key_emitter(x):
        x = x.address_text.strip().lower()
        parts = SORT_REGEX.split(x)
        parts = [ int(part) if part.isdigit() else part
                  for part in parts ]
        return parts

    examples = sorted(examples, key=key_emitter)
    if is_paged:
        paginator = Paginator(entries, per_page=12, orphans=2)
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
        try:
            page = paginator.page(pagenum)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        AB = paginator_re.match(request.GET.get('AB', ''))
        if AB:
            A, B = AB.groups()
            page.A = int(A)
            page.B = int(B)
        examples = page.object_list
    else:
        page = None

    show_additional_info = (httpGET_SHOWAI or
            'ai' in request.COOKIES and not httpGET_HIDENUMBERS)
    if httpGET_HIDEAI:
        show_additional_info = False

    context = {
        'examples': examples,
        'show_numbers': not httpGET_HIDENUMBERS,
        'title': title,
        'show_additional_info': show_additional_info,
        'is_paged': is_paged,
        'page': page,
        'params_without_page': params_without_page(request.GET),
        'is_subset': is_subset,
        'unionset': parts,
        }

    if mark_as_audited or mark_as_unaudited:
        mark = mark_as_audited #  or not mark_as_unaudited
        for example in examples:
            example.audited = mark
            example.save(without_mtime=True)
        url = '/print/examples/'
        if context['params_without_page']:
            url += '?' + context['params_without_page']
        return redirect(url)

    return render(request, 'all_examples.html', context)


@login_required
def single_entry(request, entry_id, extra_context=None,
                 template='single_entry.html'):
    if not extra_context:
        extra_context = {}
    entry = get_object_or_404(Entry, id=entry_id)
    user = request.user

    if request.path.endswith('intermed/'):
        user_groups = [t[0] for t in user.groups.values_list('name')]
        if (not entry.preplock or user.has_key_for_preplock) \
                and (not entry.authors.exists() or user.is_superuser
                     or 'editors' in user_groups or 'admins' in user_groups
                     or user in entry.authors.all()):
            pass
        else:
            return redirect(entry.get_absolute_url())

    context = {
        'entry': entry,
        'title': entry.civil_equivalent,
        'show_additional_info': 'ai' in request.COOKIES,
        'user': user,
    }
    context.update(extra_context)
    return render(request, template, context)


@login_required
def switch_additional_info(request):
    referer = request.META.get('HTTP_REFERER', '/')
    response = redirect(referer)
    if 'ai' in request.COOKIES:
        response.delete_cookie('ai')
    else:
        date_expired = datetime.datetime.now() + datetime.timedelta(days=90)
        response.set_cookie('ai', max_age=7776000, expires=date_expired)
    return response


@login_required
def import_csv_billet(request):
    # NOTE: Этот метод в общем случае не годится для синхронной загрузки
    # данных из csv-файла в базу, если только импорт не производить маленькими
    # порциями. Иначе запрос может быть прерван веб-сервером по таймауту.
    #
    # Когда необходимо загрузить большую порцию (например, 700 статей на новую
    # букву), то приходится это делать через тестовую базу:
    #
    # 1) Потушить временно боевой сервер и выгрузить последние данные
    #    из боевой базы:
    #
    #    python manage.py dumpdata --all --format=xml --indent=2 >d.xml
    #
    # 2) Обнулить тестовую базу и загрузить в неё данные:
    #
    #    python manage.py flush
    #    python manage.py loaddata -v 3 d.xml
    #
    # 3) Импортировать csv-файл в тестовую базу по адресу /adhoc/csv-import/.
    #    Удостовериться, что импорт прошел успешно. Проверить импортированные
    #    статьи, нет ли чего лишнего. Если что, проделать пункт 2 повторно
    #    и заново загрузить исправленный csv-файл.
    #
    # 4) Если всё в порядке сделать пункт 1 для тестовой базы.
    #
    # 5) Сделать пункт 2 для боевой базы и запустить боевой сервер.

    if request.method == 'POST':
        form = BilletImportForm(request.POST, request.FILES)
        if form.is_valid():

            csvfile = io.TextIOWrapper(request.FILES['csvfile'],
                                       encoding='utf-8')
            csv_reader = csv.reader(csvfile, dialect=slavdict.csv.calc)
            output = io.StringIO()
            csv_writer = csv.writer(output, dialect=slavdict.csv.calc)

            # Первую строку, -- в ней обязаны быть заголовки, --
            # упреждающе записываем в возможный файл возврата конфликтующих
            # csv-записей.
            csv_writer.writerow(next(csv_reader))

            # Список списков, каждый из которых содержит один элемент.
            idems = OrthographicVariant.objects.all().values_list('idem')

            # Переходим от списка списков к списку самих элементов
            # (орфографических вариантов).
            idems = [x[0] for x in idems]

            # Оформляем орф.варианты в виде множества, а не списка
            idems = set(idems)

            authors = CustomUser.objects.all()

            orthvar_collisions = False
            csv_authors = {'': None}

            # Регулярное выражение для отыскания любой черты (прямой, косой,
            # обратной косой), обрамленной любым количеством пробельного
            # материала.
            bar = re.compile(r"\s*[/\|\\]\s*", re.MULTILINE | re.UNICODE)

            with transaction.atomic():
              for row in csv_reader:
                # Столбцы в CSV-файле
                (orthvars_info, civil_equivalent, word_forms_list,
                        antconc_query, author_in_csv, additional_info,
                        homonym_order, homonym_gloss, duplicate) = row

                # Обработка поля с орфографическими вариантами.
                # Орфографические варианты разделяются любой чертой (прямой,
                # косой или обратной косой). Звездочка означает, что
                # орфогр.вариант был реконструирован. Вопросительный знак --
                # сомнения в правильности реконструкции. Черты и знаки могут
                # отделяться друг от друга и от орф.вариантов любым количеством
                # пробельного материала.
                _list = bar.split(orthvars_info)
                orthvars_list = [
                        (
                            i.strip(" \r\n\t*?"),
                            "*" in i,
                            "?" in i
                        )
                        for i in _list
                ]
                orthvars_set = set([i[0] for i in orthvars_list])

                # GET-параметр "force":
                #
                # =add    -- добавить лексему, даже если похожие лексемы
                #            уже есть.
                #
                # =update -- если похожая лексема всего одна, то дополнить
                #            информацию по ней из CSV-файла.
                #
                force = request.GET.get('force', False)
                intersection = idems.intersection(orthvars_set)

                if not force and intersection:
                    orthvar_collisions = True
                    csv_writer.writerow(row)
                else:
                    author_in_csv = author_in_csv.strip().lower()
                    if author_in_csv:
                        if author_in_csv in csv_authors:
                            author = csv_authors[author_in_csv]
                        else:
                            for au in authors:
                                if au.last_name and author_in_csv.startswith(
                                                        au.last_name.lower()):
                                    author = au
                                    csv_authors[author_in_csv] = au
                                    break
                            else:
                                raise NameError("""Автор, указанный
                                        в CSV-файле, не найден среди участников
                                        работы над словарём.""")
                    else:
                        author = None

                    # Если поле с гражданским эквивалентом пусто, то берем
                    # конвертацию в гражданку заглавного слова. Если же это
                    # поле заполнено, то берём его без изменений.
                    if not civil_equivalent.strip():
                        civil_equivalent = civilrus_convert(orthvars_list[0][0])

                    from_csv = {
                        'word_forms_list': word_forms_list,
                        'civil_equivalent': civil_equivalent,
                        'antconc_query': antconc_query,
                        'additional_info': additional_info,
                        'homonym_order': (int(float(homonym_order))
                                          if homonym_order else None),
                        'homonym_gloss': homonym_gloss or '',
                        'duplicate': bool(duplicate),
                    }

                    entry = Entry()
                    if not intersection or (force == 'add'):
                        entry.__dict__.update(from_csv)
                        entry.save()
                        if author is not None:
                            entry.authors.add(author)

                        for i in orthvars_list:
                            orthvar = i[0]
                            ov = OrthographicVariant.objects.create(
                                                entry=entry, idem=orthvar,
                                                reconstructed=(i[2] or i[1]),
                                                questionable=i[2])
                            ov.save()
                            idems.add(orthvar)
                    elif intersection and (force=='update'):
                        raise NameError("""Поддержка GET-параметра 'force'
                                со значением 'update' ещё не реализована.""")
                        # Вытягиваем из базы все словарные статьи, у которых
                        # встречаются хотя бы один из орф.вариантов Если их
                        # больше одной, выплёвываем строку таблицы в csv-файл.
                        # Если нет, то заменяем запрос для АнтКонка, дополняем
                        # доп.инфо через "||". Для каждого орф.варианта если
                        # он уже существует обновляем флаги реконструкции
                        # и надежности. Если нет, добавляем его полностью.
                    else:
                        raise NameError("""Поддержка GET-параметра 'force'
                          со значением '{0}' не реализована.""".format(force))

            if 'force' not in request.GET and orthvar_collisions:
                data = output.getvalue().encode('utf-8')
                response = HttpResponse(data, content_type="text/csv")
                response['Content-Disposition'] = ('attachment; '
                        'filename={:%Y.%m.%d--%H.%M.%S}--not.imported.csv'
                        .format(datetime.datetime.now()))
            else:
                response = HttpResponseRedirect('/')

            output.close()
            csvfile.close()
            return response
    else:
        form = BilletImportForm()

    get_parameters = '?' + urllib.parse.urlencode(request.GET)
    return render(request, 'csv_import.html', {'form': form,
                  'get_parameters': get_parameters})

MEANING_INDICATOR = 'meaning'
URGENT_INDICATOR = 'urgent'

@login_required
def entry_list(request, for_hellinists=False, per_page=12,
        context=None):
    template = 'entry_list.html'
    if for_hellinists:
        template = 'hellinist_workbench.html'
    salt = request.path + request.user.username
    cookie_salt = hashlib.md5(salt.encode('utf-8')).hexdigest()

    if request.method == 'POST' and len(request.POST) > 1:
        # Сам по себе объект QueryDict, на который указывает request.POST,
        # является неизменяемым. Метод ``copy()`` делает его полную уже
        # доступную для изменения копию.
        data = request.POST.copy()
        if request.POST.get('hdrSearch'):
            data['find'] = request.POST['hdrSearch']
    else:
        if for_hellinists:
            data = FilterEntriesForm.default_data_for_hellinists.copy()
        else:
            data = FilterEntriesForm.default_data.copy()
        update_data_from_cookies(request.COOKIES, cookie_salt, data)
        if (request.method == 'POST'
                and len(request.POST) == 1
                and 'hdrSearch' in request.POST):
            data['find'] = request.POST['hdrSearch']

    form = FilterEntriesForm(data)
    if not form.is_valid():
        message = 'Форма FilterEntriesForm заполнена неправильно.'
        if request.method == 'POST':
            raise RuntimeError(message)
        else:
            # Кидаем исключение для обработки в мидлваре и стирания всех кук.
            raise InvalidCookieError(message)

    if for_hellinists and 'id' in request.GET and request.GET['id'].isdigit():
        entries = Entry.objects.filter(pk=int(request.GET['id']))
    else:
        entries = filters.get_entries(form, for_hellinists)

    paginator = Paginator(entries, per_page=per_page, orphans=2)
    if request.method == 'POST':
        pagenum = 1
    else:
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    AB = paginator_re.match(request.GET.get('AB', ''))
    if AB:
        A, B = AB.groups()
        page.A = int(A)
        page.B = int(B)

    if context is None:
        context = dict()
    context.update({
        'viewmodel': {
            'authors': viewmodels.jsonAuthors,
            'canonical_name': viewmodels.jsonCanonicalName,
            'gender': viewmodels.jsonGenders,
            'onym': viewmodels.jsonOnyms,
            'pos': viewmodels.jsonPos,
            'possessive': viewmodels.jsonPossessive,
            'statuses': viewmodels.jsonStatuses,
            'sortdir': viewmodels.jsonSortdir,
            'sortbase': viewmodels.jsonSortbase,
            'tantum': viewmodels.jsonTantum,
            'volumes': viewmodels.jsonVolumes,
            },
        'entries': page.object_list,
        'number_of_entries': paginator.count,
        'form': form,
        'page': page,
        'user': request.user,
        'title': 'Словарь церковнославянского языка Нового времени',
        'MAX_LENGTHS': models.MAX_LENGTHS,
        'statusList': constants.GREEK_EQ_STATUS,
        'MEANING_INDICATOR': MEANING_INDICATOR,
        'URGENT_INDICATOR': URGENT_INDICATOR,
    })
    if for_hellinists:
        context['hellinist_workbench'] = True
        exclude_Q = (
            Q(meaning__isnull=True) | Q(wordform_example=True)
            | Q(hidden=True))
        context['indicators'] = {
            URGENT_INDICATOR: Example.objects.exclude(exclude_Q).filter(
                greek_eq_status=constants.GREEK_EQ_URGENT).count(),
            MEANING_INDICATOR: Example.objects.exclude(exclude_Q).filter(
                greek_eq_status=constants.GREEK_EQ_MEANING).count(),
        }

    response = render(request, template, context)
    if request.method == 'POST':
        response = set_cookie_from_data(response, request, cookie_salt, form)
    return response

@login_required
def hellinist_workbench(request, per_page=4):
    salt = request.path + request.user.username
    cookie_salt = hashlib.md5(salt.encode('utf-8')).hexdigest()

    if request.method == 'POST':
        data = request.POST
    else:
        data = FilterExamplesForm.default_data.copy()
        if MEANING_INDICATOR in request.GET:
            data['hwStatus'] = constants.GREEK_EQ_MEANING
        elif URGENT_INDICATOR in request.GET:
            data['hwStatus'] = constants.GREEK_EQ_URGENT
        else:
            update_data_from_cookies(request.COOKIES, cookie_salt, data)

    form = FilterExamplesForm(data)
    if not form.is_valid():
        message = 'Форма FilterExamplesForm заполнена неправильно.'
        if request.method == 'POST':
            raise RuntimeError(message)
        else:
            # Кидаем исключение для обработки в мидлваре и стирания всех кук.
            raise InvalidCookieError(message)
    examples = filters.get_examples(form)
    #if not request.user.has_key_for_preplock:
    #    examples = [ex for ex in examples if not ex.host_entry.preplock]

    paginator = Paginator(examples, per_page=per_page, orphans=2)
    if request.method == 'POST':
        pagenum = 1
    else:
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    AB = paginator_re.match(request.GET.get('AB', ''))
    if AB:
        A, B = AB.groups()
        page.A = int(A)
        page.B = int(B)

    vM_examples = [e.forHellinistJSON() for e in page.object_list]
    exclude_Q = (
        Q(meaning__isnull=True) | Q(wordform_example=True) | Q(hidden=True))

    context = {
        'examples': page.object_list,
        'form': form,
        'jsonExamples': viewmodels._json(vM_examples),
        'number_of_examples': paginator.count,
        'indicators': {
            URGENT_INDICATOR: Example.objects.exclude(exclude_Q).filter(
                greek_eq_status=constants.GREEK_EQ_URGENT).count(),
            MEANING_INDICATOR: Example.objects.exclude(exclude_Q).filter(
                greek_eq_status=constants.GREEK_EQ_MEANING).count(),
            },
        'page': page,
        'statusList': constants.GREEK_EQ_STATUS,
        'title': 'Греческий кабинет',
        'viewmodel': {
            'authors': viewmodels.jsonAuthors,
            'statuses': viewmodels.jsonGreqStatuses,
            'sortdir': viewmodels.jsonSortdir,
            'sortbase': viewmodels.jsonGreqSortbase,
            'volumes': viewmodels.jsonVolumes,
            },
        'MAX_LENGTHS': models.MAX_LENGTHS,
        'MEANING_INDICATOR': MEANING_INDICATOR,
        'URGENT_INDICATOR': URGENT_INDICATOR,
        }
    response = render(request, 'hellinist_workbench.html', context)
    if request.method == 'POST':
        response = set_cookie_from_data(response, request, cookie_salt, form)
    return response


@login_required
def antconc2ucs8_converter(request):
    random.seed()
    examples = (
        "Дрꙋ'гъ дрꙋ'га тѧготы^ носи'те, и та'кѡ испо'лните зако'нъ хрСто'въ.",

        "Ѿ дне'й же іѡа'нна крСти'телѧ досе'лѣ, црСтвіе нбСное нꙋ'дитсѧ, "
        "и нꙋ'ждницы восхища'ютъ є`",

        "Пре'жде же всѣ'хъ дрꙋ'гъ ко дрꙋ'гꙋ любо'вь прилѣ'жнꙋ имѣ'йте: "
        "зане` любо'вь покрыва'етъ мно'жество грѣхѡ'въ. "
        "Страннолю'бцы дрꙋ'гъ ко дрꙋ'гꙋ, безЪ ропта'ній.",

        "Наказꙋ'ѧ наказа' мѧ гдСь, сме'рти же не предаде' мѧ",

        "Вни'дите ѹ'зкими враты`, ꙗ'кѡ простра'ннаѧ врата`, и широ'кій "
        "пꙋ'ть вводѧ'й въ па'гꙋбꙋ, и мно'зи сꙋ'ть входѧ'щіи и'мъ. Что` "
        "ѹ'зкаѧ врата`, и тѣ'сный пꙋ'ть вводѧ'й въ живо'тъ, и ма'лѡ и'хъ "
        "є'сть, и`же ѡбрѣта'ютъ єго`",

        "Бꙋ'дите ѹ'бѡ вы` соверше'ни, ꙗ'коже ѻц~ъ ва'шъ нбСный "
        "соверше'нъ є'сть.",

        "Возведо'хъ ѻ'чи мои` въ го'ры, ѿню'дꙋже пріи'детъ по'мощь моѧ`",
    )
    context = {
        'title': 'Конвертър',
        'user': request.user,
        'convertee': random.choice(examples),
    }
    return render(request, 'converter.html', context)


@login_required
@never_cache
def edit_entry(request, id):
    entry = get_object_or_404(Entry, id=id)
    user = request.user

    prepareCond = not entry.preplock or user.has_key_for_preplock
    authorlessCond = not entry.authors.exists()
    authorCond = user in entry.authors.all()
    editorCond = user.is_admeditor

    # TODO: schedule stale temp_edit removal
    for temp_edit in TempEdit.objects.filter(
            deadline__lte=datetime.datetime.now()):
        temp_edit.delete()

    tempEditor = TempEdit.objects.filter(
            user=user, entry=entry, deadline__gt=datetime.datetime.now()
            ).exists()

    if (tempEditor or
            prepareCond and (authorlessCond or authorCond or editorCond)):
        pass
    else:
        return redirect(entry.get_absolute_url())

    choices = {
        'author': viewmodels.editAuthors,
        'entry_status': viewmodels.editStatuses,
        'gender': viewmodels.editGenders,
        'onym': viewmodels.editOnyms,
        'participle_type': viewmodels.editParticiples,
        'part_of_speech': viewmodels._choices(constants.PART_OF_SPEECH_CHOICES),
        'substantivus_type': viewmodels.editSubstantivusTypes,
        'tantum': viewmodels.editTantum,
        'translation_source': viewmodels._choices(constants.TRANSLATION_SOURCE_CHOICES),
        'volumes': viewmodels.editVolumes,
    }
    labels = {
        'author': dict(viewmodels.AUTHOR_CHOICES),  # sic! viewmodels
        'entry_status': dict(constants.STATUS_CHOICES),
        'gender': dict(constants.GENDER_CHOICES),
        'onym': dict(constants.ONYM_CHOICES),
        'participle_type': dict(constants.PARTICIPLE_CHOICES),
        'part_of_speech': dict(constants.PART_OF_SPEECH_CHOICES),
        'substantivus_type': dict(constants.SUBSTANTIVUS_TYPE_CHOICES),
        'tantum': dict(constants.TANTUM_CHOICES),
        'translation_source': constants.TRANSLATION_SOURCE_TEXT,
    }
    slugs = {
        'onym': constants.ONYM_MAP,
        'part_of_speech': constants.PART_OF_SPEECH_MAP,
    }
    entry_json = viewmodels._json(entry.get_search_item())
    entry_json_in_attr = entry_json.replace('"', '&#34;')
    tips = dict((tip.ref, tip.html()) for tip in models.Tip.objects.all())
    context = {
        'title': entry.civil_equivalent,
        'user': user,
        'entry_json_in_attr': entry_json_in_attr,
        'entry': viewmodels.entry_json(id),
        'antconc_query': entry.antconc_query,
        'choices': viewmodels._json(choices),
        'labels': viewmodels._json(labels),
        'slugs': viewmodels._json(slugs),
        'tips': viewmodels._json(tips),
        'entryURL': entry.get_absolute_url(),
        'PARTS_OF_SPEECH': constants.PART_OF_SPEECH_CHOICES,
        'GENDERS': constants.GENDER_CHOICES,
        'STATUSES': constants.STATUS_CHOICES,
        'GREEK_EQ_STATUSES': constants.GREEK_EQ_STATUS,
        'SUBSTANTIVUS_TYPES': constants.SUBSTANTIVUS_TYPE_CHOICES,
        'MAX_LENGTHS': models.MAX_LENGTHS,
    }
    return render(request, 'single_entry_edit.html', context)


@login_required
@never_cache
def duplicate_entry(request, id):
    entry = get_object_or_404(Entry, id=id)
    prepareCond = not entry.preplock or request.user.has_key_for_preplock
    editorCond = request.user.is_admeditor
    if prepareCond and editorCond:
        pass
    else:
        return redirect(entry.get_absolute_url())
    entry.save()
    entry, entry_copy = entry.make_double()
    return redirect('all_entries_url')

@login_required
def dump(request):
    import os
    pid = os.fork()
    if not pid:
        # NOTE: Избавляемся от процессов-зомби, создавая дочерний процесс
        # дочернего процесса. См. http://stackoverflow.com/a/16809886
        # Использовать сигналы ``signal.signal(signal.SIGCHLD,
        # signal.SIG_IGN)`` не получается, поскольку данная функция сама будет
        # выполняться джангой не в родительском процессе.
        pid = os.fork()
        if not pid:
            os.execvp('python', ('python', 'url_mail_dumper.py'))
            raise NameError('В параллельном процессе отсылки дампа базы '
                            'возникла непредвиденная ошибка.')
        else:
            os._exit(0)
    else:
        os.wait()
    return  HttpResponseRedirect('/')



def useful_urls_redirect(uri, request):
    base_url = '/admin/dictionary/'
    cgURI = base_url + 'collocationgroup/'
    eURI = base_url + 'entry/'
    mURI = base_url + 'meaning/'
    exURI = base_url + 'example/'
    VOLUME = constants.CURRENT_VOLUME

    def uri_qs(uri, **kwargs):
        if 'id__in' in kwargs and not kwargs['id__in']:
            kwargs['id__in'] = '000'
        qs = '&'.join('{0}={1}'.format(k, v) for k, v in list(kwargs.items()))
        return '{0}?{1}'.format(uri, qs)

    if uri == 'all_collocations':
        uri = uri_qs(cgURI, volume=VOLUME)

    elif uri == 'collocs_same_meaning':
        meanings = functools.reduce(operator.add,
                [list(cg.meanings) for cg in CollocationGroup.objects.all()])
        child_meanings = functools.reduce(operator.add,
                [list(m.child_meanings) for m in meanings])
        meanings = meanings + child_meanings
        same = collections.defaultdict(list)
        for m in meanings:
            meaning = m.meaning.lower().strip()
            if meaning:
                same[meaning].append(m)
            gloss = m.gloss.lower().strip()
            if gloss:
                same[gloss].append(m)
        groups = [(key,
                   uri_qs(cgURI,
                          id__in=','.join(
                            str(cg.id)
                            for cg in set(
                                m.collogroup_container if m.collogroup_container
                                    else m.parent_meaning.collogroup_container
                                for m in values)),
                          volume=VOLUME),
                   tuple(sorted(
                       set(cg.host_entry for cg in value),
                       key=lambda x:x.civil_equivalent
                   ))
                  )
                  for key, values in list(same.items())
                  if len(values) > 1]
        groups.sort()
        context = {
            'name': 'Словосочетания с одинаковыми значениями',
            'groups': groups,
            'user': request.user,
        }
        return render(request, 'useful_urls2.html', context)

    elif uri == 'collocs_without_meanings':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if len(cg.all_meanings) == 0)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_ambivalent':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if len(cg.all_meanings) > 1)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_oneword':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if all(not re.search(r'\s', c.collocation.strip())
                         for c in cg.collocations))
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_litsym':
        cgs = (m.host
               for m in Meaning.objects.filter(metaphorical=True)
               if isinstance(m.host, CollocationGroup))
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'entries_litsym':
        eids = set(m.host_entry.id
                   for m in Meaning.objects.filter(metaphorical=True)
                   if isinstance(m.host, CollocationGroup))
        uri = uri_qs(eURI, id__in=','.join(str(eid) for eid in eids),
                     volume=VOLUME)

    elif uri == 'entries_greq':
        eids = set(et.entry_id for et in Etymology.objects.all())
        uri = uri_qs(eURI, id__in=','.join(str(eid) for eid in eids),
                     volume=VOLUME)

    elif uri == 'entries_greq2':
        eids = set(et.entry_id for et in Etymology.objects.all()
                   if re.search(r'\W', unicodedata.normalize('NFC', et.unitext))
        uri = uri_qs(eURI, id__in=','.join(str(eid) for eid in eids),
                     volume=VOLUME)

    elif uri == 'phraseological_collocs':
        uri = uri_qs(cgURI, phraseological__exact=1, volume=VOLUME)

    elif uri == 'collocs_noun':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if (any(m.substantivus for m in cg.meanings) or
                      any(cm.substantivus for m in cg.meanings
                                            for cm in m.child_meanings)))
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'same_collocs_same_entry':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if cg.host_entry.volume(VOLUME))
        cs = (list(cg.collocations) for cg in cgs)
        same = collections.defaultdict(set)
        for collocations in cs:
            for c in collocations:
                collocation = c.civil_equivalent.lower().strip()
                if collocation:
                    same[collocation].add(c.collogroup)
        same = list(same.items())
        same = ((key, value) for key, value in same if len(value) > 1)
        same = ((key, value) for key, value in same
                if len(value) > len(set(cg.host_entry for cg in value)))
        groups = [(key, uri_qs(cgURI,
                               id__in=','.join(str(cg.id) for cg in value),
                               volume=VOLUME
                               ), tuple(sorted(
                                       set(cg.host_entry for cg in value),
                                       key=lambda x:x.civil_equivalent
                                   )))
                  for key, value in same]
        groups.sort()
        context = {
            'name': 'Одинаковые словосочетания в одной статье',
            'groups': groups,
            'user': request.user,
        }
        return render(request, 'useful_urls2.html', context)

    elif uri == 'same_collocs_diff_entry':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if cg.host_entry.volume(VOLUME))
        cs = (list(cg.collocations) for cg in cgs)
        same = collections.defaultdict(set)
        for collocations in cs:
            for c in collocations:
                collocation = c.civil_equivalent.lower().strip()
                if collocation:
                    same[collocation].add(c.collogroup)
        same = list(same.items())
        same = ((key, value) for key, value in same if len(value) > 1)
        same = ((key, value) for key, value in same
                if len(set(cg.host_entry for cg in value)) > 1)
        groups = [(key, uri_qs(cgURI,
                               id__in=','.join(str(cg.id) for cg in value),
                               volume=VOLUME
                               ), tuple(sorted(
                                       set(cg.host_entry for cg in value),
                                       key=lambda x:x.civil_equivalent
                                   )))
                  for key, value in same]
        groups.sort()
        context = {
            'name': 'Одинаковые словосочетания в разных статьях',
            'groups': groups,
            'user': request.user,
        }
        return render(request, 'useful_urls2.html', context)

    elif uri == 'collocs_same_civil':
        cgs = []
        for cg in CollocationGroup.objects.all():
            cs = [c.collocation for c in cg.collocations]
            words = [civilrus_convert(resolve_titles(x)).lower()
                     for c in cs
                       for x in re.split(r'[\s/\\,;\(\)\[\]\.]+', c)]
            words = [word for word in words
                          if not word.startswith('-') and len(word) > 2]
            if any(value > 1
                   for key, value in list(collections.Counter(words).items())):
                cgs.append(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_similar_civil':
        cgs = []
        DISTANCE = 3
        def has_similar_words(words):
            for i, word1 in enumerate(words):
                for word2 in words[i + 1:]:
                    ix = min(len(word1), len(word2)) - DISTANCE
                    if (levenshtein_distance(word1, word2) < DISTANCE + 1
                            and word1[:ix] == word2[:ix]):
                        return True
            return False
        for cg in CollocationGroup.objects.all():
            cs = [c.collocation for c in cg.collocations]
            words = tuple(sorted(set(civilrus_convert(resolve_titles(x)).lower()
                          for c in cs
                              for x in re.split(r'[\s/\\,;\(\)\[\]\.]+', c))))
            words = tuple(word for word in words
                               if not word.startswith('-') and len(word) > 2)
            if has_similar_words(words):
                cgs.append(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_uniq':
        cgs = set()
        for cg in CollocationGroup.objects.all():
            m = cg.base_meaning
            e = cg.base_entry
            empty_meaning = m and not m.meaning.strip() and not m.gloss.strip()
            no_meanings = not m and e and not list(e.meanings) + list(e.metaph_meanings)
            if empty_meaning or no_meanings:
                cgs.add(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_uniqab':
        cgs = set()
        letters = ()
        for i in range(1, constants.CURRENT_VOLUME):
            letters += constants.VOLUME_LETTERS[i]
        letters += tuple(letter.upper() for letter in letters)
        for cg in CollocationGroup.objects.all():
            m = cg.base_meaning
            e = cg.base_entry
            empty_meaning = m and not m.meaning.strip() and not m.gloss.strip()
            no_meanings = not m and e and not list(e.meanings) + list(e.metaph_meanings)
            several_ABwords = any(
                len([True
                     for x in re.split(r'[\s/,;\(\)]+', c.civil_equivalent)
                     if x.startswith(letters)]) > 1
                for c in cg.collocations)
            if (empty_meaning or no_meanings) and several_ABwords:
                cgs.add(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_refs':
        cgs = set()
        regex = re.compile(r'\b(?:cf|qv|[сc][рpм]\.|idem|то\s*же,?\s+что\b)',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        for cg in CollocationGroup.objects.all():
            for m in cg.all_meanings:
                if regex.search('%s %s' % (m.meaning, m.gloss)):
                    cgs.add(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'all_meanings':
        uri = uri_qs(mURI, volume=VOLUME)

    elif uri == 'meanings_without_examples':
        ms = (m for m in Meaning.objects.all() if not m.example_set.count())
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'terminal_meanings_without_examples':
        regex = re.compile(r'\b(?:qv|[сc]м\.|idem|то\s*же,?\s+что\b)',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if 0 == m.example_set.count()
                    and 0 == m.collocationgroup_set.count()
                    and 0 == m.child_meaning_set.filter(parent_meaning=m).count()
                    and not regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_literal':
        mark = 'букв.'
        ms = (m for m in Meaning.objects.all() if m.not_hidden() and
                (mark in m.meaning or mark in m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_qv_cf_idem_marks_non_cgs':
        regex = re.compile(r'\b(?:(?:ср|см)\.|то\s*же,?\s+что\b)',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects
                            .filter(collogroup_container_id__isnull=True)
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_pl':
        mark = 'мн.'
        ms = (m for m in Meaning.objects.all() if m.not_hidden() and
                (m.special_case == constants.MSC11
                 or m.substantivus
                    and m.is_substantivus_type('m.pl.', 'f.pl.', 'n.pl.')
                 or mark in m.meaning
                 or mark in m.gloss
                 or any(mc.show_in_dictionary and
                        mark in (mc.left_text.strip(),
                                 mc.right_text.strip())
                        for mc in m.meaningcontext_set.all()
                        )
                 )
              )
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_ps_text':
        regex = re.compile(r'в\s+роли\s',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_ps':
        regex = re.compile(r'в\s+роли\s',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all() if m.not_hidden() and
                (m.substantivus
                 or m.special_case in constants.MSC_ROLE
                 or regex.search('%s %s' % (m.meaning, m.gloss))
                 )
              )
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_verbs_noun':
        regex = re.compile(r'в\s+роли\s+сущ',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden()
                and (m.substantivus or regex.search('%s %s' % (m.meaning, m.gloss)))
                and m.host_entry.is_part_of_speech('verb')
              )
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_ps2':
        regex = re.compile(r'в\s+знач',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_vvodn':
        regex = re.compile(r'вводн',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_direct_speech':
        regex = re.compile(r'с\s+(?:пр\.|прям\.|прямой)\s*речью',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_sobstv':
        regex = re.compile(
                r'им[^\s\.]*\.?\s*собст|собст[^\s\.]*\.?\s*им',
                flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_quest':
        regex = re.compile(r'[?!]',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search('%s %s' % (m.meaning, m.gloss)))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'headwords_titles':
        es = []
        r = re.compile(r'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
            # NOTE: ЪЬ намеренно исключены. Нужны любые титла, но не паерки.
        for e in Entry.objects.all():
            ov = e.orth_vars.first()
            if ov and r.search(ov.idem):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'headwords_symbols':
        es = []
        r = re.compile(r'[^=~\'`\^'
                       r'абвгдеєжзѕийіклмноѻпрстѹуꙋфхѿцчшщѣьыъюꙗѡѽѧѯѱѳѵ'
                       r'АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУꙊФХѾЦЧШЩѢЬЫЪЮꙖѠѼѦѮѰѲѴ]')
        for e in Entry.objects.all():
            ov = e.orth_vars.first()
            if ov and r.search(ov.idem):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_and':
        es = []
        for e in Entry.objects.all():
            if e.base_vars.count() > 1:
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_without_accents':
        es = []
        r1 = re.compile(r"['`\^]")
        r2 = re.compile(r'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
            # NOTE: ЪЬ намеренно исключены. Нужны любые титла, но не паерки.
        for e in Entry.objects.all():
            if any(not r1.search(o.idem) and not r2.search(o.idem)
                   for o in e.orth_vars.all()):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_titles':
        es = []
        r = re.compile(r'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
            # NOTE: ЪЬ намеренно исключены. Нужны любые титла, но не паерки.
        for e in Entry.objects.all():
            if any(r.search(o.idem) for o in e.orth_vars.all()):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_paerok':
        es = []
        r = re.compile(r'[ЪЬ]')
        for e in Entry.objects.all():
            if any(r.search(o.idem) for o in e.orth_vars.all()):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_questionable':
        es = []
        for e in Entry.objects.all():
            if any(o.questionable for o in e.orth_vars.all()):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_vos_voz':
        es = []
        pattern = r"^[Вв][оѻѡѽ]"
        r1 = re.compile(pattern + 'з')
        r2 = re.compile(pattern + 'с')
        for e in Entry.objects.all():
            if (any(r1.search(o.idem) for o in e.orth_vars.all())
                    and any(r2.search(o.idem) for o in e.orth_vars.all())):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_ln':
        es = []
        pattern1 = r"{0}[ъЪ]?{1}"
        pattern2 = r"{0}ь{1}"
        patterns = [('л', i)
                    for i in itertools.chain('бвгджмнстхцчшщ',
                                       ['[зѕ]', '[кѯ]', '[пѱ]', '[фѳ]'])]
        patterns = [(pattern1.format(*p), pattern2.format(*p))
                    for p in patterns]
        regexps = [(re.compile(p1), re.compile(p2))
                    for p1, p2 in patterns]
        for e in Entry.objects.all():
            orthvars = [ov.idem for ov in e.orth_vars.all()]
            if any(any(r1.search(ov) for ov in orthvars)
                   and any(r2.search(ov) for ov in orthvars)
                   for r1, r2 in regexps):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'forms_without_accents':
        es = []
        r = re.compile(r"['`\^]")
        for e in Entry.objects.all():
            forms = (e.genitive, e.sg1, e.sg2, e.short_form)
            if any(form.strip() and not form.strip().startswith('-')
                   and not r.search(form) for form in forms) \
               or any(p.idem.strip() and not r.search(p.idem)
                      for p in e.participles):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'multiple_forms':
        es = []
        r = re.compile(r"[,;]")
        for e in Entry.objects.all():
            forms = (e.genitive, e.sg1, e.sg2, e.short_form, e.nom_pl)
            if any(form.strip() and r.search(form) for form in forms):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'entries_all_figurative':
        es = []
        for e in Entry.objects.all():
            FIG = 'перен.'
            all_figurative = len(e.meanings) > 0 and all(
                m.figurative or FIG in m.meaning or FIG in m.gloss
                for m in e.meanings)
            if all_figurative:
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'entries_without_examples':
        es = []
        for e in Entry.objects.all():
            if len(e.all_meanings) == 0:
                continue
            meaning_collogroups = (m.collogroups for m in e.all_meanings)
            all_collogroups = itertools.chain(e.collogroups,
                                              *meaning_collogroups)
            collogroup_meanings = (cg.all_meanings for cg in all_collogroups)
            all_meanings = itertools.chain(e.all_meanings, *collogroup_meanings)
            no_example = all(
                not meaning.examples
                    and all(not cm.examples for cm in meaning.child_meanings)
                for meaning in all_meanings)
            if no_example:
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'duplicate_entries':
        es = []
        r = re.compile(r'\s*[,;:]\s*|\s+\=?и\s+')
        entries = []
        for e in Entry.objects.all():
            forms = list(itertools.chain(*[r.split(ov.idem)
                                           for ov in e.orth_vars.all()]))
            for form in (e.genitive, e.sg1, e.sg2, e.nom_pl, e.short_form):
                form = form.strip()
                if form:
                    forms.extend(r.split(form))
            forms.extend(itertools.chain(*[r.split(p.idem)
                                           for p in e.participles]))
            forms = [x for x in forms if x.strip() and not x.startswith('-')]
            record = (e, set(civilrus_convert(f) for f in forms))
            entries.append(record)
        while len(entries) > 1:
            entry1, forms1 = entries.pop()
            indices = []
            for i, (entry2, forms2) in enumerate(entries):
                if (forms1.intersection(forms2)
                        and (not entry1.homonym_order
                             or not entry2.homonym_order)):
                    es.append(entry2)
                    indices.append(i)
            if indices:
                es.append(entry1)
                entries = [e for i, e in enumerate(entries)
                             if i not in indices]
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'ex_aliud_parallel':
        exs = []
        for ex in Example.objects.all():
            if any(ge.aliud and ge.unitext.strip() for ge in ex.greek_equivs):
                exs.append(ex)
        uri = uri_qs(exURI, id__in=','.join(str(ex.id) for ex in exs),
                     volume=VOLUME)

    elif uri == 'ex_brackets_at':
        exs = []
        needles = re.compile(r'[\(\)\[\]\{\}⟨⟩<>@/\\—]')
        for ex in Example.objects.all():
            if needles.search(ex.example):
                exs.append(ex)
        uri = uri_qs(exURI, id__in=','.join(str(ex.id) for ex in exs),
                     volume=VOLUME)

    return HttpResponseRedirect(uri)


@login_required
@never_cache
def useful_urls(request, x=None, y=None):
    VOLUME = constants.CURRENT_VOLUME
    prev_volumes_letters = ()
    for i in range(1, constants.CURRENT_VOLUME):
        prev_volumes_letters += constants.VOLUME_LETTERS[i]
    prev_volumes_letters = tuple(
            letter.upper() for letter in prev_volumes_letters)
    urls = (
            ('Формы слова', (
                    ('Все заглавные слова с титлами (без учета вариантов в скобках)', 'headwords_titles'),
                    ('Все заглавные слова с чужеродными символами', 'headwords_symbols'),
                    ('Все заглавные слова, где реконструкция вызывает сомнения', 'orthvars_questionable'),
                    ('Заглавные слова через "и"', 'orthvars_and'),
                    ('Орф. варианты без ударений', 'orthvars_without_accents'),
                    ('Орф. варианты под титлом', 'orthvars_titles'),
                    ('Орф. варианты с паерком', 'orthvars_paerok'),
                    ('Формы без ударений', 'forms_without_accents'),
                    ('Несколько форм в одном поле', 'multiple_forms'),
                    ('Варианты с воз-/вос-', 'orthvars_vos_voz'),
                    ('Варианты с льн/лн, льм/лм и т.п.', 'orthvars_ln'),
                )),
            ('Статьи', (
                    ('Без примеров', 'entries_without_examples'),
                    ('Дубликаты', 'duplicate_entries'),
                    ('Где все значения "перен."', 'entries_all_figurative'),
                    ('С литургическими символами', 'entries_litsym'),
                    ('С греч. параллелями к статье', 'entries_greq'),
                    ('С греч. параллелями к статье, где две и более формы в поле',
                        'entries_greq2'),
                )),
            ('Словосочетания (cc)', (
                    ('Все', 'all_collocations'),
                    ('Фразеологизмы', 'phraseological_collocs'),
                    ('Из одного слова', 'collocs_oneword'),
                    ('Без значений', 'collocs_without_meanings'),
                    ('С несколькими значениями', 'collocs_ambivalent'),
                    ('С одинаковыми значениями', 'collocs_same_meaning'),
                    ('Литургические символы', 'collocs_litsym'),
                    ('В роли сущ.', 'collocs_noun'),
                    ('Одинаковые в одной статье', 'same_collocs_same_entry'),
                    ('Одинаковые в разных статьях', 'same_collocs_diff_entry'),
                    ('Такие сс, что кроме них в статье ничего нет', 'collocs_uniq'),
                    ('Такие сс, что кроме них в статье ничего нет '
                     'и сс содержит несколько слов на %s' %
                        ', '.join(prev_volumes_letters), 'collocs_uniqab'),
                    ('С полным совпадением гражданского написания вариантов '
                     "(до'ждь нбСный/небе'сный) "
                     "[учитываются слова из 3 и более символов]", 'collocs_same_civil'),
                    ('С частичным совпадением гражданского написания вариантов '
                     "(возложи'ти єпітрахи'ль[//єпітрахи'лій] или "
                     "высота` добродѣ'тели/добродѣ'телей) "
                     "[учитываются слова из 3 и более символов]",
                     'collocs_similar_civil'),
                    ('С отсылками (см.; ср.; то же, что; qv; cf; idem)', 'collocs_refs'),
                )),
            ('Значения и употребления', (
                    ('Все значения и употребления', 'all_meanings'),
                    ('С пометой "букв."', 'meanings_literal'),
                    ('С пометой "мн."', 'meanings_pl'),
                    ('С пометой или текстом "в роли .."', 'meanings_ps'),
                    ('C пометой или текстом "в роли сущ." только у глаголов',
                        'meanings_verbs_noun'),
                    ('С текстом "в роли .."', 'meanings_ps_text'),
                    ('С текстом "в знач...."', 'meanings_ps2'),
                    ('С текстом "вводн"', 'meanings_vvodn'),
                    ('С текстом "с прямой речью"', 'meanings_direct_speech'),
                    ('С текстом "[?!]"', 'meanings_quest'),
                    ('С текстом "с именем собств."', 'meanings_sobstv'),
                    ('Без примеров', 'meanings_without_examples'),
                    ('Без примеров (учитывать только терминальные значения '
                     'без помет "см.", "то же, что" и тэгов "qv" и "idem")',
                        'terminal_meanings_without_examples'),
                    ('С пометами "см.", "ср.", "то же, что" '
                     '(но не тегами qv, cf, idem) не в сс',
                        'meanings_qv_cf_idem_marks_non_cgs'),
                )),
            ('Примеры', (
                    ('в греч. иначе и параллель', 'ex_aliud_parallel'),
                    ('с символами скобок, слешами и @', 'ex_brackets_at'),
                )),
    )
    if x:
        for section, data in urls:
            for name, uri in data:
                if x == uri:
                    return useful_urls_redirect(uri, request)
    context = {
        'urls': urls,
        'user': request.user,
        'volume': VOLUME,
    }
    return render(request, 'useful_urls.html', context)
