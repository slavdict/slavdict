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

    # Все этимоны для словарной статьи (в том числе вложенные). NB:
    # ``Entry.etimologies`` возвращает все этимоны, для которых нет других
    # этимонов. Поэтому здесь это не используется.
    etymons = Etymology.objects.filter(entry=entry).order_by('order', 'id')

    meanings = Meaning.objects.filter(entry_container=entry)
    # Список с тех. номерами значений
    L = range(len(meanings))

    # Список, содержащий в качестве элементов группы примеров,
    # относящиеся к одному значению. TODO: возможно, этот список лучше делать
    # по-другому для лучшей производительности.
    example_groups = [Example.objects.filter(meaning=m) for m in meanings]
    # То же для контекстов значений.
    mnng_cntxt_groups = [MeaningContext.objects.filter(meaning=m) for m in meanings]

    OrthVarFormSet = modelformset_factory(OrthographicVariant, form=OrthVarForm, extra=0)
    EtymologyFormSet = modelformset_factory(Etymology, form=EtymologyForm, extra=0)
    MeaningFormSet = modelformset_factory(Meaning, form=MeaningForm, extra=0)
    ExampleFormSet = modelformset_factory(Example, form=ExampleForm, extra=0)
    MnngCntxtFormSet = modelformset_factory(MeaningContext, form=MnngCntxtForm, extra=0)
    GrEqForMnng = modelformset_factory(GreekEquivalentForMeaning, form=GrEqForMnngForm, extra=0)
    GrEqForEx = modelformset_factory(GreekEquivalentForExample, form=GrEqForExForm, extra=0)

    if request.method == "POST":

        # Создаём формы на основе POST-данных
        entry_form = EntryForm(

            request.POST,
            instance=entry,
            prefix="entry"

            )

        orth_var_formset = OrthVarFormSet(

            request.POST,
            queryset=orth_vars,
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

        example_formset_groups = [ # list comprehension
                                   # variables: i, eg
            ExampleFormSet(

                request.POST,
                queryset=eg,
                prefix='example-%s' % i

                )

            for i, eg in enumerate(example_groups)

        ]

        mnng_cntxt_formset_groups = [ # list comprehension
                                      # variables: i, mc
            MnngCntxtFormSet(

                request.POST,
                queryset=mc,
                prefix='mnng_cntxt-%s' % i

                )

            for i, mc in enumerate(mnng_cntxt_groups)

        ]

        # Создаём список всех форм и формсетов, добавляя туда сначала сами
        # формы и формсеты.
        _forms = [

            entry_form,
            orth_var_formset,
            etymology_formset,
            meaning_formset,

            ]

        # Расширяем список за счёт example_formset_groups, т.к. эта переменная
        # содержит не формсет или форму, а целый список формсетов
        _forms.extend( example_formset_groups )
        # Аналогично.
        _forms.extend( mnng_cntxt_formset_groups )


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

        mnng_cntxt_formset_groups = [ # list comprehension
                                      # variables: i, mc
            MnngCntxtFormSet(

                queryset=mc,
                prefix='mnng_cntxt-%s' % i

                )

            for i, mc in enumerate(mnng_cntxt_groups)

        ]

    # Добавляется свойство, возвращающее список троек вида "Форма для
    # значения"--"Набор форм контекстов значения"--"Набор форм примеров
    # значения".
    meaning_formset.mnng_cntxt_ex = [(meaning_formset.forms[i], mnng_cntxt_formset_groups[i], example_formset_groups[i]) for i in L]

    return render_to_response(

        "change_form.html",

        {
            'entry_form': entry_form,
            'orth_var_formset': orth_var_formset,
            'etymology_formset': etymology_formset,
            'meaning_formset': meaning_formset,
        },
        )
