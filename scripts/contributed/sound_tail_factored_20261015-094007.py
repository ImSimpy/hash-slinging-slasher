"""Modern sound heads x the *factored* tail space: every code x volume x rate x language.

`sound_tail_retarget.py` offers each target only the whole tails it is measured to carry. But a
tail is four independent fields -- `<code>.<vol>.<rate>.<lang>` -- and a combination nobody has
resolved yet in the target (say MW7's `qnn` at volume 20, or a 32000 rate on a code only seen at
48000) is unreachable that way. This multiplies the fields instead, each field taken from every
modern title (a field value needs >= MIN_FIELD sightings anywhere), so the engine tries every
head with every tail the format can express.

    python contrib/sound_tail_factored.py <GAME>  -> contrib/out/stf_<GAME>.{stems,ends}.txt + plan
    bin/windows/confirm_plan plans/stf_<GAME>.txt --game <GAME> --size    (check the cost first)

Needs state/an/<GAME>_sound_asset.named for all five titles and contrib/out/every_name.txt.
Spent by: the same heads already offered; re-run when heads grow or a new field value appears.
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
MIN_FIELD = 20


def main():
    game = sys.argv[1].upper()
    an = ROOT / "state" / "an"
    out = ROOT / "contrib" / "out"
    heads = set()
    fields = [Counter(), Counter(), Counter(), Counter()]
    sources = [an / f"{g}_sound_asset.named" for g in MODERN] + [out / "every_name.txt"]
    for path in sources:
        for line in path.open(encoding="utf-8", errors="replace"):
            name = line.strip().lower()
            m = TAIL.search(name)
            if not m or m.start() == 0 or " " in name or "\\" in name:
                continue
            heads.add(name[:m.start()].replace("/", "."))
            for i in range(4):
                fields[i][m.group(i + 1)] += 1

    if game in DOTTED:
        spelled = sorted(heads)
    else:
        spelled = sorted({h.rsplit(".", 1)[0].replace(".", "/") + "/" + h.rsplit(".", 1)[1]
                          if "." in h else h for h in heads})
    keep = [sorted(v for v, c in f.items() if c >= MIN_FIELD) for f in fields]
    ends = [f".{a}.{b}.{c}.{d}" for a in keep[0] for b in keep[1] for c in keep[2] for d in keep[3]]

    (out / f"stf_{game}.stems.txt").write_text("\n".join(spelled) + "\n", encoding="utf-8")
    (out / f"stf_{game}.ends.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"stf_{game}.txt").write_text(
        f"label: modern sound heads x factored tails (code x vol x rate x lang) for {game}\n"
        f"describe: every modern sound head x every combination of tail fields seen >= {MIN_FIELD} "
        f"times in any modern title (contrib/sound_tail_factored.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/stf_{game}.stems.txt\n"
        f"end: @contrib/out/stf_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    print(f"{game}: {len(spelled):,} heads x {len(ends):,} tails "
          f"({' x '.join(str(len(k)) for k in keep)}) = {len(spelled) * len(ends):,}", file=sys.stderr)
    for k in keep:
        print("   ", " ".join(k), file=sys.stderr)


if __name__ == "__main__":
    main()
