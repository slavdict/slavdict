import re

from slavdict.dictionary.models import Example

# Примеры, где сохранение заглавных букв принципиально важно.
# Все они в статьях, посвященных отдельным буквам.
exclude_ids = (
    8196, 8197, 8236, 8202,  # А
    8226, 8235, 8227,  # Б
    8229, 8230, 8237, 8231,  # В
    23812, 23813, 23814, 23819,  # Г
    25130, 25128, 25127, 25137,  # Д
    27683,  # Ять
)

r = (
    r'(?:^|(?<=[^'
    r'абвгдеєжѕзийіıклмноѻпрстѹꙋуфхѿцчшщъыьѣюꙗѡѽѧѯѱѳѵ'
    r'АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУꙊФХѾЦЧШЩЪЫЬѢЮꙖѠѼѦѮѰѲѴ~'
    r"\^'`"
    r']))'
    r'([АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩЪЫЬѢЮꙖѠѼѦѮѰѲѴꙊ])'
)

for ex in Example.objects.exclude(id__in=exclude_ids):
    segments = re.split(r, ex.example)
    if len(segments) > 1:
        print()
        print(ex.example)
        ex.example = ''.join(s if i % 2 == 0 else s.lower()
                              for i, s in enumerate(segments))
        print(ex.example)
        ex.save(without_mtime=True)
