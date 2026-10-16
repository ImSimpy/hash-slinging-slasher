"""Bullet whiz-by files built from the whiz aliases that play them.

MW7's link table (2026-10-16): 539 `<cls>[_sub|_super]_whiz_<d1>_<d2>_<in|out>` aliases play files
`core/prj/whizby/<cls>/<cls>_whiz_<d1>_<d2>_<in|out>_<NN>.<tail>` (533 resolved, ~370 not). Every
alias in any modern title is turned into its file family: class folder as is and with `sup`/`lrg`/
`sub` stripped, file stem with and without the sub/super token, takes 01..16, and every tail any
modern title's resolved whiz-by file carries.

    python contrib/whizby_from_aliases.py <GAME> | confirm_list - --game <GAME>
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
ALIAS = re.compile(r"^([a-z0-9]+?)(?:_(sub|super))?_whiz((?:_[a-z0-9]+)*)$")
FILE = re.compile(r"[./]whizby[./][a-z0-9_]+[./][a-z0-9_]+_\d{2}(\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+)$")


def main():
    game = sys.argv[1].upper()
    sep = "." if game in ("MODWAR22", "YAMYAMOK") else "/"
    tails, combos = set(), set()
    for g in MODERN:
        for line in (ROOT / "state" / "an" / f"{g}_sound_asset.named").open(encoding="utf-8"):
            m = FILE.search(line.strip())
            if m:
                tails.add(m.group(1))
        for line in (ROOT / "state" / "an" / f"{g}_sound_alias.named").open(encoding="utf-8"):
            m = ALIAS.match(line.strip())
            if m:
                combos.add(m.groups())
    out = sys.stdout
    seen = set()
    for cls, sub, rest in combos:
        folders = {cls, re.sub(r"(sup|lrg|sub)$", "", cls)}
        stems = {f"{cls}_whiz{rest}", re.sub(r"(sup|lrg|sub)$", "", cls) + f"_whiz{rest}"}
        if sub:
            stems |= {f"{cls}_{sub}_whiz{rest}"}
        for f in folders:
            for s in stems:
                for k in range(1, 17):
                    for t in tails:
                        c = f"core{sep}prj{sep}whizby{sep}{f}{sep}{s}_{k:02d}{t}"
                        if c not in seen:
                            seen.add(c)
                            out.write(c + "\n")
    print(f"{game}: {len(combos)} whiz aliases, {len(tails)} tails -> {len(seen):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
