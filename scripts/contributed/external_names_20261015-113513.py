"""Every name-shaped field from another local name-recovery tree, minus what this repository knows.

Reads every .txt/.tsv/.csv under the given folders, splits each line on tab/comma, and keeps any
field that looks like an asset name (lower-case path-ish token, 3-200 chars, a letter in it).
Names already present in verified public tables or current submissions/findings are dropped.

    python scripts/contributed/external_names_20261015-113513.py <folder>... > contrib/out/external.txt
    confirm_list contrib/out/external.txt --game <GAME>
"""
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

NAME = re.compile(r"^[a-z0-9_/\\.~&@#$-]{3,200}$")
SPLIT = re.compile(r"[\t,]")
LETTER = re.compile(r"[a-z]")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Supply one or more explicit local input directories")
    folders = [Path(value) for value in sys.argv[1:]]
    if any(not folder.is_dir() for folder in folders):
        raise SystemExit("Every input must be an existing directory")
    known = set(all_known_names())
    new = set()
    files = 0
    for folder in folders:
        for p in folder.rglob("*"):
            if p.is_symlink() or not p.is_file() or p.suffix.lower() not in (".txt", ".tsv", ".csv"):
                continue
            files += 1
            with p.open(encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    for field in SPLIT.split(line.strip().lower()):
                        field = field.strip().strip('"')
                        if NAME.match(field) and LETTER.search(field) and field not in known:
                            new.add(field)
    sys.stdout.write("\n".join(sorted(new)) + "\n")
    print(f"{files} files -> {len(new):,} names not known here", file=sys.stderr)


if __name__ == "__main__":
    main()
