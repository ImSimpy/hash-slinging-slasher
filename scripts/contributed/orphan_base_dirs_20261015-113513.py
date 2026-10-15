"""Folder-less sound basenames placed in the folders of resolved files sharing their longest prefix.

An external tree (HashFinder3000) holds millions of sound basenames with their format tail but no
directory -- `weap_rex_rex_kilo5_fire_npc_shot_far_03.snn.50.48000.all`. A modern sound file is
only reachable with its folder, and siblings share folders: so each basename is offered under
every folder whose resolved files share its longest token prefix (>= MIN_TOKENS, at most MAX_DIRS
folders), spelled for the target.

    python scripts/contributed/orphan_base_dirs_20261015-113513.py <GAME> < contrib/out/orphan_bases.txt | confirm_list - --game <GAME>
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

TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
DOTTED = {"MODWAR22", "YAMYAMOK"}
MIN_TOKENS, MAX_TOKENS, MAX_DIRS = 3, 8, 6


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Supply one supported modern game")
    game = modern_game(sys.argv[1])
    dirs_by_prefix = defaultdict(set)
    for g in MODERN:
        for line in named_names(g, "sound_asset"):
            n = line.strip()
            m = TAIL.search(n)
            if not m:
                continue
            head = n[:m.start()].replace("/", ".")
            d, _, base = head.rpartition(".")
            if not d:
                continue
            t = base.split("_")
            for k in range(MIN_TOKENS, min(MAX_TOKENS, len(t)) + 1):
                dirs_by_prefix["_".join(t[:k])].add(d)
    out = sys.stdout
    emitted = 0
    for line in sys.stdin:
        name = line.strip()
        m = TAIL.search(name)
        if not m:
            continue
        base = name[:m.start()]
        t = base.split("_")
        for k in range(min(MAX_TOKENS, len(t)), MIN_TOKENS - 1, -1):
            dirs = dirs_by_prefix.get("_".join(t[:k]))
            if dirs and len(dirs) <= MAX_DIRS:
                for d in sorted(dirs):
                    dd = d if game in DOTTED else d.replace(".", "/")
                    sep = "." if game in DOTTED else "/"
                    out.write(f"{dd}{sep}{name}\n")
                    emitted += 1
                break
    print(f"{emitted:,} placed candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
