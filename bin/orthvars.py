from slavdict.dictionary.models import *

with open('orthvars.txt', 'w') as f:
    for e in Entry.objects.order_by('civil_equivalent'):
        if len(e.orth_vars) > 1:
            ovs = (ov for ov in e.orth_vars)
            txt = ', '.join(ov.idem_ucs for ov in sorted(ovs, key=lambda ov: ov.order))
            txt += '\n'
            f.write(txt)

# vim: set ai et sw=4 ts=4:
