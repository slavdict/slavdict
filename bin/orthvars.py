# -*- coding: utf-8 -*-
from slavdict.dictionary.models import *

with open('orthvars.txt', 'wb') as f:
    for e in Entry.objects.order_by('civil_equivalent'):
        if len(e.orth_vars) > 1:
            ovs = (ov for ov in e.orth_vars)
            txt = u', '.join(ov.idem_ucs for ov in sorted(ovs, key=lambda ov: ov.order))
            txt += u'\n'
            bts = txt.encode('utf-8')
            f.write(bts)

# vim: set ai et sw=4 ts=4:
