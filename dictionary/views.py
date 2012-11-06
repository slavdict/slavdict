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

import dictionary.models
import dictionary.viewmodels
import unicode_csv
from custom_user.models import CustomUser
from dictionary.forms import BilletImportForm
from dictionary.forms import EntryForm
from dictionary.forms import EtymologyForm
from dictionary.forms import ExampleForm
from dictionary.forms import FilterEntriesForm
from dictionary.forms import GrEqForExForm
from dictionary.forms import GrEqForMnngForm
from dictionary.forms import MeaningForm
from dictionary.forms import MnngCntxtForm
from dictionary.forms import OrthVarForm
from dictionary.forms import RawValueWidget
from dictionary.models import civilrus_convert
from dictionary.models import Entry
from dictionary.models import entry_dict
from dictionary.models import Etymology
from dictionary.models import Example
from dictionary.models import GreekEquivalentForExample
from dictionary.models import GreekEquivalentForMeaning
from dictionary.models import Meaning
from dictionary.models import MeaningContext
from dictionary.models import OrthographicVariant
from directory.models import CategoryValue
from unicode_csv import UnicodeReader




# Вспомогательная функция
# для сортировки списка словарных статей.
def entry_key(entry):
    return u'%s %s' % ( entry.civil_equivalent.lower(), entry.homonym_order )

@login_required
def make_greek_found(request):

    greqlist = GreekEquivalentForExample.objects.all() # Выбираем все греч. параллели для примеров.
    exlist = [g.for_example for g in greqlist] # Создаём для них список примеров, к которым они относятся.
    # Присваеваем полю статуса греч. параллелей для каждого примера значение "найдены".
    # И сохраняем каждый пример из списка.
    for ex in exlist:
        if ex.greek_eq_status == u'L':
            ex.greek_eq_status = u'F'
            ex.save()
    # Перенаправляем на ту страницу, с которой пользователь пришёл, либо на заглавную страницу.
    referer = request.META.get('HTTP_REFERER', '/')
    response = redirect(referer)
    return response


@login_required
def all_entries(request):
    httpGET_AUTHOR = request.GET.get('author')
    httpGET_CORRUPTED_GREEK = 'corrupted-greek' in request.GET
    httpGET_DUPLICATES = 'duplicates' in request.GET
    httpGET_FIND = request.GET.get('find')
    httpGET_LIST = request.GET.get('list')
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
        entries = entries.exclude(status__slug=u'created')

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
        greek_etymons = Etymology.objects.filter(language__slug='greek', corrupted=True)
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
    context = {
        'entries': entries,
        'title': title,
        'show_additional_info': 'ai' in request.COOKIES,
        'show_duplicates_warning': False if httpGET_DUPLICATES else True,
        'user': request.user,
        }
    return render_to_response('all_entries.html', context, RequestContext(request))


@login_required
def test_entries(request):
    grfexs = GreekEquivalentForExample.objects.filter(~Q(mark=u''))
    entry_id_list = [grfex.for_example.meaning.entry_container.id for grfex in grfexs]
    entries = Entry.objects.filter(id__in=entry_id_list).order_by('civil_equivalent', 'homonym_order')
    context = {
        'entries': entries,
        'title': u'Избранные статьи',
        'show_additional_info': 'ai' in request.COOKIES,
        'user': request.user,
        }
    return render_to_response('all_entries.html', context, RequestContext(request))


@login_required
def greek_to_find(request):
    # Обеспечиваем то, чтобы поля статуса параллей у примеров с параллелями
    # были отличны от u'L' (статус "необходимо найти параллели")
    greqlist = GreekEquivalentForExample.objects.all() # Выбираем все греч. параллели для примеров.
    ex_list = [g.for_example for g in greqlist] # Создаём для них список примеров, к которым они относятся.
    # Присваеваем полю статуса греч. параллелей для каждого примера значение "найдены".
    # И сохраняем каждый пример из списка.
    for ex in ex_list:
        if ex.greek_eq_status == u'L':
            ex.greek_eq_status = u'F'
            ex.save(without_mtime=True)

    # Выдаём все словарные статьи, для примеров которых найти греч. параллели
    # необходимо.
    status_list = (u'L',)
    #status_list = (u'L', u'A', u'C', u'N')
    ex_list = Example.objects.filter(greek_eq_status__in=status_list)
    examples_with_hosts = [(ex.host_entry, ex.host, ex) for ex in ex_list]
    examples_with_hosts = sorted(examples_with_hosts, key=lambda x: entry_key(x[0]))
    examples_with_hosts = [(n + 1, e[1], e[2]) for n, e in enumerate(examples_with_hosts)]

    context = {
        'examples_with_hosts': examples_with_hosts,
        'title': u'Примеры, для которых необходимо найти греческие параллели',
        'show_additional_info': 'ai' in request.COOKIES,
        'user': request.user,
        }
    return render_to_response('greek_to_find.html', context, RequestContext(request))


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
def last_entry(request):
    error = False
    try:
        entry = Entry.objects.all().order_by('-id')[0]
    except IndexError:
        entry = None
        error = True
    context = {
        'entry': entry,
        'title': u'Последняя добавленная статья',
        'show_additional_info': 'ai' in request.COOKIES,
        'error': error,
        'user': request.user,
        }
    return render_to_response('single_entry.html', context, RequestContext(request))


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
def change_entry(request, entry_id):

    entry = get_object_or_404(Entry, pk=entry_id)

    orthvars = OrthographicVariant.objects.filter(entry=entry).order_by('order','id')
    # Все этимоны для словарной статьи (в том числе вложенные). NB:
    # ``entry.etimologies`` возвращает все этимоны, для которых нет других
    # этимонов. Поэтому здесь это не используется.
    etymons = Etymology.objects.filter(entry=entry).order_by('order', 'id')
    meanings = Meaning.objects.filter(entry_container=entry).order_by('order','id')
    examples = Example.objects.filter(meaning__in=meanings).order_by('meaning','order','id')
    cntxts = MeaningContext.objects.filter(meaning__in=meanings).order_by('meaning','order','id')
    grfmnngs = GreekEquivalentForMeaning.objects.filter(for_meaning__in=meanings).order_by('for_meaning','id')
    grfexs = GreekEquivalentForExample.objects.filter(for_example__in=examples).order_by('for_example','id')

    OrthVarFormSet = modelformset_factory(OrthographicVariant, form=OrthVarForm, extra=0)
    EtymologyFormSet = modelformset_factory(Etymology, form=EtymologyForm, extra=0)
    MeaningFormSet = modelformset_factory(Meaning, form=MeaningForm, extra=0)
    ExampleFormSet = modelformset_factory(Example, form=ExampleForm, extra=0)
    MnngCntxtFormSet = modelformset_factory(MeaningContext, form=MnngCntxtForm, extra=0)
    GrEqForMnngFormSet = modelformset_factory(GreekEquivalentForMeaning, form=GrEqForMnngForm, extra=0)
    GrEqForExFormSet = modelformset_factory(GreekEquivalentForExample, form=GrEqForExForm, extra=0)

    if request.method == "POST":

        # Создаём формы на основе POST-данных
        entry_form = EntryForm(

            request.POST,
            instance=entry,
            prefix="entry"

            )

        orthvar_formset = OrthVarFormSet(

            request.POST,
            queryset=orthvars,
            prefix='orthvar'

            )

        etymology_formset = EtymologyFormSet(

            request.POST,
            queryset=etymons,
            prefix='etym'

            )

        meaning_formset = MeaningFormSet(

            request.POST,
            queryset=meanings,
            prefix='meaning'

            )

        example_formset = ExampleFormSet(

            request.POST,
            queryset=examples,
            prefix='example'

            )

        cntxt_formset = MnngCntxtFormSet(

            request.POST,
            queryset=cntxts,
            prefix='cntxt'

            )

        grfmnng_formset = GrEqForMnngFormSet(

            request.POST,
            queryset=grfmnngs,
            prefix='grfmnng'

            )

        grfex_formset = GrEqForExFormSet(

            request.POST,
            queryset=grfexs,
            prefix='grfex'

            )

        # Создаём список всех форм и формсетов, добавляя туда сначала сами
        # формы и формсеты.
        _forms = [

            entry_form,
            orthvar_formset,
            etymology_formset,
            meaning_formset,
            example_formset,
            cntxt_formset,
            grfmnng_formset,
            grfex_formset,

            ]

        # Список правильности заполнения форм.
        # NB: необходимо, чтобы метод is_valid() был вызван для каждого
        # элемента списка, иначе не все формы будут проверены. Поэтому,
        # например, в силу лени операции конкатенации, ``if ...and ...and...``
        # не подойдёт.
        forms_validity = [x.is_valid() for x in _forms]

        if all(forms_validity):
            for x in _forms:
                # TODO: здесь должен быть учёт зависимостей, чтобы не пытаться
                # сохранить раньше времени те объекты, которые зависят от
                # других ещё не существующих.
                x.save()
            return redirect( entry.get_absolute_url() )

    else:
        entry_form = EntryForm(

            instance=entry,
            prefix='entry'

            )

        orthvar_formset = OrthVarFormSet(

            queryset=orthvars,
            prefix='orthvar'

            )

        etymology_formset = EtymologyFormSet(

            queryset=etymons,
            prefix='etym'

            )

        meaning_formset = MeaningFormSet(

            queryset=meanings,
            prefix='meaning'

            )

        example_formset = ExampleFormSet(

            queryset=examples,
            prefix='example'

            )

        cntxt_formset = MnngCntxtFormSet(

            queryset=cntxts,
            prefix='cntxt'

            )

        grfmnng_formset = GrEqForMnngFormSet(

            queryset=grfmnngs,
            prefix='grfmnng'

            )

        grfex_formset = GrEqForExFormSet(

            queryset=grfexs,
            prefix='grfex'

            )


    meaning_ids = [meaning.id for meaning in meanings]
    raw_widget = RawValueWidget()

    for example_form in example_formset.forms:
        #try: mID = example_form.instance.meaning.id
        #except DoesNotExist:

        #mID = example_form.instance.meaning.id
        mID = int(example_form['meaning'].as_widget(widget=raw_widget))
        # Если выдаваемая строка будет содержать нецифровые символы или вообще
        # не содрежать символов будет вызвано исключение ValueError. Его пока
        # решено не обрабатывать.

        i = meaning_ids.index(mID)
        x = meaning_formset.forms[i]
        if hasattr(x, 'example_forms'):
            x.example_forms.append(example_form)
        else:
            x.example_forms = [example_form,]

    for cntxt_form in cntxt_formset.forms:
        #mID = cntxt_form.instance.meaning.id
        mID = int(cntxt_form['meaning'].as_widget(widget=raw_widget))
        i = meaning_ids.index(mID)
        x = meaning_formset.forms[i]
        if hasattr(x, 'cntxt_forms'):
            x.cntxt_forms.append(cntxt_form)
        else:
            x.cntxt_forms = [cntxt_form,]

    for grfmnng_form in grfmnng_formset.forms:
        #mID = grfmnng_form.instance.for_meaning.id
        mID = int(grfmnng_form['for_meaning'].as_widget(widget=raw_widget))
        i = meaning_ids.index(mID)
        x = meaning_formset.forms[i]
        if hasattr(x, 'grfmnng_forms'):
            x.grfmnng_forms.append(grfmnng_form)
        else:
            x.grfmnng_forms = [grfmnng_form,]

    example_ids = [example.id for example in examples]

    for grfex_form in grfex_formset.forms:
        #mID = grfex_form.instance.for_example.id
        mID = int(grfex_form['for_example'].as_widget(widget=raw_widget))
        i = example_ids.index(mID)
        x = example_formset.forms[i]
        if hasattr(x, 'grfex_forms'):
            x.grfex_forms.append(grfex_form)
        else:
            x.grfex_forms = [grfex_form,]

    context = {
        'entry_form': entry_form,
        'orthvar_formset': orthvar_formset,
        'etymology_formset': etymology_formset,
        'meaning_formset': meaning_formset,

        'example_management_form': example_formset.management_form,
        'cntxt_management_form': cntxt_formset.management_form,
        'grfmnng_management_form': grfmnng_formset.management_form,
        'grfex_management_form': grfex_formset.management_form,

        'example_empty_form': example_formset.empty_form,
        'cntxt_empty_form': cntxt_formset.empty_form,
        'grfmnng_empty_form': grfmnng_formset.empty_form,
        'grfex_empty_form': grfex_formset.empty_form,
        }
    return render_to_response("change_form.html", context, RequestContext(request))



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

                    entry_args = entry_dict.copy() # Поверхностная (!) копия словаря.
                    entry_args['status'] = CategoryValue.objects.get(pk=26) # 26 -- статус статьи "Статья создана"
                    # Все булевские переменные уже выставлены по умолчанию в False в entry_dict

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

                    if not intersection or (force == 'add'):
                        entry_args.update(from_csv)
                        entry_args.update({
                            'reconstructed_headword': orthvars_list[0][1],
                            'questionable_headword': orthvars_list[0][2],
                            })

                        entry = Entry.objects.create(**entry_args)
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


def _get_entries(form):
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


@login_required
def entry_list(request):
    if 'find' in request.COOKIES:
        request.COOKIES['find'] = base64.standard_b64decode(request.COOKIES['find']).decode('utf8')

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
    entries = _get_entries(form.cleaned_data)

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
        'form': form,
        'page': page,
        'user': request.user,
        }
    response = render_to_response('entry_list.html', context, RequestContext(request))
    if request.method == 'POST':
        form.cleaned_data['find'] = base64.standard_b64encode(form.cleaned_data['find'].encode('utf8'))
        for param, value in form.cleaned_data.items():
            response.set_cookie(param, value, path=request.path)
    return response


@login_required
def hellinist_workbench(request):

    DEFAULT_STATUS = 'L'
    httpGET_STATUS = request.GET.get('status')
    if httpGET_STATUS not in [s[0] for s in dictionary.models.Example.GREEK_EQ_STATUS]:
        httpGET_STATUS = None

    if httpGET_STATUS:
        redirect_path = "./"
        response = HttpResponseRedirect(redirect_path)
        response.set_cookie('HWstatus', httpGET_STATUS, path=request.path)
        return response

    COOKIES_STATUS = request.COOKIES.get('HWstatus', DEFAULT_STATUS)

    examples = Example.objects.filter(greek_eq_status=COOKIES_STATUS).order_by('id')

    paginator = Paginator(examples, per_page=4, orphans=2)
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
            'id': e.id, 'triplet': e.context_ucs, 'antconc': e.context.strip() or e.example,
            'address': e.address_text, 'status': e.greek_eq_status, 'comment': e.additional_info,
            'greqs': [
                { 'unitext': greq.unitext, 'text': greq.text, 'initial_form': greq.initial_form,
                  'id': greq.id, 'additional_info': greq.additional_info }
                for greq in e.greek_equivs
            ]
        }
    for e in page.object_list]

    context = {
        'title': u'Греческий кабинет',
        'examples': page.object_list,
        'jsonExamples': json.dumps(vM_examples, ensure_ascii=False, separators=(',',':')),
        'statusList': dictionary.models.Example.GREEK_EQ_STATUS,
        'statusFilter': COOKIES_STATUS,
        'page': page,
        }
    return render_to_response('hellinist_workbench.html', context, RequestContext(request))


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
