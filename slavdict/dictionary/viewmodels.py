import json

from django.db.utils import OperationalError
from django.db.utils import ProgrammingError

from slavdict.custom_user.models import CustomUser
from slavdict.dictionary import constants
from slavdict.dictionary.models import Entry
from slavdict.dictionary.utils import volume_label

def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',',':'))

def _json_deterministic(x):
    return json.dumps(x, ensure_ascii=False, separators=(',',':'),
                      sort_keys=True)

def _tuple(x):
    return tuple((i['id'], i['name']) for i in x)

def _choices(choices):
    return tuple(
        {'id': id, 'name': name}
        for id, name in choices
    )


def entry_json(id):
    entry = Entry.objects.get(pk=id)
    return _json(entry.forJSON())

EMPTY_STRING_ID_OBJECT = {'id': '', 'name': ''}
NONE_ID_OBJECT = {'id': None, 'name': ''}

try:
    AUTHOR_CHOICES = tuple(
        (user.id, str(user))
        for user in CustomUser.objects.filter(groups__name='authors')
    )
    authors = (
        {'id': 'all',  'name': 'все авторы'},
        {'id': 'none', 'name': 'статьи без автора'},
        {'id': 'few',  'name': 'статьи с неск. авторами'},
    ) + tuple(
        {'id': str(u.id), 'name': str(u)}
        for u in CustomUser.objects.filter(groups__name='authors')
    )
except (OperationalError, ProgrammingError):
    AUTHOR_CHOICES = tuple()
    authors = tuple()

editAuthors = (NONE_ID_OBJECT,) + _choices(AUTHOR_CHOICES)

volumes = (
    {'id': 'all', 'name': 'все тома'},
    {'id': '0', 'name': 'статьи, не вошедшие в тома'},
) + tuple(
    {'id': str(key), 'name': volume_label(key, value)}
    for key, value in constants.VOLUME_LETTERS.items()
)

editVolumes = _choices(constants.VOLUME_CHOICES)

canonical_name = (
    {'id': 'all', 'name': 'все имена'},
    {'id': '1',   'name': 'только канонические'},
    {'id': '0',   'name': 'только неканонические'},
)

genders = (
    {'id': 'all',  'name': 'любой'},
    {'id': 'none', 'name': 'где род не указан'},
) + _choices(constants.GENDER_CHOICES)

editGenders = (EMPTY_STRING_ID_OBJECT,) + _choices(constants.GENDER_CHOICES)

greqSortbase = (
    {'id': 'addr', 'name': 'по адресу иллюстраций'},
)

greqStatuses = ({'id': 'all', 'name': '— любой —'},) \
        + _choices(constants.GREEK_EQ_STATUS)

onyms = (
    {'id': 'all',  'name': 'любой'},
    {'id': 'none', 'name': 'не имя собст.'},
) + _choices([x for x in constants.ONYM_CHOICES if x[0]])

editOnyms = (EMPTY_STRING_ID_OBJECT,) + _choices(constants.ONYM_CHOICES)

editParticiples = (EMPTY_STRING_ID_OBJECT,) + _choices(constants.PARTICIPLE_CHOICES)

pos = (
    {'id': 'all',  'name': 'любая'},
    {'id': 'none', 'name': 'где часть речи не указана'},
) + _choices(constants.PART_OF_SPEECH_CHOICES)

possessive = (
    {'id': 'all', 'name': ''},
    {'id': '1',   'name': 'притяжательные'},
    {'id': '0',   'name': 'непритяжательные'},
)

sortdir = (
    {'id': '+', 'name': 'по возрастанию'},
    {'id': '-', 'name': 'по убыванию'},
)

sortbase = (
    {'id': 'alph', 'name': 'по алфавиту'},
    {'id': 'phla', 'name': 'по алфавиту с инверсией слова'},
    {'id': 't',    'name': 'по времени изменения'},
)

editSubstantivusTypes = ((EMPTY_STRING_ID_OBJECT,) +
        _choices(constants.SUBSTANTIVUS_TYPE_CHOICES))

tantum = (
    {'id': 'all',  'name': 'любое'},
    {'id': 'none', 'name': 'где число не указано'},
) + _choices(constants.TANTUM_CHOICES)

editTantum = (EMPTY_STRING_ID_OBJECT,) + _choices(constants.TANTUM_CHOICES)

statuses = ({'id': 'all', 'name': 'любой'},) \
        + _choices(constants.STATUS_CHOICES)

editStatuses = (EMPTY_STRING_ID_OBJECT,) + _choices(constants.STATUS_CHOICES)


jsonAuthors = _json(authors)
jsonCanonicalName = _json(canonical_name)
jsonGenders = _json(genders)
jsonGreqSortbase = _json(greqSortbase)
jsonGreqStatuses = _json(greqStatuses)
jsonOnyms = _json(onyms)
jsonPos = _json(pos)
jsonPossessive = _json(possessive)
jsonSortbase = _json(sortbase)
jsonSortdir = _json(sortdir)
jsonStatuses = _json(statuses)
jsonTantum = _json(tantum)
jsonVolumes = _json(volumes)

tupleAuthors = _tuple(authors)
tupleCanonicalName = _tuple(canonical_name)
tupleGenders = _tuple(genders)
tupleGreqSortbase = _tuple(greqSortbase)
tupleGreqStatuses = _tuple(greqStatuses)
tupleOnyms = _tuple(onyms)
tuplePos = _tuple(pos)
tuplePossessive = _tuple(possessive)
tupleSortbase = _tuple(sortbase)
tupleSortdir = _tuple(sortdir)
tupleStatuses = _tuple(statuses)
tupleTantum = _tuple(tantum)
tupleVolumes = _tuple(volumes)
