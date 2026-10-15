"""Operator dialogue heads with their delivery-variant token swapped, x the factored tails.

Modern operator lines end their basename in a variant token: measured 2026-10-15 on resolved
names, MWIII carries `ogr2` 16,194 / `opg2` 15,626 / `opg3` 14,759 -- the same lines three ways --
while BO7 carries `opg2`/`opg3` and no `ogr2`, and MW7 only 1,410 dialogue names at all against
BO7's 66,544. So every dialogue head is re-offered with each variant token, under every tail the
format can express (the `stf_<GAME>.ends.txt` list `sound_tail_factored.py` writes).

    python contrib/sound_tail_factored.py <GAME>       (writes the ends list first)
    python contrib/sound_dx_variant_swap.py <GAME>     -> contrib/out/sdx_<GAME>.stems.txt + plan
    bin/windows/confirm_plan plans/sdx_<GAME>.txt --game <GAME>

Spent by: the same dialogue heads already offered; re-run when any title gains dx_ names.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

VARIANT = re.compile(r"^(.*[./]dx_[a-z0-9_]+_)(o[gp][rg][0-9])$")
TOKENS = ["ogr1", "ogr2", "ogr3", "opg1", "opg2", "opg3", "opg4"]


def main():
    if len(sys.argv) != 2 or sys.argv[1].upper() not in {"MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"}:
        raise SystemExit("Supply one supported modern game")
    game = sys.argv[1].upper()
    out = ROOT / "contrib" / "out"
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "plans").mkdir(parents=True, exist_ok=True)
    if not (out / f"stf_{game}.ends.txt").is_file():
        raise SystemExit("Run sound_tail_factored for this game first")
    stems = set()
    for head in (out / f"stf_{game}.stems.txt").open(encoding="utf-8"):
        m = VARIANT.match(head.strip())
        if m:
            for t in TOKENS:
                stems.add(m.group(1) + t)
    (out / f"sdx_{game}.stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"sdx_{game}.txt").write_text(
        f"label: operator dialogue heads with swapped variant token x factored tails for {game}\n"
        f"describe: every dx_ head ending ogrN/opgN re-offered with {' '.join(TOKENS)}, x every "
        f"factored tail (contrib/sound_dx_variant_swap.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/sdx_{game}.stems.txt\n"
        f"end: @contrib/out/stf_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    ends = sum(1 for _ in (out / f"stf_{game}.ends.txt").open())
    print(f"{game}: {len(stems):,} stems x {ends:,} tails = {len(stems) * ends:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
