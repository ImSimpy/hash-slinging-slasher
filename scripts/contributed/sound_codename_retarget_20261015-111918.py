"""Modern sound heads with one codename token swapped, re-worn with the target's own tails.

Combines `codename_swap.py` (a `t10/...` head reappearing as `sat/...`) with method 33 (each title
writes its own `<code>.<vol>.<rate>.<lang>` tail): a verbatim codename swap keeps the source tail
and so cannot land in a title whose tails differ. Stems are every known modern sound head with one
codename token swapped (target separator); ends are `stt2_<GAME>.ends.txt`.

    python contrib/sound_codename_retarget.py <GAME>  -> contrib/out/scr_<GAME>.stems.txt + plan
    bin/windows/confirm_plan plans/scr_<GAME>.txt --game <GAME>
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

CODES = ["iw8", "iw9", "jup", "t9", "t10", "sat", "rex", "s4", "s6", "cer"]
TOKEN = re.compile(r"(?<![a-z0-9])(" + "|".join(CODES) + r")(?![a-z0-9])")
DOTTED = {"MODWAR22", "YAMYAMOK"}


def main():
    game = sys.argv[1].upper()
    out = ROOT / "contrib" / "out"
    stems = set()
    for line in (out / f"stt2_{game}.stems.txt").open(encoding="utf-8"):
        h = line.strip()
        for m in TOKEN.finditer(h):
            for c in CODES:
                if c != m.group(1):
                    stems.add(h[:m.start()] + c + h[m.end():])
    (out / f"scr_{game}.stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"scr_{game}.txt").write_text(
        f"label: modern sound heads, one codename swapped, x {game}'s own tails\n"
        "describe: every known modern sound head with one codename token (iw9/jup/t10/sat/rex/...) "
        "swapped, x the target's measured tails (contrib/sound_codename_retarget.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/scr_{game}.stems.txt\n"
        f"end: @contrib/out/stt2_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    ends = sum(1 for _ in (out / f"stt2_{game}.ends.txt").open())
    print(f"{game}: {len(stems):,} heads x {ends} = {len(stems) * ends:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
