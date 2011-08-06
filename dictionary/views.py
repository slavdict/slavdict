# -*- coding: utf-8 -*-
import datetime
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext
from dictionary.models import Entry, \
    Meaning, Example, OrthographicVariant, Etymology, \
    MeaningContext, GreekEquivalentForMeaning, \
    GreekEquivalentForExample

from dictionary.forms import RawValueWidget
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from unicode_csv import UnicodeReader

# Вспомогательная функция
# для сортировки списка словарных статей.
def entry_key(entry):
    return u'%s %s' % ( entry.civil_equivalent.lower(), entry.homonym_order )

@login_required
def make_greek_found(request):
    from slavdict.dictionary.models import GreekEquivalentForExample

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
    entries = Entry.objects.all().order_by('civil_equivalent', 'homonym_order')
    entries = sorted(entries, key=entry_key)
    context = {
        'entries': entries,
        'title': u'Все статьи',
        'show_additional_info': 'ai' in request.COOKIES,
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
    from slavdict.dictionary.models import GreekEquivalentForExample, Example
    greqlist = GreekEquivalentForExample.objects.all() # Выбираем все греч. параллели для примеров.
    ex_list = [g.for_example for g in greqlist] # Создаём для них список примеров, к которым они относятся.
    # Присваеваем полю статуса греч. параллелей для каждого примера значение "найдены".
    # И сохраняем каждый пример из списка.
    for ex in ex_list:
        if ex.greek_eq_status == u'L':
            ex.greek_eq_status = u'F'
            ex.save()

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



from django.forms.models import modelformset_factory
from slavdict.dictionary.forms import EntryForm, \
    MeaningForm, ExampleForm, OrthVarForm, EtymologyForm, \
    MnngCntxtForm, GrEqForMnngForm, GrEqForExForm

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



from dictionary.forms import BilletImportForm
from django.http import HttpResponse, HttpResponseRedirect
import slavdict.unicode_csv as unicode_csv
import StringIO

from custom_user.models import CustomUser
from slavdict.directory.models import CategoryValue
ccc = CategoryValue.objects.get(pk=26) # Создана (Статус статьи "Статья создана")

from slavdict.dictionary.models import entry_dict, civilrus_convert

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
            authors = CustomUser.objects.all()

            orthvar_collisions = False
            csv_authors = {u'': None}

            for row in csv_reader:
                # Столбцы в CSV-файле
                orthvar, orthvar_is_reconstructed, civil_equivalent, word_forms_list, antconc_query, author_in_csv, additional_info = row

                if orthvar in idems:
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
                    entry_args['status'] = ccc
                    # Все булевские переменные уже выставлены по умолчанию в False в entry_dict

                    # Если поле с гражданским эквивалентом пусто, то берем конвертацию в гражданку заглавного слова.
                    # Если же это поле заполнено, то берём его без изменений. С практической точки зрения это значит,
                    # что в CSV-файле можно не указывать гражданку для слов без титл, они автоматом должны хорошо
                    # преобразовываться. А для слов с титлами или буквотитлами гражданку лучше указывать, чтобы
                    # впоследствии не надо было её уточнять из форм вроде "бл*годетель".
                    if not civil_equivalent.strip():
                        civil_equivalent = civilrus_convert(orthvar)

                    from_csv = {
                        'word_forms_list': word_forms_list,
                        'civil_equivalent': civil_equivalent,
                        'antconc_query': antconc_query,
                        'editor': author,
                        'additional_info': additional_info,
                    }
                    entry_args.update(from_csv)

                    entry = Entry.objects.create(**entry_args)
                    entry.save()

                    x = orthvar_is_reconstructed.strip()
                    if x==u'да':
                        orthvar_is_reconstructed = True
                    elif x==u'нет' or not x:
                        orthvar_is_reconstructed = False
                    else:
                        raise NameError(u"Поле реконструкции заполнено неправильно")
                    ov = OrthographicVariant.objects.create(entry=entry, idem=orthvar,
                                                            is_reconstructed=orthvar_is_reconstructed)
                    ov.save()
                    idems.append(ov.idem)

            if orthvar_collisions:
                response = HttpResponse(output.getvalue(), mimetype="text/csv")
                response['Content-Disposition'] = 'attachment; filename=%s--not.imported.csv' % datetime.datetime.strftime(datetime.datetime.now(), format='%Y.%m.%d--%H.%M.%S')
            else:
                response = HttpResponseRedirect('/')

            output.close()
            csvfile.close()
            return response
    else:
        form = BilletImportForm()
    return render_to_response('csv_import.html', {'form': form})



from slavdict.pdf import write_pdf

@login_required
def pdf_for_single_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    context = {
        'entry': entry,
        'title': u'Статья «%s»' % entry.civil_equivalent,
        'show_additional_info': 'ai' in request.COOKIES,
        'user': request.user,
        'date': datetime.datetime.now(),
        'filename': 'entry%s.pdf' % entry_id,
        }
    return write_pdf(request, 'pdf_for_single_entry.html', context)


from django.core.paginator import Paginator, EmptyPage, InvalidPage

@login_required
def entry_list(request, mine=False):
    SORT_MAPPING = {
        'alph': ('civil_equivalent', 'homonym_order'),
        '-alph': ('-civil_equivalent', '-homonym_order'),
        't': ('mtime', 'id'),
        '-t': ('-mtime', '-id'),
        }
    DEFAULT_SORT = '-t'
    VALID_SORT_PARAMS = set(SORT_MAPPING)
    GET_SORT = request.GET.get('sort')
    GET_FIND = request.GET.get('find')

    if GET_SORT:
        redirect_path = "./"
        if GET_FIND:
            redirect_path = "?find=%s" % GET_FIND
        response = HttpResponseRedirect(redirect_path)
        if GET_SORT in VALID_SORT_PARAMS:
            response.set_cookie('sort', GET_SORT)
        return response

    COOKIES_SORT = request.COOKIES.get('sort', DEFAULT_SORT)
    SORT_PARAMS = SORT_MAPPING[COOKIES_SORT]

    if GET_FIND is None and not mine:
        GET_FIND = u''
        entry_list = Entry.objects.all().order_by(*SORT_PARAMS) #filter(editor=request.user)
    else:
        if GET_FIND:
            # Ищем все лексемы, удовлетворяющие запросу в независимости от регистра начальной буквы запроса.
            # Код писался из расчёта, что на БД полагаться нельзя, поскольку у меня не получается правильно
            # настроить COLLATION в Postgres. Когда это сделать удастся, надо будет в .filter использовать
            # `civil_equivalent__istartswith=GET_FIND`.
            FIND_LOWER = GET_FIND.lower()
            FIND_UPPER = GET_FIND.capitalize()
            entry_list = Entry.objects.filter(
                    Q(civil_equivalent__startswith=FIND_LOWER) | Q(civil_equivalent__startswith=FIND_UPPER)
                ).order_by(*SORT_PARAMS) #filter(editor=request.user)
        else:
            if mine:
                entry_list = Entry.objects.filter(editor=request.user).order_by(*SORT_PARAMS)
            else:
                return HttpResponseRedirect("./")

    if COOKIES_SORT=='alph':
        entry_list = sorted(entry_list, key=entry_key, reverse=False)
    elif COOKIES_SORT=='-alph':
        entry_list = sorted(entry_list, key=entry_key, reverse=True)

    paginator = Paginator(entry_list, per_page=12, orphans=2)
    try:
        pagenum = int(request.GET.get('page', 1))
    except ValueError:
        pagenum = 1
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    context = {
        'entries': page.object_list,
        'page': page,
        'sort': COOKIES_SORT,
        'find_prefix': GET_FIND,
        'mine': mine,
        }
    return render_to_response('entry_list.html', context, RequestContext(request))

@login_required
def antconc2ucs8_converter(request):
    import random
    random.seed()
    examples = (
        u"Дрꙋ'гъ дрꙋ'га тѧготы^ носи'те, и та'кѡ испо'лните зако'нъ хрСто'въ.",

        u"Ѿ дне'й же іѡа'нна крСти'телѧ досе'лѣ, црСтвіе нбСное нꙋ'дитсѧ, и нꙋ'ждницы восхища'ютъ є`",

        u"Мно'ги скѡ'рби пра'вєднымъ, и ѿ всѣ'хъ и'хъ изба'витъ ѧ` гдСь",

        u"Наказꙋ'ѧ наказа' мѧ гдСь, сме'рти же не предаде' мѧ",

        u"Вни'дите ѹ'зкими враты`, ꙗ'кѡ простра'ннаѧ врата`, и широ'кій пꙋ'ть вводѧ'й въ па'гꙋбꙋ, "
        u"и мно'зи сꙋ'ть входѧ'щіи и'мъ. Что` ѹ'зкаѧ врата`, и тѣ'сный пꙋ'ть вводѧ'й въ живо'тъ, и ма'лѡ "
        u"и'хъ є'сть, и`же ѡбрѣта'ютъ єго`",

        u"Бꙋ'дите ѹ'бѡ вы` соверше'ни, ꙗ'коже ѻц~ъ ва'шъ нбСный соверше'нъ є'сть.",

        u"Возведо'хъ ѻ'чи мои` въ го'ры, ѿню'дꙋже пріи'детъ по'мощь моѧ`",
    )
    context = { 'convertee': random.choice(examples) }
    return render_to_response('converter.html', context, RequestContext(request))
