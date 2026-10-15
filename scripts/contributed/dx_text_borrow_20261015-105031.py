"""Operator dialogue files built from a known alias + the text other operators speak for that line.

File basenames are `dx_op_<fspk>_<cat>_<aspk>_<line>_<text>_<variant>`, where <text> is the first
20 characters of the spoken line. Measured 2026-10-15 over every resolved modern dialogue file:
782 (cat, line) codes, a median of 5 distinct texts each, and the most common text for a line
covering 46.6% of its files -- generic callouts ("needpistolrounds") are said the same way by many
operators. Alias speaker -> file speaker code is unambiguous (95 of 95).

So for every resolved alias `dx_op_<cat>_<line>_<aspk>` (any title) whose speaker has a known folder
and file code, this emits that speaker's file head with every text any operator uses for the line,
in every variant, spelled for the target; the target's captured sound names supply measured format tails.

    python scripts/contributed/dx_text_borrow_20261015-105031.py <GAME>    -> contrib/out/dtb_<GAME>.stems.txt + plans/dtb_<GAME>.txt
    bin/windows/confirm_plan plans/dtb_<GAME>.txt --game <GAME>

Spent by: the same aliases x texts; re-run when aliases, speakers or line texts grow.
"""
from collections import defaultdict
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

FILE = re.compile(r"^(?P<dir>.*)[./]dx_op_(?P<fspk>[a-z0-9]+)_(?P<cat>[a-z0-9]+)_(?P<aspk>[a-z0-9]+)_"
                  r"(?P<line>[a-z0-9]+)_(?P<text>[a-z0-9]+)_(?P<var>o[gp][rg][0-9])\.")
ALIAS = re.compile(r"^dx_op_([a-z0-9]+)_([a-z0-9]+)_([a-z0-9]+)$")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
DOTTED = {"MODWAR22", "YAMYAMOK"}
VARIANTS = ["ogr2", "opg2", "opg3"]


def lines_of(paths):
    for p in paths:
        for line in p.open(encoding="utf-8", errors="replace"):
            line = line.rstrip("\r\n").lower()
            yield line.partition(",")[2] if "," in line else line


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Supply one supported modern game")
    game = modern_game(sys.argv[1])
    texts = defaultdict(set)          # (cat, line) -> texts
    speaker = defaultdict(set)        # aspk -> {(dir with '.', fspk)}
    for name in modern_names("sound_asset"):
        m = FILE.match(name)
        if m:
            texts[(m["cat"], m["line"])].add(m["text"])
            speaker[m["aspk"]].add((m["dir"].replace("/", "."), m["fspk"]))
    aliases = set()
    for name in modern_names("sound_alias"):
        m = ALIAS.match(name)
        if m:
            aliases.add(m.groups())
    stems = set()
    for cat, line, aspk in aliases:
        for d, fspk in speaker.get(aspk, ()):
            if game not in DOTTED:
                d = d.replace(".", "/")
            sep = "." if game in DOTTED else "/"
            for text in texts.get((cat, line), ()):
                for var in VARIANTS:
                    stems.add(f"{d}{sep}dx_op_{fspk}_{cat}_{aspk}_{line}_{text}_{var}")
    out = output_dir()
    _, endings = sound_lists(game)
    (out / f"dtb_{game}.ends.txt").write_text("\n".join(endings) + "\n", encoding="utf8")
    (out / f"dtb_{game}.stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"dtb_{game}.txt").write_text(
        f"label: operator dialogue files from known aliases x texts other operators speak, {game}\n"
        "describe: speaker folder/code from any resolved file, (cat,line) from resolved aliases, "
        "text from every operator's file for that line, variants ogr2/opg2/opg3, x the target's "
        "own tails (scripts/contributed/dx_text_borrow_20261015-105031.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/dtb_{game}.stems.txt\n"
        f"end: @contrib/out/dtb_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    ends = len(endings)
    print(f"{game}: {len(aliases):,} aliases, {len(speaker)} speakers -> {len(stems):,} heads "
          f"x {ends} tails = {len(stems) * ends:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
