from slavdict.dictionary.models import *

with open('headwords_wtitles.txt', 'w') as f:
    for e in Entry.objects.order_by('civil_equivalent'):
        ovs = [ov for ov in sorted((ov for ov in e.orth_vars), key=lambda ov: ov.order)]
        if len(ovs) > 0:
            ov = ovs[0]
            if ov.idem != ov.idem.lower() or '~' in ov.idem:
                bts = ov.idem_ucs + '\n'
                f.write(bts)

# vim: set ai et sw=4 ts=4:
