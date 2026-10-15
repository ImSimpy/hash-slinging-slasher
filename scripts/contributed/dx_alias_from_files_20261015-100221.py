"""Operator-dialogue sound aliases derived from the dialogue *files* they play.

Modern operator files are `dx_op_<spk>_<cat>_<spk2>_<line>_<text>_<variant>` (e.g.
`dx_op_shrd_ping_shrd_plah_largecaliberhere_ogr2`); the aliases that play them are short codes,
`dx_op_<cat>_<line>_<spk>` (e.g. `dx_op_ping_pila_klau`). So every resolved dialogue file implies a
handful of alias spellings. Fed by any batch of new dialogue files -- 2026-10-15 added 89 K MWII
operator files (method 33), none of whose aliases had been offered.

    python contrib/dx_alias_from_files.py --measure      how many resolved aliases this reproduces
    python contrib/dx_alias_from_files.py | confirm_list - --game <GAME>

Reads every modern `state/an/*_sound_asset.named` plus today's findings.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

BASE = re.compile(r"(?:^|[./])(dx_op_[a-z0-9_]+?)\.[a-z]{1,4}\.\d")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]


def file_bases():
    paths = [ROOT / "state" / "an" / f"{g}_sound_asset.named" for g in MODERN]
    paths += list((ROOT / "findings").rglob("sound_asset*.txt"))
    for p in paths:
        for line in p.open(encoding="utf-8", errors="replace"):
            m = BASE.search(line.lower())
            if m:
                yield m.group(1)


def aliases(base):
    t = base.split("_")[2:]          # drop dx, op
    if len(t) < 4:
        return
    spk, cat, spk2, line = t[0], t[1], t[2], t[3]
    for s in {spk, spk2}:
        yield f"dx_op_{cat}_{line}_{s}"
        yield f"dx_op_{cat}_{s}_{line}"
        yield f"dx_op_{s}_{cat}_{line}"
    yield f"dx_op_{cat}_{spk2}_{line}_{spk}"
    yield f"dx_op_{spk}_{cat}_{spk2}_{line}"


def main():
    cands = set()
    for b in file_bases():
        cands.update(aliases(b))
    if "--measure" in sys.argv:
        for g in MODERN:
            named = {l.strip() for l in (ROOT / "state" / "an" / f"{g}_sound_alias.named")
                     .open(encoding="utf-8") if l.startswith("dx_op_")}
            print(f"{g}: {len(named & cands):,} of {len(named):,} resolved dx_op_ aliases reproduced",
                  file=sys.stderr)
        print(f"{len(cands):,} candidates", file=sys.stderr)
        return
    sys.stdout.write("\n".join(sorted(cands)) + "\n")


if __name__ == "__main__":
    main()
