"""Sound files whose basename *is* a known alias, placed in the folder of their nearest sibling.

Measured 2026-10-16: in MWIII 6,484 of 10,354 resolved `dx_sp_/dx_cp_/dx_zm_/dx_mp_` aliases are
exactly the basename of a resolved sound file (63%), BO6 1,672 of 3,443 (49%). So every alias whose
file is still unnamed implies a head: the alias, placed in the folder(s) of the resolved files that
share its longest token prefix (>= MIN_TOKENS, at most MAX_DIRS folders), spelled for the target.
The target's own tails (`stt2_<GAME>.ends.txt`) complete it.

    python contrib/alias_to_file_placed.py <GAME>  -> contrib/out/atf_<GAME>.stems.txt + plans/atf_<GAME>.txt
    bin/windows/confirm_plan plans/atf_<GAME>.txt --game <GAME>

Seeds: every resolved/confirmed alias in any modern title; folders from every title's resolved files.
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
DOTTED = {"MODWAR22", "YAMYAMOK"}
MIN_TOKENS, MAX_TOKENS, MAX_DIRS = 2, 8, 20
ALIAS = re.compile(r"^[a-z0-9_]{6,120}$")


def main():
    game = sys.argv[1].upper()
    an = ROOT / "state" / "an"
    dirs_by_prefix = defaultdict(set)
    have = set()
    for g in MODERN:
        for line in (an / f"{g}_sound_asset.named").open(encoding="utf-8"):
            n = line.strip()
            m = TAIL.search(n)
            if not m:
                continue
            d, _, base = n[:m.start()].replace("/", ".").rpartition(".")
            if not d:
                continue
            have.add(base)
            t = base.split("_")
            for k in range(MIN_TOKENS, min(MAX_TOKENS, len(t)) + 1):
                dirs_by_prefix["_".join(t[:k])].add(d)
    aliases = set()
    for p in [an / f"{g}_sound_alias.named" for g in MODERN] + list((ROOT / "findings").rglob("sound_alias*.txt")):
        for line in p.open(encoding="utf-8", errors="replace"):
            line = line.strip().lower()
            a = line.partition(",")[2] if "," in line else line
            if ALIAS.match(a) and a not in have:
                aliases.add(a)
    stems = set()
    for a in aliases:
        t = a.split("_")
        for k in range(min(MAX_TOKENS, len(t)), MIN_TOKENS - 1, -1):
            ds = dirs_by_prefix.get("_".join(t[:k]))
            if ds and len(ds) <= MAX_DIRS:
                for d in ds:
                    stems.add(f"{d}.{a}" if game in DOTTED else f"{d.replace('.', '/')}/{a}")
                break
    out = ROOT / "contrib" / "out"
    (out / f"atf_{game}.stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"atf_{game}.txt").write_text(
        f"label: sound files named exactly as a known alias, placed by nearest sibling folder, {game}\n"
        "describe: every resolved modern alias with no same-named file, in the folders of resolved "
        "files sharing its longest token prefix, x the target's tails (contrib/alias_to_file_placed.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/atf_{game}.stems.txt\n"
        f"end: @contrib/out/stt2_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    ends = sum(1 for _ in (out / f"stt2_{game}.ends.txt").open())
    print(f"{game}: {len(aliases):,} aliases without a file -> {len(stems):,} placed heads x {ends} "
          f"= {len(stems) * ends:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
