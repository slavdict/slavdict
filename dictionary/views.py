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

    entry_list = [
        ex.meaning.entry_container or \
        ex.meaning.collogroup_container.base_entry or \
        ex.meaning.collogroup_container.base_meaning.entry_container
        for ex in ex_list
        ]
    entry_id_list = [e.id for e in entry_list]

    entries = Entry.objects.filter(id__in=entry_id_list).order_by('civil_equivalent', 'homonym_order')
    context = {
        'entries': entries,
        'title': u'Статьи, для примров которых необходимо найти греческие параллели',
        'show_additional_info': 'ai' in request.COOKIES,
        'user': request.user,
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
from django.http import HttpResponseRedirect, HttpResponse
from custom_user.models import CustomUser

# Взято полностью с
# http://docs.python.org/library/csv.html#examples
import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#
# конец вырезки из документации по Питону
#

sniffer = csv.Sniffer()

from slavdict.directory.models import CategoryValue
ccc = CategoryValue.objects.get(pk=26) # Создана

entry_dict = {
    'additional_info': u'',
    'antconc_query': u'',
    'canonical_name': False,
    'cf_collogroups': None,
    'cf_entries': None,
    'cf_meanings': None,
    'civil_equivalent': u'',
    'derivation_entry': None,
    'editor': None,
    'gender': None,
    'genitive': u'',
    'grequiv_status': None,
    'hidden': False,
    'homonym_gloss': u'',
    'homonym_order': None,
    'link_to_collogroup': None,
    'link_to_entry': None,
    'link_to_meaning': None,
    'nom_pl': u'',
    'nom_sg': u'',
    'onym': None,
    'part_of_speech': None,
    'participle_type': None,
    'percent_status': None,
    'possessive': False,
    'sg1': u'',
    'sg2': u'',
    'short_form': u'',
    'status': None,
    'tantum': None,
    'transitivity': None,
    'uninflected': False,
    'word_forms_list': u'',
}

@login_required
def import_csv_billet(request):

    if request.method == 'POST':
        form = BilletImportForm(request.POST, request.FILES)
        if form.is_valid():

            csvfile = request.FILES['csvfile']
            dialect = sniffer.sniff(csvfile.read(65535))
            csvfile.seek(0)
            csv_reader = UnicodeReader(csvfile, dialect, encoding='utf-8')

            idems = OrthographicVariant.objects.all().values_list('idem')
            authors = CustomUser.objects.all()

            collision_orthvars = []
            collision_csv_rows = []

            for n, row in enumerate(csv_reader):
                orthvar, word_forms_list, antconc_query, author, additional_info = row
                if orthvar in idems:
                    collision_orthvars.append(idems.index(orthvar))
                    collision_csv_rows.append(n)
                else:
                    for au in authors:
                        if author.startswith(au.last_name):
                            author = au
                            break

                    entry = Entry.objects.create( word_forms_list=word_forms_list,
                        antconc_query=antconc_query, editor=author,
                        additional_info=additional_info,

                        hidden=False, uninflected=False, canonical_name=False, possessive=False, status=ccc)

                    entry.save()
                    ov = OrthographicVariant.objects.create(entry=entry, idem=orthvar)
                    ov.save()

            csvfile.close()
            #return render_to_response('csv_import_conflicts.html', )
            return HttpResponseRedirect('/')
    else:
        form = BilletImportForm()
    return render_to_response('csv_import.html', {'form': form})


from django import http
from django.template.loader import render_to_string
import ho.pisa as pisa
import cStringIO as StringIO
from django.conf import settings

def write_pdf(request, template_src, context_dict):
    html  = render_to_string(template_src, context_dict, RequestContext(request))
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(
        StringIO.StringIO(html.encode('UTF-8')),
        result,
        path=settings.STATIC_ROOT + 'stub')
        # Аргумент path внутренне используется следующим образом.
        # pisaDocument преполагает, что это тот путь, по которому должен был
        # быть расположен наш html-файл. На основе этого пути вычисляется
        # путь объемлющей директории. И он принимается за отправную точку
        # для вычисления относительных ссылок в файле. В данном случае
        # строчка 'stub' в `path = settings.STATIC_ROOT + 'stub'` используется
        # только для того, чтобы она была отсечена и чтобы в качестве отправной
        # директории использовался путь settings.STATIC_ROOT.
    if not pdf.err:
        response = http.HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s' % context_dict['filename']
        return response
    return http.HttpResponseRedirect('/')


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
def entry_list(request):
    SORT_MAPPING = {
        'alph': ('civil_equivalent', 'homonym_order'),
        '-alph': ('-civil_equivalent', '-homonym_order'),
        't': ('mtime',),
        '-t': ('-mtime',),
        }
    DEFAULT_SORT = '-t'
    VALID_SORT_PARAMS = set(SORT_MAPPING)
    GET_SORT = request.GET.get('sort')
    if GET_SORT:
        response = HttpResponseRedirect("?")
        if GET_SORT in VALID_SORT_PARAMS:
            response.set_cookie('sort', GET_SORT)
        return response

    COOKIES_SORT = request.COOKIES.get('sort', DEFAULT_SORT)
    SORT_PARAMS = SORT_MAPPING[COOKIES_SORT]
    entry_list = Entry.objects.all().order_by(*SORT_PARAMS) #filter(editor=request.user)
    paginator = Paginator(entry_list, per_page=15, orphans=2)
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
        }
    return render_to_response('entry_list.html', context, RequestContext(request))