"""Profile the format tails of modern sound-file names, per game (analysis helper, not a method).

Slashed games (BO6/BO7/MW7) spell `dir/dir/base.ext`; dotted games (MWII/MWIII) spell
`dir.dir.base.code.vol.rate.all`. Prints the top tails per game and how many basenames are shared
between a slashed and a dotted game, so a format-translating transfer can be sized before it is built.
"""
from collections import Counter
from pathlib import Path
import re
import sys

AN = Path("state/an")
DOTTED_TAIL = re.compile(r"\.([a-z]{1,4})\.(\d{1,3})\.(\d{4,6})\.all$")


def split(game, name):
    m = DOTTED_TAIL.search(name)
    if not m:
        return None
    sep = "/" if "/" in name[:m.start()] else "."
    return name[:m.start()].replace("/", "."), sep + " " + m.group(0)[1:]


games = sys.argv[1:] or ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
heads = {}
for g in games:
    tails = Counter()
    hs = set()
    bad = 0
    for line in (AN / f"{g}_sound_asset.named").open(encoding="utf-8"):
        n = line.strip()
        if not n:
            continue
        s = split(g, n)
        if s is None:
            bad += 1
            continue
        hs.add(s[0])
        tails[s[1]] += 1
    heads[g] = hs
    print(f"== {g}: {len(hs)} heads, {bad} unparsed; top tails:",
          ", ".join(f"{t} {c}" for t, c in tails.most_common(12)))
for a in games:
    for b in games:
        if a < b:
            print(f"shared heads {a} & {b}: {len(heads[a] & heads[b])}")
