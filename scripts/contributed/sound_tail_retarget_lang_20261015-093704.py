"""Every known modern sound-file head, re-worn with the target game's own format tails --
the language variant: the last tail field may be any language (`english`, `english_safe`, ...)
rather than only `all`, so operator pings and other dialogue shared between titles are carried.

Modern sound files are spelled `<dirs><sep><basename>.<code>.<vol>.<rate>.all`. The head (dirs +
basename) is shared widely between titles -- measured 2026-10-15 on resolved names: BO6 & MWIII
share 56,904 heads, BO6 & MWII 39,262, MWII & MW7 14,597 -- but each title writes its own tail:
MWII `ln.75.48000.all`, BO6/BO7 `tnn.75.48000.all`, MW7 `vnn`/`qnn`, MWIII both `ln` and `lnn`.
So a verbatim cross-game transfer (`every_game_transfer`) cannot reach a head that is known in one
title and unnamed in another: the tail differs. This writes the plan lists for that cross product:

    stems = every head known in any modern title (resolved names + every sound-shaped name on disk),
            spelled with the target's separator (`.` for MWII/MWIII, `/` for BO6/BO7/MW7)
    ends  = every tail the target is measured to carry at least MIN_TAIL times

    python contrib/sound_tail_retarget.py <GAME>   -> contrib/out/stt_<GAME>.{stems,ends}.txt + plan
    bin/windows/confirm_plan plans/stt_<GAME>.txt --game <GAME>

Needs state/an/<GAME>_sound_asset.named (scripts/contributed/_dump_named_*.py, run with
python scripts/export_named.py; contrib/out/every_name.txt is optional).
Spent by: a target already offered the heads as they stand; re-run when any title gains sound names.
"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

TAIL = re.compile(r"\.([a-z]{1,4})\.(\d{1,3})\.(\d{4,6})\.([a-z_]+)$")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
DOTTED = {"MODWAR22", "YAMYAMOK"}
MIN_TAIL = 3


def heads_and_tails(lines):
    for line in lines:
        name = line.strip().lower()
        m = TAIL.search(name)
        if m and m.start() > 0:
            yield name[:m.start()], name[m.start() + 1:]


def main():
    if len(sys.argv) != 2 or sys.argv[1].upper() not in {"MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"}:
        raise SystemExit("Supply one supported modern game")
    game = sys.argv[1].upper()
    an = ROOT / "state" / "an"
    out = ROOT / "contrib" / "out"
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "plans").mkdir(parents=True, exist_ok=True)
    heads = set()
    tails = Counter()
    for g in MODERN:
        path = an / f"{g}_sound_asset.named"
        for head, tail in heads_and_tails(path.open(encoding="utf-8")):
            heads.add(head.replace("/", "."))
            if g == game:
                tails[tail] += 1
    every = out / "every_name.txt"
    if every.exists():
        for head, _ in heads_and_tails(every.open(encoding="utf-8", errors="replace")):
            if " " not in head and "\\" not in head:
                heads.add(head.replace("/", "."))

    # A dotted title separates directories with `.`, so the dotted spelling is the head as is.
    # A slashed one needs every directory dot back to `/`, keeping the basename intact; the
    # basename is the last dot-separated piece because modern basenames carry no dots.
    if game in DOTTED:
        spelled = sorted(heads)
    else:
        spelled = sorted({h.rsplit(".", 1)[0].replace(".", "/") + "/" + h.rsplit(".", 1)[1]
                          if "." in h else h for h in heads})
    ends = ["." + t for t, c in tails.most_common() if c >= MIN_TAIL]

    (out / f"stt2_{game}.stems.txt").write_text("\n".join(spelled) + "\n", encoding="utf-8")
    (out / f"stt2_{game}.ends.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
    plan = ROOT / "plans" / f"stt2_{game}.txt"
    plan.write_text(
        f"label: modern sound heads incl. dialogue re-worn with {game}'s own format tails\n"
        f"describe: every modern sound-file head known in any title x every tail {game} carries "
        f">= {MIN_TAIL} times (contrib/sound_tail_retarget.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/stt2_{game}.stems.txt\n"
        f"end: @contrib/out/stt2_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    print(f"{game}: {len(spelled):,} heads x {len(ends)} tails = {len(spelled) * len(ends):,}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
