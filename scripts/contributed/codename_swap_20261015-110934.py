"""Every known name with one game-codename token swapped for each other codename.

Modern titles stamp their codename into asset names (`cm_sat_...`, `c_t10_...`, `mtl_jup_...`,
`iw9_...`, `rex/...`). Measured 2026-10-15 (`contrib/codename_swap_probe.py`): swapping one such
token in a resolved name lands on a name resolved in another title 0.1-0.5% of the time across
image, material, xanim and alias -- weak per candidate, but the candidates are few.

    python contrib/codename_swap.py | confirm_list - --game <GAME>

Seeds: contrib/out/every_name.txt (every_game_transfer output) -- tables, submissions, findings.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

CODES = ["iw8", "iw9", "jup", "t9", "t10", "sat", "rex", "s4", "s6", "cer", "wz"]
TOKEN = re.compile(r"(?<![a-z0-9])(" + "|".join(CODES) + r")(?![a-z0-9])")


def main():
    seen = set()
    out = sys.stdout
    for line in (ROOT / "contrib" / "out" / "every_name.txt").open(encoding="utf-8", errors="replace"):
        n = line.strip().lower()
        if not n or " " in n or "\\" in n:
            continue
        for m in TOKEN.finditer(n):
            for c in CODES:
                if c != m.group(1):
                    s = n[:m.start()] + c + n[m.end():]
                    if s not in seen:
                        seen.add(s)
                        out.write(s + "\n")
    print(f"{len(seen):,} swapped names", file=sys.stderr)


if __name__ == "__main__":
    main()
