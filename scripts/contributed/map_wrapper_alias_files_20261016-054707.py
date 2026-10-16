"""Files behind map-wrapped aliases: strip the map wrapper, wear the file prefix, place by sibling.

BO7's link table (2026-10-16) shows map aliases wrapping a shared core:
    amb_emt_sat_barrel_light_buzz_soft_06_lp -> iw9/amb/amb_emitters_iw9/lights/emt_iw9_light_buzz_soft_06_lp
    rtl_sat_roji_ceramic_potted_plant_large  -> jup/dst/dst_ceramic_potted_plant_large_01..06
For every `(amb_emt|rtl|...)_<code>_<map>_<core>` alias in any modern title the core is offered as
`emt_<core>`, `emt_<code>_<core>` (emitters) or `dst_<core>` (destruction), bare and with takes,
in the folders of resolved files whose basename shares the longest token prefix with it.

    python contrib/map_wrapper_alias_files.py <GAME>  -> contrib/out/mwa_<GAME>.stems.txt + plan
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
DOTTED = {"MODWAR22", "YAMYAMOK"}
TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
WRAP = re.compile(r"^(amb_emt|amb|rtl|dst|emt)_(sat|t10|jup|iw9|rex|s6|iw8)_([a-z0-9]+)_(.+)$")
PREFIX = {"amb_emt": ["emt"], "amb": ["amb", "emt"], "emt": ["emt"], "rtl": ["dst"], "dst": ["dst"]}
MAX_DIRS = 10


def main():
    game = sys.argv[1].upper()
    sep = "." if game in DOTTED else "/"
    dirs_by_prefix = defaultdict(set)
    for g in MODERN:
        for line in (ROOT / "state" / "an" / f"{g}_sound_asset.named").open(encoding="utf-8"):
            n = line.strip()
            m = TAIL.search(n)
            if not m:
                continue
            d, _, base = n[:m.start()].replace("/", ".").rpartition(".")
            t = base.split("_")
            for k in range(2, min(6, len(t)) + 1):
                dirs_by_prefix["_".join(t[:k])].add(d)
    bases = set()
    for g in MODERN:
        for line in (ROOT / "state" / "an" / f"{g}_sound_alias.named").open(encoding="utf-8"):
            m = WRAP.match(line.strip())
            if not m:
                continue
            kind, code, _map, core = m.groups()
            core = re.sub(r"_\d{2}$", "", core)
            for p in PREFIX[kind]:
                bases.add(f"{p}_{core}")
                bases.add(f"{p}_{code}_{core}")
    stems = set()
    for b in bases:
        t = b.split("_")
        for k in range(min(6, len(t)), 1, -1):
            ds = dirs_by_prefix.get("_".join(t[:k]))
            if ds and len(ds) <= MAX_DIRS:
                for d in ds:
                    dd = d if sep == "." else d.replace(".", "/")
                    stems.add(f"{dd}{sep}{b}")
                break
    out = ROOT / "contrib" / "out"
    tails = [l.strip() for l in (out / f"stt2_{game}.ends.txt").open() if l.strip()]
    ends = [s + t for s in [""] + [f"_{i:02d}" for i in range(1, 13)] + ["_lp"] for t in tails]
    (out / f"mwa_{game}.stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    (out / f"mwa_{game}.ends.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"mwa_{game}.txt").write_text(
        f"label: files behind map-wrapped aliases (amb_emt/rtl_<code>_<map>_<core>), {game}\n"
        "describe: alias core with the file prefix (emt_/dst_), placed by longest-prefix sibling "
        "folders, x takes x the target's tails (contrib/map_wrapper_alias_files.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/mwa_{game}.stems.txt\n"
        f"end: @contrib/out/mwa_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    print(f"{game}: {len(bases):,} cores -> {len(stems):,} placed heads x {len(ends):,} ends", file=sys.stderr)


if __name__ == "__main__":
    main()
