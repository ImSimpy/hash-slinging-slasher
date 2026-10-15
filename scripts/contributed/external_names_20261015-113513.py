"""Every name-shaped field from another local name-recovery tree, minus what this repository knows.

Reads every .txt/.tsv/.csv under the given folders, splits each line on tab/comma, and keeps any
field that looks like an asset name (lower-case path-ish token, 3-200 chars, a letter in it).
Anything already in contrib/out/every_name.txt is dropped, so the output is only new seed text.

    python contrib/external_names.py <folder>... > contrib/out/external.txt
    confirm_list contrib/out/external.txt --game <GAME>
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

NAME = re.compile(r"^[a-z0-9_/\\.~&@#$-]{3,200}$")
SPLIT = re.compile(r"[\t,]")
LETTER = re.compile(r"[a-z]")


def main():
    known = {l.strip().lower() for l in (ROOT / "contrib" / "out" / "every_name.txt")
             .open(encoding="utf-8", errors="replace")}
    new = set()
    files = 0
    for folder in sys.argv[1:]:
        for p in Path(folder).rglob("*"):
            if not p.is_file() or p.suffix.lower() not in (".txt", ".tsv", ".csv"):
                continue
            files += 1
            for line in p.open(encoding="utf-8", errors="replace"):
                for field in SPLIT.split(line.strip().lower()):
                    field = field.strip().strip('"')
                    if NAME.match(field) and LETTER.search(field) and field not in known:
                        new.add(field)
    sys.stdout.write("\n".join(sorted(new)) + "\n")
    print(f"{files} files -> {len(new):,} names not known here", file=sys.stderr)


if __name__ == "__main__":
    main()
