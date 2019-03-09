# -*- coding: utf-8 -*-
import base64
import collections
import datetime
import hashlib
import itertools
import operator
import random
import re
import StringIO
import urllib

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from slavdict import unicode_csv
from slavdict.custom_user.models import CustomUser
from slavdict.dictionary import filters
from slavdict.dictionary import models
from slavdict.dictionary import viewmodels
from slavdict.dictionary.forms import BilletImportForm
from slavdict.dictionary.forms import FilterEntriesForm
from slavdict.dictionary.forms import FilterExamplesForm
from slavdict.dictionary.models import civilrus_convert
from slavdict.dictionary.models import CollocationGroup
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import GreekEquivalentForExample
from slavdict.dictionary.models import Meaning
from slavdict.dictionary.models import MSC5
from slavdict.dictionary.models import MSC11
from slavdict.dictionary.models import MSC12
from slavdict.dictionary.models import OrthographicVariant
from slavdict.dictionary.models import resolve_titles
from slavdict.middleware import InvalidCookieError



# Вспомогательная функция
# для сортировки списка словарных статей.
def entry_key(entry):
    return u'%s %s' % ( entry.civil_equivalent.lower(), entry.homonym_order )

paginator_re = re.compile(r'(\d+)[,;:](\d+)')


@login_required
def materials(request):
    template = 'materials.html'
    context = {
        'title': u'Материалы',
        'user': request.user,
    }
    return render(request, template, context)


@login_required
def all_entries(request, is_paged=False):
    if not request.GET:
        text = u'''
Отображение статей как бы для печати. Для фильтрации статей используйте
параметры адреса данной страницы, например:

    %s?authors=Калужнина&startswith=В

Данный запрос найдет все статьи Калужниной, начинающиеся с буквы «В».


Допустимые параметры
====================

?authors=Петрова,Корнилаева     Статьи соответствующих авторов. Для статей без
                                авторства используйте сочетание "без автора",
                                для авторских статей — фамилию автора.

?startswith=Ав                  Отображать только статьи, начинающиеся
                                на «Ав» без учета регистра символов.

?duplicates                     Отображать только статьи-дубликаты.

?aliud-greek                    Статьи, где есть примеры с пометой
                                "в греч. иначе".

?goodness                       Отображать только "хорошие" статьи.

?hide-ai                        При отображении статей не показывать рабочие
                                примечания-комментарии.

?show-ai                        При отображении статей обязательно показывать
                                рабочие примечания-комментарии.

?hide-numbers                   Не нумеровать статьи.

?list=1324,3345,22              Отображать только статьи с указанными
                                числовыми идентификаторами.

?status=в работе,поиск греч.    Отображать только статьи с перечиленными
?status=-создана                значениями поля "статус статьи". При постановке
                                перед наименованием статуса знака минус статьи
                                с данным статусом будут исключены из выборки.

?hide-refentries                Не отображать отсылочные статьи.

?per-page=100                   Отображать по столько-то статей на странице,
                                по умолчанию, все.


        ''' % request.path
        response = HttpResponse(text, content_type="text/plain; charset=utf-8")
        return response

    httpGET_AUTHORS = urllib.unquote(request.GET.get('authors', ''))
    httpGET_ALIUD_GREEK = 'aliud-greek' in request.GET
    httpGET_DUPLICATES = 'duplicates' in request.GET
    httpGET_GOODNESS = request.GET.get('goodness')
    httpGET_HIDEAI = 'hide-ai' in request.GET
    httpGET_HIDENUMBERS = 'hide-numbers' in request.GET
    httpGET_LIST = request.GET.get('list')
    httpGET_PERPAGE = request.GET.get('per-page')
    httpGET_SHOWAI = 'show-ai' in request.GET
    httpGET_STARTSWITH = request.GET.get('startswith')
    httpGET_STATUS = urllib.unquote(request.GET.get('status', ''))
    httpGET_HIDEREFENTRIES = 'hide-refentries' in request.GET

    COMMA = re.compile(ur'\s*\,\s*')
    SPACE = re.compile(ur'\s+')
    entries = Entry.objects.all()

    if httpGET_AUTHORS:
        httpGET_AUTHORS = [a.strip() for a in COMMA.split(httpGET_AUTHORS)]
        httpGET_AUTHORS = [SPACE.sub(u' ', a) for a in httpGET_AUTHORS]
        httpGET_AUTHORS = [a[:1].upper() + a[1:].lower() for a in httpGET_AUTHORS]
        query = Q(authors__last_name__in=httpGET_AUTHORS)
        if u'Без автора' in httpGET_AUTHORS:
            query = query | Q(authors__isnull=True)
        entries = entries.filter(query)

    if httpGET_STARTSWITH:
        httpGET_STARTSWITH = httpGET_STARTSWITH.strip()
        entries = entries.filter(
                civil_equivalent__istartswith=httpGET_STARTSWITH)

    if httpGET_STATUS:
        httpGET_STATUS = COMMA.split(httpGET_STATUS)
        httpGET_STATUS = [SPACE.sub(u' ', s.strip()) for s in httpGET_STATUS]
        httpGET_STATUS = [s.lower() for s in httpGET_STATUS]
        statuus = []
        exclude_statuus = []
        for status in httpGET_STATUS:
            for value, label in models.STATUS_CHOICES:
                if status[0] == u'-':
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

    if httpGET_GOODNESS:
        g = httpGET_GOODNESS
        if len(g) == 1:
            entries = entries.filter(good=g)
        else:
            g = g.split(',')
            entries = entries.filter(good__in=g)

    if httpGET_DUPLICATES:
        entries = entries.filter(duplicate=True)

    if httpGET_LIST:
        try:
            httpGET_LIST = [int(i) for i in httpGET_LIST.split(',')]
        except ValueError:
            pass
        else:
            entries = entries.filter(pk__in=httpGET_LIST)

    if httpGET_ALIUD_GREEK:
        greqex = GreekEquivalentForExample.objects.filter(aliud=True)
        entries = list(set(i.host_entry for i in greqex))
        entries.sort(key=lambda entry: entry.civil_equivalent)

    # Формирование заголовка страницы в зависимости от переданных
    # GET-параметров
    if httpGET_DUPLICATES:
        title = u'Статьи-дубликаты'
    else:
        if httpGET_AUTHORS:
            title = u'Статьи авторов %s' % u', '.join(httpGET_AUTHORS)
        else:
            title = u'Все статьи'

    if httpGET_STARTSWITH:
        title += u', начинающиеся на „{0}-“'.format(httpGET_STARTSWITH)

    entries = sorted(entries, key=entry_key)
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
        'show_numbers': not httpGET_HIDENUMBERS,
        'show_refentries': not httpGET_HIDEREFENTRIES,
        'title': title,
        'show_additional_info': show_additional_info,
        'show_duplicates_warning': False if httpGET_DUPLICATES else True,
        'user': request.user,
        'is_paged': is_paged,
        'page': page,
        'params_without_page': urllib.urlencode(
            dict(
                (k, unicode(v).encode('utf-8'))
                for k, v in request.GET.items()
                if k not in  ('page', 'AB')
            )
        ),
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
                       (status for status, name in Example.GREEK_EQ_STATUS)):
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
    title = u'Примеры'
    if httpGET_ADDRESS:
        title += u', с адресом на „{0}...“'.format(httpGET_ADDRESS)

    SORT_REGEX = re.compile(ur'[\s\.\,\;\:\-\(\)\!]+', re.UNICODE)
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
        'params_without_page': urllib.urlencode(
            dict(
                (k, unicode(v).encode('utf-8'))
                for k, v in request.GET.items()
                if k not in  ('page', 'AB')
            )
        ),
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

            csvfile = request.FILES['csvfile']
            csv_reader = unicode_csv.UnicodeReader(csvfile,
                    dialect=unicode_csv.calc, encoding='utf-8')

            output = StringIO.StringIO()
            csv_writer = unicode_csv.UnicodeWriter(output,
                    dialect=unicode_csv.calc, encoding='utf-8')

            # Первую строку, -- в ней обязаны быть заголовки, --
            # упреждающе записываем в возможный файл возврата конфликтующих
            # csv-записей.
            csv_writer.writerow(csv_reader.next())

            # Список списков, каждый из которых содержит один элемент.
            idems = OrthographicVariant.objects.all().values_list('idem')

            # Переходим от списка списков к списку самих элементов
            # (орфографических вариантов).
            idems = [x[0] for x in idems]

            # Оформляем орф.варианты в виде множества, а не списка
            idems = set(idems)

            authors = CustomUser.objects.all()

            orthvar_collisions = False
            csv_authors = {u'': None}

            # Регулярное выражение для отыскания любой черты (прямой, косой,
            # обратной косой), обрамленной любым количеством пробельного
            # материала.
            bar = re.compile(r"\s*[/\|\\]\s*", re.MULTILINE | re.UNICODE)

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
                                raise NameError(u"""Автор, указанный
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
                        'homonym_gloss': homonym_gloss or u'',
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
                        raise NameError(u"""Поддержка GET-параметра 'force'
                                со значением 'update' ещё не реализована.""")
                        # Вытягиваем из базы все словарные статьи, у которых
                        # встречаются хотя бы один из орф.вариантов Если их
                        # больше одной, выплёвываем строку таблицы в csv-файл.
                        # Если нет, то заменяем запрос для АнтКонка, дополняем
                        # доп.инфо через "||". Для каждого орф.варианта если
                        # он уже существует обновляем флаги реконструкции
                        # и надежности. Если нет, добавляем его полностью.
                    else:
                        raise NameError(u"""Поддержка GET-параметра 'force'
                          со значением '{0}' не реализована.""".format(force))

            if 'force' not in request.GET and orthvar_collisions:
                response = HttpResponse(output.getvalue(), content_type="text/csv")
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

    get_parameters = '?' + urllib.urlencode(request.GET)
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
    cookie_salt = hashlib.md5(request.path + request.user.username).hexdigest()
    cookie_name = 'find{0}'.format(cookie_salt)
    if cookie_name in request.COOKIES:
        request.COOKIES[cookie_name] = base64 \
            .standard_b64decode(request.COOKIES[cookie_name]) \
            .decode('utf8')

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
        data.update((key[:-len(cookie_salt)], value)
                for key, value in request.COOKIES.items()
                if key.endswith(cookie_salt) and value)
        if (request.method == 'POST' and len(request.POST) == 1
        and 'hdrSearch' in request.POST):
            data['find'] = request.POST['hdrSearch']

    form = FilterEntriesForm(data)
    if not form.is_valid():
        message = u'Форма FilterEntriesForm заполнена неправильно.'
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
            },
        'entries': page.object_list,
        'number_of_entries': paginator.count,
        'form': form,
        'page': page,
        'user': request.user,
        'title': u'Словарь церковнославянского языка Нового времени',
        'MAX_LENGTHS': models.MAX_LENGTHS,
        'statusList': models.Example.GREEK_EQ_STATUS,
        'MEANING_INDICATOR': MEANING_INDICATOR,
        'URGENT_INDICATOR': URGENT_INDICATOR,
    })
    if for_hellinists:
        context['hellinist_workbench'] = True
        context['indicators'] = {
            URGENT_INDICATOR: Example.objects.filter(
                meaning__isnull=False,
                greek_eq_status=Example.GREEK_EQ_URGENT).count(),
            MEANING_INDICATOR: Example.objects.filter(
                meaning__isnull=False,
                greek_eq_status=Example.GREEK_EQ_MEANING).count(),
        }

    response = render(request, template, context)
    if request.method == 'POST':
        form.cleaned_data['find'] = base64 \
            .standard_b64encode(form.cleaned_data['find'].encode('utf8'))
        for param, value in form.cleaned_data.items():
            cookie_name = param + cookie_salt
            response.set_cookie(cookie_name, value, path=request.path)
    return response

@login_required
def hellinist_workbench(request, per_page=4):
    cookie_salt = hashlib.md5(request.path + request.user.username).hexdigest()
    for key in ('hwPrfx', 'hwAddress', 'hwExample'):
        key = key + cookie_salt
        if key in request.COOKIES:
            request.COOKIES[key] = base64 \
                .standard_b64decode(request.COOKIES[key]) \
                .decode('utf8')

    if request.method == 'POST':
        data = request.POST
    else:
        data = FilterExamplesForm.default_data.copy()
        if MEANING_INDICATOR in request.GET:
            data['hwStatus'] = Example.GREEK_EQ_MEANING
        elif URGENT_INDICATOR in request.GET:
            data['hwStatus'] = Example.GREEK_EQ_URGENT
        else:
            data.update((key[:-len(cookie_salt)], value)
                         for key, value in request.COOKIES.items()
                         if key.endswith(cookie_salt) and value)

    form = FilterExamplesForm(data)
    if not form.is_valid():
        message = u'Форма FilterExamplesForm заполнена неправильно.'
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

    context = {
        'examples': page.object_list,
        'form': form,
        'jsonExamples': viewmodels._json(vM_examples),
        'number_of_examples': paginator.count,
        'indicators': {
            URGENT_INDICATOR: Example.objects.filter(
                meaning__isnull=False,
                greek_eq_status=Example.GREEK_EQ_URGENT).count(),
            MEANING_INDICATOR: Example.objects.filter(
                meaning__isnull=False,
                greek_eq_status=Example.GREEK_EQ_MEANING).count(),
            },
        'page': page,
        'statusList': models.Example.GREEK_EQ_STATUS,
        'title': u'Греческий кабинет',
        'viewmodel': {
            'authors': viewmodels.jsonAuthors,
            'statuses': viewmodels.jsonGreqStatuses,
            'sortdir': viewmodels.jsonSortdir,
            'sortbase': viewmodels.jsonGreqSortbase,
            },
        'MAX_LENGTHS': models.MAX_LENGTHS,
        'MEANING_INDICATOR': MEANING_INDICATOR,
        'URGENT_INDICATOR': URGENT_INDICATOR,
        }
    response = render(request, 'hellinist_workbench.html', context)
    if request.method == 'POST':
        for key in ('hwPrfx', 'hwAddress', 'hwExample'):
            form.cleaned_data[key] = base64.standard_b64encode(
                                        form.cleaned_data[key].encode('utf8'))
        for param, value in form.cleaned_data.items():
            param = param + cookie_salt
            response.set_cookie(param, value, path=request.path)
    return response


@login_required
def antconc2ucs8_converter(request):
    random.seed()
    examples = (
        u"Дрꙋ'гъ дрꙋ'га тѧготы^ носи'те, и та'кѡ испо'лните зако'нъ хрСто'въ.",

        u"Ѿ дне'й же іѡа'нна крСти'телѧ досе'лѣ, црСтвіе нбСное нꙋ'дитсѧ, "
        u"и нꙋ'ждницы восхища'ютъ є`",

        u"Пре'жде же всѣ'хъ дрꙋ'гъ ко дрꙋ'гꙋ любо'вь прилѣ'жнꙋ имѣ'йте: "
        u"зане` любо'вь покрыва'етъ мно'жество грѣхѡ'въ. "
        u"Страннолю'бцы дрꙋ'гъ ко дрꙋ'гꙋ, безЪ ропта'ній.",

        u"Наказꙋ'ѧ наказа' мѧ гдСь, сме'рти же не предаде' мѧ",

        u"Вни'дите ѹ'зкими враты`, ꙗ'кѡ простра'ннаѧ врата`, и широ'кій "
        u"пꙋ'ть вводѧ'й въ па'гꙋбꙋ, и мно'зи сꙋ'ть входѧ'щіи и'мъ. Что` "
        u"ѹ'зкаѧ врата`, и тѣ'сный пꙋ'ть вводѧ'й въ живо'тъ, и ма'лѡ и'хъ "
        u"є'сть, и`же ѡбрѣта'ютъ єго`",

        u"Бꙋ'дите ѹ'бѡ вы` соверше'ни, ꙗ'коже ѻц~ъ ва'шъ нбСный "
        u"соверше'нъ є'сть.",

        u"Возведо'хъ ѻ'чи мои` въ го'ры, ѿню'дꙋже пріи'детъ по'мощь моѧ`",
    )
    context = {
        'title': u'Конвертър',
        'user': request.user,
        'convertee': random.choice(examples),
    }
    return render(request, 'converter.html', context)


@login_required
@never_cache
def edit_entry(request, id):
    entry = get_object_or_404(Entry, id=id)
    user = request.user
    user_groups = [t[0] for t in user.groups.values_list('name')]

    prepareCond = not entry.preplock or user.has_key_for_preplock
    authorlessCond = not entry.authors.exists()
    authorCond = user in entry.authors.all()
    editorCond = user.is_admeditor
    if prepareCond and (authorlessCond or authorCond or editorCond):
        pass
    else:
        return redirect(entry.get_absolute_url())

    choices = {
        'author': viewmodels.editAuthors,
        'entry_status': viewmodels.editStatuses,
        'gender': viewmodels.editGenders,
        'onym': viewmodels.editOnyms,
        'part_of_speech': viewmodels._choices(
                            models.PART_OF_SPEECH_CHOICES),
        'participle_type': viewmodels.editParticiples,
        'substantivus_type': viewmodels.editSubstantivusTypes,
        'tantum': viewmodels.editTantum,
    }
    labels = {
        'author': dict(viewmodels.AUTHOR_CHOICES),  # sic! viewmodels
        'entry_status': dict(models.STATUS_CHOICES),
        'gender': dict(models.GENDER_CHOICES),
        'onym': dict(models.ONYM_CHOICES),
        'part_of_speech': dict(models.PART_OF_SPEECH_CHOICES),
        'participle_type': dict(models.PARTICIPLE_CHOICES),
        'substantivus_type': dict(models.SUBSTANTIVUS_TYPE_CHOICES),
        'tantum': dict(models.TANTUM_CHOICES)
    }
    slugs = {
        'onym': models.ONYM_MAP,
        'part_of_speech': models.PART_OF_SPEECH_MAP,
    }
    context = {
        'title': entry.civil_equivalent,
        'user': user,
        'entry': viewmodels.entry_json(id),
        'antconc_query': entry.antconc_query,
        'choices': viewmodels._json(choices),
        'labels': viewmodels._json(labels),
        'slugs': viewmodels._json(slugs),
        'entryURL': entry.get_absolute_url(),
        'PARTS_OF_SPEECH': models.PART_OF_SPEECH_CHOICES,
        'GENDERS': models.GENDER_CHOICES,
        'STATUSES': models.STATUS_CHOICES,
        'GREEK_EQ_STATUSES': models.Example.GREEK_EQ_STATUS,
        'SUBSTANTIVUS_TYPES': models.SUBSTANTIVUS_TYPE_CHOICES,
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
            raise NameError(u'В параллельном процессе отсылки дампа базы '
                            u'возникла непредвиденная ошибка.')
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
    VOLUME = 2

    def uri_qs(uri, **kwargs):
        qs = u'&'.join(u'{0}={1}'.format(k, v) for k, v in kwargs.items())
        return u'{0}?{1}'.format(uri, qs)

    if uri == 'all_collocations':
        uri = uri_qs(cgURI, volume=VOLUME)

    elif uri == 'collocs_same_meaning':
        meanings = reduce(operator.add,
                [list(cg.meanings) for cg in CollocationGroup.objects.all()])
        child_meanings = reduce(operator.add,
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
                          volume=VOLUME)
                  )
                  for key, values in same.items()
                  if len(values) > 1]
        groups.sort()
        context = {
            'name': u'Словосочетания с одинаковыми значениями',
            'groups': groups,
            'user': request.user,
        }
        return render(request, 'useful_urls2.html', context)

    elif uri == 'collocs_without_meanings':
        cgs = (cg for cg in CollocationGroup.objects.all()
                  if len(cg.all_meanings) == 0)
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
        same = same.items()
        same = ((key, value) for key, value in same if len(value) > 1)
        same = ((key, value) for key, value in same
                if len(value) > len(set(cg.host_entry for cg in value)))
        groups = [(key, uri_qs(cgURI,
                               id__in=','.join(str(cg.id) for cg in value),
                               volume=VOLUME
                               ))
                  for key, value in same]
        groups.sort()
        context = {
            'name': u'Одинаковые словосочетания в одной статье',
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
        same = same.items()
        same = ((key, value) for key, value in same if len(value) > 1)
        same = ((key, value) for key, value in same
                if len(set(cg.host_entry for cg in value)) > 1)
        groups = [(key, uri_qs(cgURI,
                               id__in=','.join(str(cg.id) for cg in value),
                               volume=VOLUME
                               ))
                  for key, value in same]
        groups.sort()
        context = {
            'name': u'Одинаковые словосочетания в разных статьях',
            'groups': groups,
            'user': request.user,
        }
        return render(request, 'useful_urls2.html', context)

    elif uri == 'collocs_varforms':
        cgs = []
        for cg in CollocationGroup.objects.all():
            cs = [c.collocation.lower() for c in cg.collocations]
            words = [civilrus_convert(resolve_titles(x)) for c in cs
                       for x in re.split(ur'[\s/\\,;\(\)\[\]]+', c)]
            if any(value > 1
                   for key, value in collections.Counter(words).items()):
                cgs.append(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'collocs_2b':
        cgs = (cg
               for cg in CollocationGroup.objects.all()
                 for c in cg.collocations
               if [x.startswith(u'б')
                   for x in re.split(ur'[\s/\\,;\(\)\[\]]+', c.collocation.lower())
                   ].count(True) > 1)
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
        for cg in CollocationGroup.objects.all():
            m = cg.base_meaning
            e = cg.base_entry
            empty_meaning = m and not m.meaning.strip() and not m.gloss.strip()
            no_meanings = not m and e and not list(e.meanings) + list(e.metaph_meanings)
            several_ABwords = any(
                len([True
                     for x in re.split(ur'[\s/,;\(\)]+', c.civil_equivalent)
                     if x.startswith((u'а', u'А', u'б', u'Б'))]) > 1
                for c in cg.collocations)
            if (empty_meaning or no_meanings) and several_ABwords:
                cgs.add(cg)
        uri = uri_qs(cgURI, id__in=','.join(str(cg.id) for cg in cgs),
                     volume=VOLUME)

    elif uri == 'all_meanings':
        uri = uri_qs(mURI, volume=VOLUME)

    elif uri == 'meanings_literal':
        mark = u'букв.'
        ms = (m for m in Meaning.objects.all() if m.not_hidden() and
                (mark in m.meaning or mark in m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_pl':
        mark = u'мн.'
        ms = (m for m in Meaning.objects.all() if m.not_hidden() and
                (m.special_case == MSC11
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
        regex = re.compile(ur'в\s+роли\s',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search(m.meaning + m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_ps':
        regex = re.compile(ur'в\s+роли\s',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all() if m.not_hidden() and
                (m.substantivus
                 or m.special_case in (MSC5, MSC12)
                 or regex.search(m.meaning + m.gloss)
                 )
              )
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_verbs_noun':
        regex = re.compile(ur'в\s+роли\s+сущ',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden()
                and (m.substantivus
                    or m.special_case in (MSC5, MSC12)
                    or regex.search(m.meaning + m.gloss))
                and m.host_entry.is_part_of_speech('verb')
              )
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_ps2':
        regex = re.compile(ur'в\s+знач',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search(m.meaning + m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_vvodn':
        regex = re.compile(ur'вводн',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search(m.meaning + m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_direct_speech':
        regex = re.compile(ur'с\s+пр(?:ям)\.\s*речью',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search(m.meaning + m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_sobstv':
        regex = re.compile(
                ur'им[^\s\.]*\.?\s*собст|собст[^\s\.]*\.?\s*им)',
                flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search(m.meaning + m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'meanings_quest':
        regex = re.compile(ur'[?!]',
                           flags=re.MULTILINE | re.IGNORECASE | re.UNICODE)
        ms = (m for m in Meaning.objects.all()
                if m.not_hidden() and regex.search(m.meaning + m.gloss))
        uri = uri_qs(mURI, id__in=','.join(str(m.id) for m in ms),
                     volume=VOLUME)

    elif uri == 'headwords_titles':
        es = []
        r = re.compile(ur'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
            # NOTE: ЪЬ намеренно исключены. Нужны любые титла, но не паерки.
        for e in Entry.objects.all():
            if r.search(e.orth_vars.first().idem):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'headwords_symbols':
        es = []
        r = re.compile(ur'[^=~\'`\^'
                       ur'абвгдеєжзѕийіклмноѻпрстѹуꙋфхѿцчшщѣьыъюꙗѡѽѧѯѱѳѵ'
                       ur'АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУꙊФХѾЦЧШЩѢЬЫЪЮꙖѠѼѦѮѰѲѴ]')
        for e in Entry.objects.all():
            if r.search(e.orth_vars.first().idem):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_without_accents':
        es = []
        r1 = re.compile(ur"['`\^]")
        r2 = re.compile(ur'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
            # NOTE: ЪЬ намеренно исключены. Нужны любые титла, но не паерки.
        for e in Entry.objects.all():
            if any(not r1.search(o.idem) and not r2.search(o.idem)
                   for o in e.orth_vars.all()):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_titles':
        es = []
        r = re.compile(ur'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
            # NOTE: ЪЬ намеренно исключены. Нужны любые титла, но не паерки.
        for e in Entry.objects.all():
            if any(r.search(o.idem) for o in e.orth_vars.all()):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_paerok':
        es = []
        r = re.compile(ur'[ЪЬ]')
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
        pattern = ur"^[Вв][оѻѡѽ]"
        r1 = re.compile(pattern + u'з')
        r2 = re.compile(pattern + u'с')
        for e in Entry.objects.all():
            if (any(r1.search(o.idem) for o in e.orth_vars.all())
                    and any(r2.search(o.idem) for o in e.orth_vars.all())):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'orthvars_ln':
        es = []
        pattern1 = ur"{0}[ъЪ]?{1}"
        pattern2 = ur"{0}ь{1}"
        patterns = [(u'л', i)
                    for i in itertools.chain(u'бвгджмнстхцчшщ',
                                       [u'[зѕ]', u'[кѯ]', u'[пѱ]', u'[фѳ]'])]
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
            if any(form.strip() and not form.strip().startswith(u'-')
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
            forms = (e.genitive, e.sg1, e.sg2, e.short_form, e.nom_sg)
            if any(form.strip() and r.search(form) for form in forms):
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'entries_all_figurative':
        es = []
        for e in Entry.objects.all():
            FIG = u'перен.'
            all_figurative = all(
                m.figurative or FIG in m.meaning or FIG in m.gloss
                for m in e.meanings)
            if all_figurative:
                es.append(e)
        uri = uri_qs(eURI, id__in=','.join(str(e.id) for e in es),
                     volume=VOLUME)

    elif uri == 'entries_without_examples':
        es = []
        for e in Entry.objects.all():
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
        r = re.compile(ur'\s*[,;:]\s*|\s+\=?и\s+')
        entries = []
        for e in Entry.objects.all():
            forms = list(itertools.chain(*[r.split(ov.idem)
                                           for ov in e.orth_vars.all()]))
            for form in (e.genitive, e.sg1, e.sg2, e.nom_sg, e.short_form):
                form = form.strip()
                if form:
                    forms.extend(r.split(form))
            forms.extend(itertools.chain(*[r.split(p.idem)
                                           for p in e.participles]))
            forms = filter(lambda x: x.strip() and not x.startswith(u'-'),
                           forms)
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

    return HttpResponseRedirect(uri)


@login_required
@never_cache
def useful_urls(request, x=None, y=None):
    urls = (
            (u'Формы слова', (
                    (u'Все заглавные слова с титлами', 'headwords_titles'),
                    (u'Все заглавные слова с чужеродными символами', 'headwords_symbols'),
                    (u'Все заглавные слова, где реконструкция вызывает сомнения', 'orthvars_questionable'),
                    (u'Орф. варианты без ударений', 'orthvars_without_accents'),
                    (u'Орф. варианты под титлом', 'orthvars_titles'),
                    (u'Орф. варианты с паерком', 'orthvars_paerok'),
                    (u'Формы без ударений', 'forms_without_accents'),
                    (u'Несколько форм в одном поле', 'multiple_forms'),
                    (u'Варианты с воз-/вос-', 'orthvars_vos_voz'),
                    (u'Варианты с льн/лн, льм/лм и т.п.', 'orthvars_ln'),
                )),
            (u'Статьи', (
                    (u'Статьи без примеров', 'entries_without_examples'),
                    (u'Cтатьи дубликаты', 'duplicate_entries'),
                    (u'Cтатьи, где все значения "перен."', 'entries_all_figurative'),
                    (u'Cтатьи с литургическими символами', 'entries_litsym'),
                )),
            (u'Словосочетания (cc)', (
                    (u'Все сс', 'all_collocations'),
                    (u'Фразеологизмы', 'phraseological_collocs'),
                    (u'Cc из одного слова', 'collocs_oneword'),
                    (u'Cc без значений', 'collocs_without_meanings'),
                    (u'Сс с одинаковыми значениями', 'collocs_same_meaning'),
                    (u'Сс – литургические символы', 'collocs_litsym'),
                    (u'Сс в роли сущ.', 'collocs_noun'),
                    (u'Одинаковые сс в одной статье', 'same_collocs_same_entry'),
                    (u'Одинаковые сс в разных статьях', 'same_collocs_diff_entry'),
                    (u'CC, где 2 слова на Б', 'collocs_2b'),
                    (u'Такие сс, что кроме них в статье ничего нет', 'collocs_uniq'),
                    (u'Такие сс, что кроме них в статье ничего нет '
                     u'и сс содержит несколько слов на А или Б', 'collocs_uniqab'),
                    (u'Такие сс, где есть варьирующие формы (отслеживается '
                     u'наличие нескольких слов с совпадающими первыми двумя '
                     u'буквами)', 'collocs_varforms'),
                )),
            (u'Значения и употребления', (
                    (u'Все значения и употребления', 'all_meanings'),
                    (u'С пометой "букв."', 'meanings_literal'),
                    (u'С пометой "мн."', 'meanings_pl'),
                    (u'С пометой или текстом "в роли .."', 'meanings_ps'),
                    (u'C пометой или текстом "в роли сущ." только у глаголов',
                      'meanings_verbs_noun'),
                    (u'С текстом "в роли .."', 'meanings_ps_text'),
                    (u'С текстом "в знач...."', 'meanings_ps2'),
                    (u'С текстом "вводн"', 'meanings_vvodn'),
                    (u'С текстом "с прям. речью"', 'meanings_direct_speech'),
                    (u'С текстом "[?!]"', 'meanings_quest'),
                    (u'С текстом "с именем собств."', 'meanings_sobstv'),
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
    }
    return render(request, 'useful_urls.html', context)
