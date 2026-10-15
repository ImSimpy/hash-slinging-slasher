"""Operator-dialogue sound aliases derived from the dialogue *files* they play.

Modern operator files are `dx_op_<spk>_<cat>_<spk2>_<line>_<text>_<variant>` (e.g.
`dx_op_shrd_ping_shrd_plah_largecaliberhere_ogr2`); the aliases that play them are short codes,
`dx_op_<cat>_<line>_<spk>` (e.g. `dx_op_ping_pila_klau`). So every resolved dialogue file implies a
handful of alias spellings. Fed by any batch of new dialogue files -- 2026-10-15 added 89 K MWII
operator files (method 33), none of whose aliases had been offered.

    python scripts/contributed/dx_alias_from_files_20261015-110216.py --measure      how many resolved aliases this reproduces
    python scripts/contributed/dx_alias_from_files_20261015-110216.py | confirm_list - --game <GAME>

Reads configured, verified public tables and current submissions/findings through generator_inputs.
"""
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

BASE = re.compile(r"(?:^|[./])(dx_op_[a-z0-9_]+?)\.[a-z]{1,4}\.\d")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]


def file_bases():
    for line in modern_names("sound_asset"):
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


OTHER = re.compile(r"(?:^|[./])(dx_(?:mp|zm|sp|cp|br)_[a-z0-9_]+?)\.[a-z]{1,4}\.\d")


def other_aliases():
    """Non-operator dialogue: the alias is the file basename minus its text token (and variant).
    `dx_mp_gnsc_actn_dog1_njct_isthatatreat...` -> `dx_mp_gnsc_actn_dog1_njct`; reproduces about
    half the resolved non-op dx aliases in MWIII, BO6 and BO7 (2026-10-15)."""
    for line in modern_names("sound_asset"):
        m = OTHER.search(line.lower())
        if m:
            t = m.group(1).split("_")
            for k in (1, 2):
                if len(t) - k >= 4:
                    yield "_".join(t[:-k])


def main():
    cands = set()
    for b in file_bases():
        cands.update(aliases(b))
    cands.update(other_aliases())
    if "--measure" in sys.argv:
        for g in MODERN:
            named = {n for n in named_names(g, "sound_alias") if n.startswith("dx_op_")}
            print(f"{g}: {len(named & cands):,} of {len(named):,} resolved dx_op_ aliases reproduced",
                  file=sys.stderr)
        print(f"{len(cands):,} candidates", file=sys.stderr)
        return
    sys.stdout.write("\n".join(sorted(cands)) + "\n")


if __name__ == "__main__":
    main()
