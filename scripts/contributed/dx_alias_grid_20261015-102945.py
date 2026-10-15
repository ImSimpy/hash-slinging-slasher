"""Operator dialogue aliases as a grid: every (category, line) code x every speaker code.

Modern operator aliases are `dx_op_<cat>_<line>_<spk>` (`dx_op_bttl_aamo_west`, `dx_op_ping_pesr_chow`)
in all five modern titles, and the line set is largely shared -- every operator asks for ammo
(`bttl_aamo`). BO6 and MW7 carry the aliases but almost none of the dialogue *files*, so
`dx_alias_from_files.py` cannot reach them (0 BO6, 48 MW7). This writes the two lists for the cross
product instead, from every resolved and confirmed alias in any modern title:

    stems = dx_op_<cat>_<line>      (lines seen with >= MIN_LINE speakers)
    ends  = _<spk>

    python scripts/contributed/dx_alias_grid_20261015-102945.py       -> contrib/out/dxg.{stems,ends}.txt + plans/dxg.txt
    bin/windows/confirm_plan plans/dxg.txt --game <GAME>

Spent by: the same codes already crossed; re-run when any title gains dx_op_ aliases or files.
"""
from collections import defaultdict
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

ALIAS = re.compile(r"^dx_op_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)$")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
MIN_LINE = 1


def main():
    speakers_of = defaultdict(set)
    speakers = set()
    for name in modern_names("sound_alias"):
        m = ALIAS.match(name.lower())
        if m:
            speakers_of[(m.group(1), m.group(2))].add(m.group(3))
            speakers.add(m.group(3))
    stems = sorted(f"dx_op_{c}_{l}" for (c, l), s in speakers_of.items() if len(s) >= MIN_LINE)
    ends = sorted("_" + s for s in speakers)
    out = output_dir()
    (out / "dxg.stems.txt").write_text("\n".join(stems) + "\n", encoding="utf-8")
    (out / "dxg.ends.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
    (ROOT / "plans" / "dxg.txt").write_text(
        "label: operator dialogue alias grid, (category, line) x speaker\n"
        f"describe: every dx_op_<cat>_<line> seen with >= {MIN_LINE} speakers x every speaker code, "
        "from all modern titles (scripts/contributed/dx_alias_grid_20261015-102945.py)\n"
        "stem: @contrib/out/dxg.stems.txt\n"
        "end: @contrib/out/dxg.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    print(f"{len(stems):,} lines x {len(ends):,} speakers = {len(stems) * len(ends):,}")


if __name__ == "__main__":
    main()
