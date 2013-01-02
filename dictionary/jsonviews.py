# -*- coding: utf-8 -*-
import collections
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse

import dictionary.viewmodels
from custom_user.models import CustomUser
from dictionary.models import Collocation
from dictionary.models import CollocationGroup
from dictionary.models import Entry
from dictionary.models import Etymology
from dictionary.models import Example
from dictionary.models import GreekEquivalentForExample
from dictionary.models import Meaning
from dictionary.models import MeaningContext
from dictionary.models import OrthographicVariant
from dictionary.models import Participle
from dictionary.models import PART_OF_SPEECH_MAP

IMT_JSON = 'application/json; charset=utf-8'

def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',',':'))

@login_required
def json_singleselect_entries_urls(request):
    httpGET_FIND = request.GET.get('find')
    if httpGET_FIND:
        FIND_LOWER = httpGET_FIND.lower()
        FIND_CAPZD = httpGET_FIND.capitalize()
        entries = Entry.objects \
            .filter(
                Q(civil_equivalent__startswith=FIND_LOWER)
                |
                Q(civil_equivalent__startswith=FIND_CAPZD)
            ).order_by('civil_equivalent', 'homonym_order')[:7]
        entries = [
                {
                'civil': e.civil_equivalent,
                'headword': e.orth_vars[0].idem_ucs,
                'hom': e.homonym_order,
                'pos': e.get_part_of_speech_display() if (e.homonym_order
                    and e.part_of_speech
                    and e.part_of_speech
                        not in (PART_OF_SPEECH_MAP['letter'],
                                PART_OF_SPEECH_MAP['number'])
                    ) else '',
                'hint': e.homonym_gloss,
                'url': e.get_absolute_url(),
                }
                for e in entries]
        data = _json(entries)
        response = HttpResponse(data, mimetype=IMT_JSON)
    else:
        response = HttpResponse(mimetype=IMT_JSON, status=400)
    return response



@login_required
def json_ex_save(request):
    jsonEx = request.POST.get('ex')
    if jsonEx:
        exDict = json.loads(jsonEx)
        ex = Example.objects.get(pk=int(exDict['id']))
        del exDict['id']
        ex.__dict__.update(exDict)
        ex.save()
        data = _json({ 'action': 'saved' })
        response = HttpResponse(data, mimetype=IMT_JSON, status=200)
    else:
        response = HttpResponse(status=400)
    return response


@login_required
def json_greq_save(request):
    jsonGreq = request.POST.get('greq')
    if jsonGreq:
        greq = json.loads(jsonGreq)
        if not greq['id']:
            del greq['id']
            gr = GreekEquivalentForExample(**greq)
            gr.save()
            data = _json({ 'action': 'created', 'id': gr.id })
        else:
            gr = GreekEquivalentForExample.objects.get(pk=int(greq['id']))
            gr.__dict__.update(greq)
            gr.save()
            data = _json({ 'action': 'saved' })
        response = HttpResponse(data, mimetype=IMT_JSON, status=200)
    else:
        response = HttpResponse(status=400)
    return response


@login_required
def json_greq_delete(request):
    jsonDelete = request.POST.get('delete')
    if jsonDelete:
        id = int( json.loads(jsonDelete) )
        if id:
            gr = GreekEquivalentForExample.objects.get(pk=id)
            gr.delete()
            data = _json({ 'action': 'deleted' })
            response = HttpResponse(data, mimetype=IMT_JSON, status=200)
        else:
            response = HttpResponse(status=400)
    else:
        response = HttpResponse(status=400)
    return response


@login_required
def json_goodness_save(request):
    entry_id = request.POST.get('id')
    goodness = request.POST.get('goodness')
    entry = Entry.objects.get(id=entry_id)
    entry.good = goodness
    entry.save(without_mtime=True)
    return HttpResponse('', mimetype=IMT_JSON, status=200)



def json_entry_get(request, id):
    data = dictionary.viewmodels.entry_json(id)
    return HttpResponse(data, mimetype=IMT_JSON, status=200)


def json_entry_save(request):
    model = (

        {'name': 'entry', 'model': Entry, 'terminals':
            {'orthvars': OrthographicVariant, 'participles': Participle}},

        {'name': 'etymologies', 'model': Etymology},

        {'name': 'collogroups', 'model': CollocationGroup,
            'terminals': {'collocations': Collocation}},

        {'name': 'meanings', 'model': Meaning,
            'terminals': {'contexts': MeaningContext}},

        {'name': 'examples', 'model': Example,
            'terminals': {'greqs': GreekEquivalentForExample}},

    )
    process_json_model(model, request.POST)
    return HttpResponse('ok', mimetype=IMT_JSON, status=200)


def process_json_model(json_model, post):
    post = json.loads(post.get('data'))
    for part in json_model:
        data = post[part['name']]
        if isinstance(data, collections.Sequence):
            part['data'] = data
        else:
            part['data'] = (data,)

    new_elements = {}
    deleted_elements = []
    fields2modelnames = {
        'base_entry_id': Entry.__name__,
        'base_meaning_id': Meaning.__name__,
        'collogroup_container_id': CollocationGroup.__name__,
        'collogroup_id': CollocationGroup.__name__,
        'collocation_id': Collocation.__name__,
        'derivation_entry_id': Entry.__name__,
        'editor_id': CustomUser.__name__,
        'entry_container_id': Entry.__name__,
        'entry_id': Entry.__name__,
        'etymon_to_id': Etymology.__name__,
        'for_example_id': Example.__name__,
        'for_meaning_id': Meaning.__name__,
        'meaning_id': Meaning.__name__,
        'parent_meaning_id': Meaning.__name__,
    }

    items_and_models = []
    for part in json_model:
        for item in part['data']:
            items_and_models.append((item, part['model']))
            if 'terminals' in part:
                for prop, model in part['terminals'].items():
                    for subitem in item[prop]:
                        items_and_models.append((subitem, model))
                    del item[prop]

    items_to_process = len(items_and_models)
    while items_to_process:
        PREVIOUS_VALUE = items_to_process
        for item, ItemModel in items_and_models:
            if '#status#' in item:
                if item['#status#'] == 'good':
                    continue
            else:
                item['#status#'] = 'bad'

            item_id = item['id']
            in_db = isinstance(item_id, int)
            to_be_destroyed = '_destroy' in item and item['_destroy']
            bad = False

            for key, value in [(k, v) for k, v in item.items()
                               if k.endswith('_id')]:
                if value is not None and not isinstance(value, int):
                    if value in new_elements:
                        item[key] = new_elements[value]
                    else:
                        bad = True
                if (value in deleted_elements
                or fields2modelnames[key] + str(value) in deleted_elements):
                    if in_db:
                        deleted_elements.append(ItemModel.__name__ +
                                                str(item_id))
                    else:
                        deleted_elements.append(item_id)
                    item['#status#'] = 'good'
                    items_to_process -= 1
                    continue
            if bad:
                continue

            del item['#status#']
            del item['id']
            if in_db:
                existent_item = ItemModel.objects.get(pk=item_id)
                if to_be_destroyed:
                    existent_item.delete()
                    deleted_elements.append(ItemModel.__name__ + str(item_id))
                else:
                    existent_item.__dict__.update(item)
                    existent_item.save()
            else:
                if to_be_destroyed:
                    deleted_elements.append(item_id)
                else:
                    new_item = ItemModel(**item)
                    new_item.save()
                    new_elements[item_id] = new_item.id
            item['#status#'] = 'good'
            items_to_process -= 1

        assert items_to_process!=PREVIOUS_VALUE, u'''Алгоритм сохранения лексемы
               работает неверно. Значение переменной items_to_process не
               меняется, поэтому оно не сможет достигнуть нуля и выход из
               вечного цикла никогда не произойдет.'''
