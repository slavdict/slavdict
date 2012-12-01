# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse

from dictionary.models import Entry
from dictionary.models import Example
from dictionary.models import GreekEquivalentForExample
from dictionary.models import PART_OF_SPEECH_MAP

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
                'hom': e.homonym_order_roman,
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
        response = HttpResponse(data, mimetype='application/json')
    else:
        response = HttpResponse(mimetype='application/json', status=400)
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
        response = HttpResponse(data, mimetype='application/json', status=200)
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
        response = HttpResponse(data, mimetype='application/json', status=200)
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
            response = HttpResponse(data, mimetype='application/json', status=200)
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
    return HttpResponse('', mimetype='application/json', status=200)
