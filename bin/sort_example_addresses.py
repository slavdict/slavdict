import re
import sys

def sort_key(line):
    fragment = line.split('\t')[-1]
    fragment = re.sub(r'[\s' '\u00a0\u202f\u2060\u200b]', '', fragment)
    fragment = re.sub(r'[\.,:;\-—–‑\(\)\[\]"«»]', '', fragment)
    return (fragment.lower(), fragment)

lines = sys.stdin.read().split('\n')
lines.sort(key=sort_key)
sys.stdout.write('\n'.join(lines))
