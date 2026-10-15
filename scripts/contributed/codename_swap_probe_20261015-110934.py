"""How often does a resolved modern name reappear in another title with its codename token swapped?
(analysis helper, not a method)

Tokens: iw9 (MWII), jup (MWIII), t10 (BO6), sat (BO7), rex (MW7), plus the s4/s6/t9/iw8 strata.
For each pool, takes every resolved name in each title, swaps each codename token for each other
one, and counts how many land on a name resolved in some *other* title -- the reproduction rate a
swap generator would have.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from generator_inputs import all_known_names, modern_game, modern_names, named_names, output_dir, sound_lists


CODES = ["iw8", "iw9", "jup", "t9", "t10", "sat", "rex", "s4", "s6", "cer", "wz"]
TOKEN = re.compile(r"(?<![a-z0-9])(" + "|".join(CODES) + r")(?![a-z0-9])")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]

for pool in ("image", "material", "xanim", "sound_alias"):
    named = {g: named_names(g,pool) for g in MODERN}
    allnamed = set().union(*named.values())
    for g in MODERN:
        hits = cands = 0
        for n in named[g]:
            for m in TOKEN.finditer(n):
                for c in CODES:
                    if c == m.group(1):
                        continue
                    s = n[:m.start()] + c + n[m.end():]
                    cands += 1
                    if s in allnamed and s not in named[g]:
                        hits += 1
        print(f"{pool:11s} {g}: {cands:,} swaps, {hits:,} land on a name resolved elsewhere")
