# -*- coding: utf-8 -*-
import base64
import datetime
import json
import random
import re
import StringIO
import urllib

from coffin.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext

import dictionary.filters
import dictionary.models
import dictionary.viewmodels
import unicode_csv
from custom_user.models import CustomUser
from dictionary.forms import BilletImportForm
from dictionary.forms import FilterEntriesForm
from dictionary.forms import FilterExamplesForm
from dictionary.models import civilrus_convert
from dictionary.models import Entry
from dictionary.models import Etymology
from dictionary.models import Example
from dictionary.models import GreekEquivalentForExample
from dictionary.models import GreekEquivalentForMeaning
from dictionary.models import Meaning
from dictionary.models import MeaningContext
from dictionary.models import OrthographicVariant
from unicode_csv import UnicodeReader




# Вспомогательная функция
# для сортировки списка словарных статей.
def entry_key(entry):
    return u'%s %s' % ( entry.civil_equivalent.lower(), entry.homonym_order )


@login_required
def all_entries(request, is_paged=False):
    httpGET_AUTHOR = request.GET.get('author')
    httpGET_CORRUPTED_GREEK = 'corrupted-greek' in request.GET
    httpGET_DUPLICATES = 'duplicates' in request.GET
    httpGET_FIND = request.GET.get('find')
    httpGET_GOODNESS = request.GET.get('goodness')
    httpGET_HIDEAI = 'hide-ai' in request.GET
    httpGET_HIDENUMBERS = 'hide-numbers' in request.GET
    httpGET_LIST = request.GET.get('list')
    httpGET_SHOWAI = 'show-ai' in request.GET
    httpGET_STATUS = request.GET.get('status')

    entries = Entry.objects.all()
    if httpGET_FIND:
        query = (
            Q(civil_equivalent__startswith=httpGET_FIND.lower())
            |
            Q(civil_equivalent__startswith=httpGET_FIND.capitalize())
        )
        entries = entries.filter(query)

    if httpGET_AUTHOR:
        if httpGET_AUTHOR == 'is-not-assigned!':
            entries = entries.filter(editor__isnull=True)
        else:
            entries = entries.filter(editor__username=httpGET_AUTHOR)

    if httpGET_STATUS=='-created':
        entries = entries.exclude(
                status=dictionary.models.STATUS_MAP['created'])

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

    if httpGET_CORRUPTED_GREEK:
        greek_etymons = Etymology.objects.filter(
                language=dictionary.models.LANGUAGE_MAP['greek'],
                corrupted=True)
        greqex = GreekEquivalentForExample.objects.filter(corrupted=True)
        greqm = GreekEquivalentForMeaning.objects.filter(corrupted=True)

        # WARNING: Переменная entries теперь будет содержать обычный список
        # вместо объекта django.db.models.query.QuerySet, так что теперь на
        # entries больше нельзя нанизывать никаких фильтров.
        entries = set([i.host_entry for i in greek_etymons])
        entries.update([i.host_entry for i in greqex])
        entries.update([i.host_entry for i in greqm])
        entries = list(entries)
        entries.sort(key=lambda entry: entry.civil_equivalent)

    # Формирование заголовка страницы в зависимости от переданных GET-параметров
    if httpGET_DUPLICATES:
        title = u'Статьи-дубликаты'
    else:
        if httpGET_AUTHOR:
            title = u'Статьи автора „%s“' % CustomUser.objects.get(username=httpGET_AUTHOR)
        else:
            title = u'Все статьи'

    if httpGET_FIND:
        title += u', начинающиеся на „%s-“' % httpGET_FIND

    entries = sorted(entries, key=entry_key)
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
        entries = page.object_list
    else:
        page = None

    show_additional_info = httpGET_SHOWAI or \
        'ai' in request.COOKIES and not httpGET_HIDENUMBERS,
    if httpGET_HIDEAI:
        show_additional_info = False

    context = {
        'entries': entries,
        'show_numbers': not httpGET_HIDENUMBERS,
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
                if k != 'page'
            )
        ),
        }
    return render_to_response('all_entries.html', context, RequestContext(request))


@login_required
def single_entry(request, entry_id, extra_context=None, template='single_entry.html'):
    if not extra_context:
        extra_context = {}
    entry = get_object_or_404(Entry, id=entry_id)
    user = request.user

    if request.path.endswith('intermed/'):
        user_groups = [t[0] for t in user.groups.values_list('name')]
        if not entry.editor or user.is_superuser \
        or 'editors' in user_groups or 'admins' in user_groups \
        or user == entry.editor:
            pass
        else:
            return redirect(entry.get_absolute_url())

    context = {
        'entry': entry,
        'title': u'Статья «%s»' % entry.civil_equivalent,
        'show_additional_info': 'ai' in request.COOKIES,
        'user': user,
    }
    context.update(extra_context)
    return render_to_response(template, context, RequestContext(request))


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

    if request.method == 'POST':
        form = BilletImportForm(request.POST, request.FILES)
        if form.is_valid():

            csvfile = request.FILES['csvfile']
            csv_reader = unicode_csv.UnicodeReader(csvfile, dialect=unicode_csv.calc, encoding='utf-8')

            output = StringIO.StringIO()
            csv_writer = unicode_csv.UnicodeWriter(output, dialect=unicode_csv.calc, encoding='utf-8')

            csv_writer.writerow(csv_reader.next()) # Первую строку, в ней обязаны быть заголовки,
            # упреждающе записываем в возможный файл возврата конфликтующих csv-записей.

            idems = OrthographicVariant.objects.all().values_list('idem') # Список списков, каждый из которых содержит один элемент.
            idems = [x[0] for x in idems] # Переходим от списка списков к списку самих элементов (орфографических вариантов).
            idems = set(idems) # Оформляем орф.варианты в виде множества, а не списка
            authors = CustomUser.objects.all()

            orthvar_collisions = False
            csv_authors = {u'': None}

            # Регулярное выражение для отыскания любой черты (прямой, косой, обратной косой),
            # обрамленной любым количеством пробельного материала.
            bar = re.compile(r"\s*[/\|\\]\s*", re.MULTILINE + re.UNICODE)

            for row in csv_reader:
                # Столбцы в CSV-файле
                orthvars_info, civil_equivalent, word_forms_list, antconc_query, author_in_csv, \
                    additional_info, homonym_order, homonym_gloss, duplicate = row

                # Обработка поля с орфографическими вариантами.
                # Орфографические варианты разделяются любой чертой (прямой, косой или обратной косой).
                # Звездочка означает, что орфогр.вариант был реконструирован. Вопросительный знак --
                # сомнения в правильности реконструкции. Черты и знаки могут отделяться друг от друга
                # и от орф.вариантов любым количеством пробельного материала.
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
                # =add    -- добавить лексему, даже если похожие лексемы уже есть.
                # =update -- если похожая лексема всего одна, то дополнить информацию по ней из CSV-файла.
                force = request.GET.get('force', False)
                intersection = idems.intersection(orthvars_set)

                if not force and intersection:
                    orthvar_collisions = True
                    csv_writer.writerow(row)
                else:
                    author_in_csv = author_in_csv.lower()
                    if author_in_csv in csv_authors:
                        author = csv_authors[author_in_csv]
                    else:
                        for au in authors:
                            if au.last_name and author_in_csv.startswith(au.last_name.lower()):
                                author = au
                                csv_authors[author_in_csv] = au
                                break
                        else:
                            raise NameError(u"Автор, указанный в CSV-файле, не найден среди участников работы над словарём.")

                    # Если поле с гражданским эквивалентом пусто, то берем конвертацию в гражданку заглавного слова.
                    # Если же это поле заполнено, то берём его без изменений. С практической точки зрения это значит,
                    # что в CSV-файле можно не указывать гражданку для слов без титл, они автоматом должны хорошо
                    # преобразовываться. А для слов с титлами или буквотитлами гражданку лучше указывать, чтобы
                    # впоследствии не надо было её уточнять из форм вроде "бл*годетель".
                    if not civil_equivalent.strip():
                        civil_equivalent = civilrus_convert(orthvars_list[0][0])

                    from_csv = {
                        'word_forms_list': word_forms_list,
                        'civil_equivalent': civil_equivalent,
                        'antconc_query': antconc_query,
                        'editor': author,
                        'additional_info': additional_info,
                        'homonym_order': int(float(homonym_order)) if homonym_order else None,
                        'homonym_gloss': homonym_gloss or u'',
                        'duplicate': bool(duplicate),
                    }

                    entry = Entry()
                    if not intersection or (force == 'add'):
                        entry.__dict__.update(from_csv)
                        entry.__dict__.update({
                            'reconstructed_headword': orthvars_list[0][1],
                            'questionable_headword': orthvars_list[0][2],
                            })

                        entry.save()

                        for i in orthvars_list:
                            orthvar = i[0]
                            ov = OrthographicVariant.objects.create(entry=entry, idem=orthvar)
                            ov.save()
                            idems.add(orthvar)
                    elif intersection and (force=='update'):
                        raise NameError(u"Поддержка GET-параметра 'force' со значением 'update' ещё не реализована.")
                        # Вытягиваем из базы все словарные статьи, у которых встречаются хотя бы один из орф.вариантов
                        # Если их больше одной, выплёвываем строку таблицы в csv-файл.
                        # Если нет, то заменяем запрос для АнтКонка, дополняем доп.инфо через "||".
                        # Для каждого орф.варианта если он уже существует обновляем флаги реконструкции и надежности.
                        # Если нет, добавляем его полностью.
                    else:
                        raise NameError(u"Поддержка GET-параметра 'force' со значением '%s' не реализована." % force)

            if 'force' not in request.GET and orthvar_collisions:
                response = HttpResponse(output.getvalue(), mimetype="text/csv")
                response['Content-Disposition'] = 'attachment; filename=%s--not.imported.csv' % \
                    datetime.datetime.strftime(datetime.datetime.now(), format='%Y.%m.%d--%H.%M.%S')
            else:
                response = HttpResponseRedirect('/')

            output.close()
            csvfile.close()
            return response
    else:
        form = BilletImportForm()
    return render_to_response('csv_import.html', {'form': form, 'get_parameters': '?' + urllib.urlencode(request.GET)})


@login_required
def entry_list(request):
    if 'find' in request.COOKIES:
        request.COOKIES['find'] = base64 \
            .standard_b64decode(request.COOKIES['find']) \
            .decode('utf8')

    if request.method == 'POST' and len(request.POST) > 1:
        data = request.POST.copy() # Сам по себе объект QueryDict, на который указывает request.POST,
            # является неизменяемым. Метод ``copy()`` делает его полную уже доступную для изменения
            # копию.
        if request.POST['hdrSearch']:
            data['find'] = request.POST['hdrSearch']
    else:
        data = dict(FilterEntriesForm.default_data)
        data.update(request.COOKIES)
        if request.method == 'POST' and len(request.POST) == 1 and 'hdrSearch' in request.POST:
            data['find'] = request.POST['hdrSearch']

    form = FilterEntriesForm(data)
    assert form.is_valid(), u'Форма заполнена неправильно'
    entries = dictionary.filters.get_entries(form.cleaned_data)

    paginator = Paginator(entries, per_page=12, orphans=2)
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

    context = {
        'viewmodel': {
            'authors': dictionary.viewmodels.jsonAuthors,
            'canonical_name': dictionary.viewmodels.jsonCanonicalName,
            'gender': dictionary.viewmodels.jsonGenders,
            'onym': dictionary.viewmodels.jsonOnyms,
            'pos': dictionary.viewmodels.jsonPos,
            'possessive': dictionary.viewmodels.jsonPossessive,
            'statuses': dictionary.viewmodels.jsonStatuses,
            'sortdir': dictionary.viewmodels.jsonSortdir,
            'sortbase': dictionary.viewmodels.jsonSortbase,
            'tantum': dictionary.viewmodels.jsonTantum,
            },
        'entries': page.object_list,
        'number_of_entries': paginator.count,
        'form': form,
        'page': page,
        'user': request.user,
        }
    response = render_to_response('entry_list.html', context, RequestContext(request))
    if request.method == 'POST':
        form.cleaned_data['find'] = base64 \
            .standard_b64encode(form.cleaned_data['find'].encode('utf8'))
        for param, value in form.cleaned_data.items():
            response.set_cookie(param, value, path=request.path)
    return response


@login_required
def hellinist_workbench(request):
    if 'hwPrfx' in request.COOKIES:
        request.COOKIES['hwPrfx'] = base64 \
            .standard_b64decode(request.COOKIES['hwPrfx']) \
            .decode('utf8')

    if 'hwAddress' in request.COOKIES:
        request.COOKIES['hwAddress'] = base64 \
            .standard_b64decode(request.COOKIES['hwAddress']) \
            .decode('utf8')

    if request.method == 'POST':
        data = request.POST
    else:
        data = FilterExamplesForm.default_data
        data.update(request.COOKIES)

    form = FilterExamplesForm(data)
    assert form.is_valid(), u'Форма FilterExamplesForm заполнена неправильно'
    examples = dictionary.filters.get_examples(form.cleaned_data)

    paginator = Paginator(examples, per_page=4, orphans=2)
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

    vM_examples = [
    {
        'id': e.id,
        'triplet': e.context_ucs,
        'antconc': e.context.strip() or e.example,
        'address': e.address_text,
        'status': e.greek_eq_status,
        'comment': e.additional_info,
        'greqs': [
            {
                'unitext': greq.unitext,
                'text': greq.text,
                'initial_form': greq.initial_form,
                'id': greq.id,
                'additional_info': greq.additional_info
            }
            for greq in e.greek_equivs]
    }
    for e in page.object_list]

    context = {
        'examples': page.object_list,
        'form': form,
        'jsonExamples': dictionary.viewmodels._json(vM_examples),
        'number_of_examples': paginator.count,
        'page': page,
        'statusList': dictionary.models.Example.GREEK_EQ_STATUS,
        'title': u'Греческий кабинет',
        'viewmodel': {
            'authors': dictionary.viewmodels.jsonAuthors,
            'statuses': dictionary.viewmodels.jsonGreqStatuses,
            'sortdir': dictionary.viewmodels.jsonSortdir,
            'sortbase': dictionary.viewmodels.jsonGreqSortbase,
            },
        }
    response = render_to_response('hellinist_workbench.html', context, RequestContext(request))
    if request.method == 'POST':
        form.cleaned_data['hwPrfx'] = base64 \
            .standard_b64encode(form.cleaned_data['hwPrfx'].encode('utf8'))
        form.cleaned_data['hwAddress'] = base64 \
            .standard_b64encode(form.cleaned_data['hwAddress'].encode('utf8'))
        for param, value in form.cleaned_data.items():
            response.set_cookie(param, value, path=request.path)
    return response


@login_required
def antconc2ucs8_converter(request):
    random.seed()
    examples = (
        u"Дрꙋ'гъ дрꙋ'га тѧготы^ носи'те, и та'кѡ испо'лните зако'нъ хрСто'въ.",

        u"Ѿ дне'й же іѡа'нна крСти'телѧ досе'лѣ, црСтвіе нбСное нꙋ'дитсѧ, и нꙋ'ждницы восхища'ютъ є`",

        u"Пре'жде же всѣ'хъ дрꙋ'гъ ко дрꙋ'гꙋ любо'вь прилѣ'жнꙋ имѣ'йте: "
        u"зане` любо'вь покрыва'етъ мно'жество грѣхѡ'въ. "
        u"Страннолю'бцы дрꙋ'гъ ко дрꙋ'гꙋ, безЪ ропта'ній.",

        u"Наказꙋ'ѧ наказа' мѧ гдСь, сме'рти же не предаде' мѧ",

        u"Вни'дите ѹ'зкими враты`, ꙗ'кѡ простра'ннаѧ врата`, и широ'кій пꙋ'ть вводѧ'й въ па'гꙋбꙋ, "
        u"и мно'зи сꙋ'ть входѧ'щіи и'мъ. Что` ѹ'зкаѧ врата`, и тѣ'сный пꙋ'ть вводѧ'й въ живо'тъ, и ма'лѡ "
        u"и'хъ є'сть, и`же ѡбрѣта'ютъ єго`",

        u"Бꙋ'дите ѹ'бѡ вы` соверше'ни, ꙗ'коже ѻц~ъ ва'шъ нбСный соверше'нъ є'сть.",

        u"Возведо'хъ ѻ'чи мои` въ го'ры, ѿню'дꙋже пріи'детъ по'мощь моѧ`",
    )
    context = { 'convertee': random.choice(examples) }
    return render_to_response('converter.html', context, RequestContext(request))
