# -*- coding: utf-8 -*-
import datetime
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext
from slavdict.dictionary.models import Entry, \
    Meaning, Example, OrthographicVariant, Etymology, \
    MeaningContext, GreekEquivalentForMeaning, \
    GreekEquivalentForExample

def all_entries(request):
    entries = Entry.objects.all().order_by('civil_equivalent', 'homonym_order')
    return render_to_response(

        'all_entries.html',

        {
            'entries': entries,
            'title': u'Все статьи',
            'show_additional_info': 'ai' in request.COOKIES,
            'user': request.user,
        },

        RequestContext(request),
        )


def single_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    return render_to_response(

        'single_entry.html',

        {
            'entry': entry,
            'title': u'Статья «%s»' % entry.civil_equivalent,
            'show_additional_info': 'ai' in request.COOKIES,
            'user': request.user,
        },

        RequestContext(request),
        )


def last_entry(request):
    error = False
    try:
        entry = Entry.objects.all().order_by('-id')[0]
    except IndexError:
        entry = None
        error = True
    return render_to_response(

        'single_entry.html',

        {
            'entry': entry,
            'title': u'Последняя добавленная статья',
            'show_additional_info': 'ai' in request.COOKIES,
            'error': error,
            'user': request.user,
        },

        RequestContext(request),
        )


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

def change_entry(request, entry_id):

    entry = Entry.objects.get(pk=entry_id)

    # Орфографические варианты.
    orth_vars = entry.orth_vars

    meanings = Meaning.objects.filter(entry_container=entry)
    # Список с тех. номерами значений
    L = range(len(meanings))

    # Список, содержащий в качестве элементов группы примеров,
    # относящиеся к одному значению.
    example_groups = [Example.objects.filter(meaning=m) for m in meanings]

    OrthVarFormSet = modelformset_factory(OrthographicVariant, form=OrthVarForm, extra=0)
    EtymologyFormSet = modelformset_factory(Etymology, form=EtymologyForm, extra=0)
    MeaningFormSet = modelformset_factory(Meaning, form=MeaningForm, extra=0)
    ExampleFormSet = modelformset_factory(Example, form=ExampleForm, extra=0)
    MnngCntxtFormSet = modelformset_factory(MeaningContext, form=MnngCntxtForm, extra=0)
    GrEqForMnng = modelformset_factory(GreekEquivalentForMeaning, form=GrEqForMnngForm, extra=0)
    GrEqForEx = modelformset_factory(GreekEquivalentForExample, form=GrEqForExForm, extra=0)

    if request.method == "POST":

        # Создаём локальную переменную POST для нужд разсортировки данных из
        # request.POST.
        POST = {

            'entry': {},

            'orthvars': {},
            'etymons': {},
            'meanings': {},

            'mnng_cntxt_groups': {},
            'example_groups': {},
            'greq_mnng_groups': {},
            'greq_ex_groups': {},

        }

        # Рассортировываем данные из request.POST по различным словарям нового
        # локального словаря POST.
        for key in request.POST.keys():

            if key.startswith('en'): # entry
                POST['entry'][key] = request.POST[key]

            elif key.startswith('o'): # orthvar
                POST['orthvars'][key] = request.POST[key]

            elif key.startswith('m'): # meaning
                POST['meanings'][key] = request.POST[key]

            elif key.startswith('ex'): # example

                # Получаем строку с номером группы примеров, т.е. номером
                # значения, к которому они относятся.
                s = key.split('-', 2)[1] # 'example-12-0-field' --> '12'

                # Добавляем ключ с пустым словарём, если ключа ещё нет.
                if s not in POST['example_groups']:
                    POST['example_groups'][s] = {}

                POST['example_groups'][s][key] = request.POST[key]


        # Создаём формы на основе POST-данных
        entry_form = EntryForm(

            POST['entry'],
            instance=entry,
            prefix="entry"

            )

        orth_var_formset = OrthVarFormSet(

            POST['orthvars'],
            queryset=orth_vars,
            prefix='orthvar'

            )

        etymology_formset = EtymologyFormSet(

            POST['etymons'],
            queryset=etymons,
            prefix='etym'

            )

        meaning_formset = MeaningFormSet(

            POST['meanings'],
            queryset=meanings,
            prefix='meaning'

            )

        example_formset_groups = [ # list comprehension
                                   # variables: i, eg
            ExampleFormSet(

                POST['example_groups'][str(i)],
                queryset=eg,
                prefix='example-%s' % i

                )

            for i, eg in enumerate(example_groups)

        ]
        #TODO
        mnng_cntxt_formset_groups = [ # list comprehension
                                      # variables: i, mc
            ExampleFormSet(

                POST['mnng_cntxt_groups'][str(i)],
                queryset=mc,
                prefix='mnng_cntxt-%s' % i

                )
            #TODO
            for i, eg in enumerate(example_groups)

        ]


        # Создаём список всех форм и формсетов.
        _forms = [entry_form, orth_var_formset, meaning_formset]
        # Расширяем список за счёт example_formset_groups, т.к. эта переменная
        # содержит не формсет или форму, а целый список формсетов
        _forms.extend( example_formset_groups )


        # Список правильности заполнения форм.
        # NB: необходимо, чтобы метод is_valid() был вызван для каждого
        # элемента списка, иначе не все формы будут проверены. Поэтому,
        # например, в силу лени операции конкатенации, ``if ...and ...and...``
        # не подойдёт.
        forms_validity = [x.is_valid() for x in _forms]

        if all(forms_validity):
            for x in _forms:
                x.save()
            return redirect( entry.get_absolute_url() )

    else:
        entry_form = EntryForm(

            instance=entry,
            prefix='entry'

            )

        orth_var_formset = OrthVarFormSet(

            queryset=orth_vars,
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

        example_formset_groups = [ # list comprehension
                                   # variables: i, eg
            ExampleFormSet(

                queryset=eg,
                prefix='example-%s' % i

                )

            for i, eg in enumerate(example_groups)
        ]

    # Добавляется свойство, возвращающее список пар вида
    # "Форма для значения"-"Набор форм примеров значения".
    meaning_formset.with_examples = [(meaning_formset.forms[i], example_formset_groups[i]) for i in L]

    return render_to_response(

        "change_form.html",

        {
            'entry_form': entry_form,
            'meaning_formset': meaning_formset,
            'orth_var_formset': orth_var_formset,
        },
        )
