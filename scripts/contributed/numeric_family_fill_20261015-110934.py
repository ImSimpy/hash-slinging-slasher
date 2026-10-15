"""Fill the gaps in every numbered family of every known modern name.

A family is a name with one digit run replaced by a hole, keyed by the run's padding width:
`ui_emblem_#`, `emt_bird_crow_caw_##.snn.75.48000.all`, `dx_zm_..._km##_...`. For each family seen
with >= MIN_SEEN members, every value from 0 to max(seen)+HEADROOM at the same width is offered.
Seeded from verified public tables and current submissions/findings, so the 2026-10-15 dialogue batches
(140 K names, many numbered takes) seed families no earlier pass had.

    python scripts/contributed/numeric_family_fill_20261015-110934.py | confirm_list - --game <GAME>
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from generator_inputs import all_known_names, modern_game, modern_names, named_names, output_dir, sound_lists

RUN = re.compile(r"\d+")
MIN_SEEN = 2
HEADROOM = 3
MAX_VALUE = 999
SKIP_TAIL = re.compile(r"\.\d{1,3}\.\d{4,6}\.[a-z_]+$")   # never vary a sound format tail


def main():
    families = defaultdict(set)
    for line in all_known_names():
        n = line.strip().lower()
        if not n or " " in n or len(n) > 200:
            continue
        tail = SKIP_TAIL.search(n)
        limit = tail.start() if tail else len(n)
        for m in RUN.finditer(n):
            if m.end() > limit or len(m.group()) > 3:
                continue
            width = len(m.group()) if m.group().startswith("0") else 0
            families[(n[:m.start()], n[m.end():], width)].add(int(m.group()))
    seen = set()
    out = sys.stdout
    for (pre, post, width), values in families.items():
        if len(values) < MIN_SEEN:
            continue
        top = min(max(values) + HEADROOM, MAX_VALUE)
        for v in range(0, top + 1):
            if v in values:
                continue
            digits = str(v).zfill(width) if width else str(v)
            s = pre + digits + post
            if s not in seen:
                seen.add(s)
                out.write(s + "\n")
    print(f"{len(families):,} families -> {len(seen):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
