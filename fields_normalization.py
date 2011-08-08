# -*- coding: utf-8 -*-
from django.core.management import setup_environ
from slavdict import settings
setup_environ(settings)

from dictionary.models import Entry

elist = Entry.objects.filter(antconc_query__icontains=u'&lt;')
print u'В запросах для АнтКонка: [ &lt; ] --> [ < ]'
for e in elist:
    s1, s2 = e.antconc_query.split(u'&lt;')
    e.antconc_query = u'%s<%s' % (s1, s2)
    e.save(without_mtime=True)
    print e.pk,

print
