"""How often do different operators share the spoken-text token for one line code? (analysis helper)

File basenames: dx_op_<fspk>_<cat>_<aspk>_<line>_<text>_<variant>. For each (cat, line), count the
distinct <text> values across speakers. If one text dominates, a known alias whose file is unnamed
can borrow it.
"""
from collections import Counter, defaultdict
from pathlib import Path
import re

BASE = re.compile(r"(?:^|[./])dx_op_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)_(o[gp][rg][0-9])\.")
texts = defaultdict(Counter)
spk_map = defaultdict(Counter)
for g in ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]:
    for line in Path(f"state/an/{g}_sound_asset.named").open(encoding="utf-8"):
        m = BASE.search(line)
        if m:
            fspk, cat, aspk, code, text, var = m.groups()
            texts[(cat, code)][text] += 1
            spk_map[aspk][fspk] += 1
lines = len(texts)
shared = sum(1 for c in texts.values() if len(c) == 1 and sum(c.values()) > 1)
top_share = sum(c.most_common(1)[0][1] for c in texts.values()) / max(1, sum(sum(c.values()) for c in texts.values()))
print(f"{lines:,} (cat,line) codes; {shared:,} have exactly one text over >1 files; "
      f"top text covers {top_share:.1%} of files")
print("distinct texts per line (median-ish):", sorted(len(c) for c in texts.values())[lines // 2])
print("alias speaker -> file speaker codes, ambiguous:", sum(1 for c in spk_map.values() if len(c) > 1),
      "of", len(spk_map))
