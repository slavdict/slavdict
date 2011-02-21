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

    for example_form in example_formset.forms:
        # TODO: здесь должен быть `try...catch`, так как `.instance` будет не у
        # всех форм.
        mID = example_form.instance.meaning.id
        i = meaning_ids.index(mID)
        x = meaning_formset.forms[i]
        if hasattr(x, 'example_forms'):
            x.example_forms.append(example_form)
        else:
            x.example_forms = [example_form,]

    for cntxt_form in cntxt_formset.forms:
        # TODO: аналогично.
        mID = cntxt_form.instance.meaning.id
        i = meaning_ids.index(mID)
        x = meaning_formset.forms[i]
        if hasattr(x, 'cntxt_forms'):
            x.cntxt_forms.append(cntxt_form)
        else:
            x.cntxt_forms = [cntxt_form,]

    for grfmnng_form in grfmnng_formset.forms:
        # TODO: аналогично.
        mID = grfmnng_form.instance.for_meaning.id
        i = meaning_ids.index(mID)
        x = meaning_formset.forms[i]
        if hasattr(x, 'grfmnng_forms'):
            x.grfmnng_forms.append(grfmnng_form)
        else:
            x.grfmnng_forms = [grfmnng_form,]

    example_ids = [example.id for example in examples]

    for grfex_form in grfex_formset.forms:
        # TODO: аналогично.
        mID = grfex_form.instance.for_example.id
        i = example_ids.index(mID)
        x = example_formset.forms[i]
        if hasattr(x, 'grfex_forms'):
            x.grfex_forms.append(grfex_form)
        else:
            x.grfex_forms = [grfex_form,]


    return render_to_response(

        "change_form.html",

        {
            'entry_form': entry_form,
            'orthvar_formset': orthvar_formset,
            'etymology_formset': etymology_formset,
            'meaning_formset': meaning_formset,

            'example_management_form': example_formset.management_form,
            'cntxt_management_form': cntxt_formset.management_form,
            'grfmnng_management_form': grfmnng_formset.management_form,
            'grfex_management_form': grfex_formset.management_form,
        },
        )
