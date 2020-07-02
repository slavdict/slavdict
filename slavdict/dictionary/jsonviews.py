import collections
import datetime
import json
import re

from django.apps import apps
from django.core import mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.db.models.fields import Field
from django.http import HttpResponse

from slavdict.dictionary import viewmodels
from slavdict.dictionary.models import Collocation
from slavdict.dictionary.models import CollocationGroup
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Etymology
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import GreekEquivalentForExample
from slavdict.dictionary.models import LANGUAGE_MAP
from slavdict.dictionary.models import Meaning
from slavdict.dictionary.models import MeaningContext
from slavdict.dictionary.models import OrthographicVariant
from slavdict.dictionary.models import Participle
from slavdict.dictionary.models import PART_OF_SPEECH_MAP
from slavdict.dictionary.models import STATUS_MAP
from slavdict.dictionary.models import Translation
from slavdict.dictionary.utils import get_query_orterms
from slavdict.dictionary.utils import make_query_from_orterms

IMT_JSON = 'application/json; charset=utf-8'

def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',',':'))

def authorize_entry(entry, user):
    ''' Возвращает булево значение по условию:

            PREP and (ORPHAN or AUTHOR or EDITOR):

    PREP -- учет залочки статьи для подготовки печатной версии словаря
    ORPHAN -- статья без авторов
    AUTHOR -- статья принадлежит текущему пользователю
    EDITOR -- текущий пользователь является редактором
    '''
    return ((not entry.preplock or user.has_key_for_preplock)  # PREP
        and (not entry.authors.exists()  # ORPHAN
             or user in entry.authors.all()  # AUTHOR
             or user.is_admeditor))  # EDITOR

def always_authorize_entry(entry, user):
    return True


@login_required
def json_singleselect_entries_urls(request):
    user = request.user
    httpGET_FIND = request.GET.get('find')
    httpGET_AUTH = request.GET.get('auth')
    if httpGET_FIND:
        FIND_LOWER = httpGET_FIND.lower()
        FIND_CAPZD = httpGET_FIND.capitalize()
        entries = Entry.objects \
            .filter(
                Q(civil_equivalent__startswith=FIND_LOWER)
                |
                Q(civil_equivalent__startswith=FIND_CAPZD)
            ).order_by('civil_equivalent', 'homonym_order')[:7]
        authorize = authorize_entry if httpGET_AUTH else always_authorize_entry
        entries = [e.get_search_item() for e in entries if authorize(e, user)]
        data = _json(entries).encode('utf-8')
        response = HttpResponse(data, content_type=IMT_JSON)
    else:
        response = HttpResponse(content_type=IMT_JSON, status=400)
    return response

@login_required
def json_meanings_for_entry(request):
    httpGET_ID = request.GET.get('id')
    if httpGET_ID:
        meanings = Meaning.objects.filter(
            entry_container_id=int(httpGET_ID),
            parent_meaning_id__isnull=True
        ).order_by('order', 'id')
        meanings = [
            { 'id': m.id,
              'meaning': m.meaning,
              'gloss': m.gloss }
            for m in meanings]
        data = _json(meanings).encode('utf-8')
        response = HttpResponse(data, content_type=IMT_JSON)
    else:
        response = HttpResponse(content_type=IMT_JSON, status=400)
    return response



@login_required
def json_ex_save(request):
    jsonEx = request.POST.get('ex')
    if jsonEx:
        exDict = json.loads(jsonEx)
        key = 'saveAuditTime'
        if key in exDict:
            if exDict[key]:
                exDict['audited_time'] = datetime.datetime.now()
            del exDict[key]
        ex = Example.objects.get(pk=int(exDict['id']))
        del exDict['id']
        ex.__dict__.update(exDict)
        ex.save()
        data = _json({ 'action': 'saved' }).encode('utf-8')
        response = HttpResponse(data, content_type=IMT_JSON, status=200)
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
            data = { 'action': 'created', 'id': gr.id }
        else:
            gr = GreekEquivalentForExample.objects.get(pk=int(greq['id']))
            gr.__dict__.update(greq)
            gr.save()
            data = { 'action': 'saved' }
        data['greek_eq_status'] = gr.for_example.greek_eq_status
        data = _json(data).encode('utf-8')
        response = HttpResponse(data, content_type=IMT_JSON, status=200)
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
            example = gr.for_example
            gr.delete()
            data = _json({ 'action': 'deleted',
                           'greek_eq_status': example.greek_eq_status })
            data = data.encode('utf-8')
            response = HttpResponse(data, content_type=IMT_JSON, status=200)
        else:
            response = HttpResponse(status=400)
    else:
        response = HttpResponse(status=400)
    return response


GREEK_RANGE = re.compile('[\u0370-\u0373\u0376-\u037D\u0386\u0388-\u03E1'
                         '\u1f00-\u1fbc\u1fc2-\u1fcc\u1fd0-\u1fdb'
                         '\u1fe0-\u1fec\u1ff2-\u1ffc]')
@login_required
def json_etym_save(request):
    jsonEtym = request.POST.get('etym')
    if jsonEtym:
        etym = json.loads(jsonEtym)
        if GREEK_RANGE.search(etym['unitext']):
            etym['language'] = LANGUAGE_MAP['greek']
        else:
            etym['language'] = LANGUAGE_MAP['latin']
        if not etym['id']:
            del etym['id']
            et = Etymology(**etym)
            et.save()
            data = _json({ 'action': 'created', 'id': et.id })
        else:
            et = Etymology.objects.get(pk=int(etym['id']))
            et.__dict__.update(etym)
            et.save()
            data = _json({ 'action': 'saved' }).encode('utf-8')
        response = HttpResponse(data, content_type=IMT_JSON, status=200)
    else:
        response = HttpResponse(status=400)
    return response


@login_required
def json_etym_delete(request):
    jsonDelete = request.POST.get('delete')
    if jsonDelete:
        id = int( json.loads(jsonDelete) )
        if id:
            et = Etymology.objects.get(pk=id)
            et.delete()
            data = _json({ 'action': 'deleted' }).encode('utf-8')
            response = HttpResponse(data, content_type=IMT_JSON, status=200)
        else:
            response = HttpResponse(status=400)
    else:
        response = HttpResponse(status=400)
    return response



@login_required
def json_entry_get(request, id):
    data = viewmodels.entry_json(id).encode('utf-8')
    return HttpResponse(data, content_type=IMT_JSON, status=200)


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
            'terminals': {'greqs': GreekEquivalentForExample,
                          'translations': Translation}},

    )
    invalid_keys_notifications = None
    with transaction.atomic():
        invalid_keys_notifications = process_json_model(model, request.POST)
    if invalid_keys_notifications:
        from django.core.mail import mail_admins
        subject = '[slavdict] JSON содержит отсутствующие в моделях поля'
        message = '''
При сохранении статей в JSON-данных содержались
следующие лишние поля, которых нет в соответствующих
моделях: '''
        message += ', '.join(invalid_keys_notifications)
        mail_admins(subject, message, fail_silently=True)
    return HttpResponse(status=200)


def merge_charfields(src, dst, fieldname, joiner=', '):
    src_str = getattr(src, fieldname)
    dst_str = getattr(dst, fieldname)
    if src_str:
        if dst_str:
            setattr(dst, fieldname, joiner.join([dst_str, src_str]))
        else:
            setattr(dst, fieldname, src_str)


@login_required
def json_entry_merge(request):
    src, dst = int(request.POST['src']), int(request.POST['dst'])
    if src == dst:
        # Недопустимо объединять статью с ней же самой
        return HttpResponse(status=400)
    src = Entry.objects.get(pk=src)
    dst = Entry.objects.get(pk=dst)
    with transaction.atomic():
        for a in src.authors.all():
            dst.authors.add(a)
        for ov in src.orth_vars:
            ov.order += 1000
            ov.save()
            dst.orthographic_variants.add(ov)
        for et in src.etymology_set.all():
            et.entry = dst
            et.order += 1000
            et.save()
        for p in src.participle_set.all():
            p.entry = dst
            p.order += 1000
            p.save()
        for ex in src.example_set.all():
            ex.entry = dst
            ex.order += 1000
            ex.save()
        for m in src.meaning_set.all():
            if m.entry_container is not None and m.entry_container == src:
                m.entry_container = dst
                m.order += 1000
                m.save()
        for e in src.cf_entries.all():
            if e.id != dst.id:
                dst.cf_entries.add(e)
        for cg in src.cf_collogroups.all():
            dst.cf_collogroups.add(cg)
        for m in src.cf_meanings.all():
            dst.cf_meanings.add(m)

        if not dst.part_of_speech and src.part_of_speech:
            dst.part_of_speech = src.part_of_speech
        merge_charfields(src, dst, 'word_forms_list', joiner=', ')
        merge_charfields(src, dst, 'genitive', joiner=',')
        merge_charfields(src, dst, 'nom_sg', joiner=',')
        merge_charfields(src, dst, 'short_form', joiner=',')
        merge_charfields(src, dst, 'sg1', joiner=',')
        merge_charfields(src, dst, 'sg2', joiner=',')
        merge_charfields(src, dst, 'additional_info', joiner=' /// ')

        orterms = get_query_orterms(dst.antconc_query)
        orterms.extend(get_query_orterms(src.antconc_query))
        dst.antconc_query = make_query_from_orterms(orterms)

        dst.special_case = ''
        dst.status = STATUS_MAP['inWork']
        dst.duplicate = False
        dst.save()
        src.delete()
    return HttpResponse(status=200)


def js_error_notify(request):
    connection = mail.get_connection()
    time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
    url = 'http://slavdict.ruslang.ru/entries/%s/edit/' % request.POST['entryId']
    emails = [email for name, email in settings.ADMINS]
    message = mail.EmailMessage(
        '[slavdict JS Error] %s, %s' % (time, url),
        str(request.POST),
        'jsException@slavdict.ruslang.ru',
        emails,
        connection=connection,
    )
    message.send()
    return HttpResponse(status=200)


def process_json_model(json_model, post):
    post = json.loads(post.get('json'))
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
                for prop, model in list(part['terminals'].items()):
                    for subitem in item[prop]:
                        items_and_models.append((subitem, model))
                    del item[prop]

    model_field_names = {}
    invalid_keys_notifications = set()
    items_to_move = []
    items_to_process = len(items_and_models)
    while items_to_process:
        PREVIOUS_VALUE = items_to_process
        for item, ItemModel in items_and_models:
            if ItemModel.__name__ not in model_field_names:
                model_field_names[ItemModel.__name__] = [
                        f.attname for f in ItemModel._meta.get_fields()
                        if isinstance(f, Field)]
            valid_field_names = model_field_names[ItemModel.__name__]

            if '#status#' in item:
                if item['#status#'] == 'good':
                    continue
            else:
                item['#status#'] = 'bad'

            item_id = item['id']
            in_db = isinstance(item_id, int)
            to_be_destroyed = '_destroy' in item and item['_destroy']
            bad = False

            for key, value in [(k, v) for k, v in list(item.items())
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

            move_item = False
            if '#move#' in item:
                move_item = True
                del item['#move#']

            del item['#status#']
            del item['id']
            for key in list(item.keys()):
                if key not in valid_field_names:
                    del item[key]
                    invalid_keys_notifications.add(
                            '%s.%s' % (ItemModel.__name__, key))
            if in_db:
                existent_item = ItemModel.objects.get(pk=item_id)
                if to_be_destroyed:
                    existent_item.delete()
                    deleted_elements.append(ItemModel.__name__ + str(item_id))
                else:
                    existent_item.__dict__.update(item)
                    existent_item.save()
                    if move_item:
                        items_to_move.append(existent_item)
            else:
                if to_be_destroyed:
                    deleted_elements.append(item_id)
                else:
                    new_item = ItemModel(**item)
                    new_item.save()
                    new_elements[item_id] = new_item.id
                    if move_item:
                        items_to_move.append(new_item)
            item['#status#'] = 'good'
            items_to_process -= 1

        assert items_to_process != PREVIOUS_VALUE, '''Алгоритм сохранения
            лексемы работает неверно. Значение переменной items_to_process не
            меняется, поэтому оно не сможет достигнуть нуля и выход из вечного
            цикла никогда не произойдет.'''

    if post.get('dstEntryId'):
        dst_entry = Entry.objects.get(pk=int(post['dstEntryId']))
        dst_meaning = None
        dst_meaning_id = post.get('dstMeaningId')
        if dst_meaning_id is not None:
            dst_meaning = Meaning.objects.get(pk=int(dst_meaning_id))
        dst_meaning_create = post.get('dstMeaningCreate')
        if dst_meaning_create:
            dst_meaning = Meaning()
            dst_meaning.entry_container = dst_entry
            dst_meaning.save()
        LAST = 400  # Такой порядковый номер, чтобы элемент оказался
        # последним в списке однородных элементов.

        for item in items_to_move:
            if isinstance(item, Example):
                item.meaning = dst_meaning
                item.entry = dst_entry
            elif isinstance(item, CollocationGroup):
                item.base_meaning = dst_meaning
            elif isinstance(item, Meaning):
                item.parent_meaning = None
                item.collogroup_container = None
                item.entry_container = dst_entry
            item.order = LAST
            item.save()

    to_destroy = post['toDestroy']
    for model_name in to_destroy:
        normalized_model_name = {
            'Greq': 'GreekEquivalentForExample',
            'Collogroup': 'CollocationGroup',
            'Orthvar': 'OrthographicVariant',
            'Context': 'MeaningContext'
        }.get(model_name, model_name)
        model = apps.get_model('dictionary', normalized_model_name)
        for item_id in to_destroy[model_name]:
            try:
                item = model.objects.get(pk=item_id)
            except model.DoesNotExist:
                pass
            else:
                item.delete()
