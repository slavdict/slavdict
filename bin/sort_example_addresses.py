import re
import sys

def sort_key(line):
    fragment = line.split(u'\t')[-1]
    fragment = re.sub(ur'[\s\u00a0\u202f\u2060\u200b]', u'', fragment)
    fragment = re.sub(ur'[\.,:;\-—–‑"«»]', u'', fragment)
    return (fragment.lower(), fragment)

lines = sys.stdin.read().decode('utf-8').split('\n')
lines.sort(key=sort_key)
sys.stdout.write(u'\n'.join(lines).encode('utf-8'))
