import sys
from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import ulysses_unicode

ulysses_compiled_conversion = compile_conversion(ulysses_unicode.conversion)

def ulysconv(text):
    return convert(text, ulysses_compiled_conversion)

from dictionary.models import GreekEquivalentForExample
l = GreekEquivalentForExample.objects.all()
length = len(l)

for n, ge in enumerate(l):
    if ge.text:
        ge.unitext = ulysconv(ge.text)
        ge.save(without_mtime=True)
        sys.stdout.write('%s%%\r' % int(n * 100.0 / length))
