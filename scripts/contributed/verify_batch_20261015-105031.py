"""Independent duplicate check for submission folders (analysis helper, not a method).

For every `hash,name` line in the given submission folders: rehash the name under its game's
policy, and check (1) the stored hash matches, (2) the id is in the game's capture, (3) the id was
UNNAMED in state/an/<GAME>_<pool>.unnamed (dumped before the run: tables + every confirmed and
merged name), (4) the id is not in state/claimed.txt (open pull requests), (5) no two names in the
batch share an id, (6) no name was already sent in an earlier submission folder by anybody.

    PYTHONPATH=scripts python contrib/verify_batch.py submissions/ImSimpy_YAMYAMOK_20261015-*
"""
from collections import defaultdict
from pathlib import Path
import sys

import snapshot

M = snapshot.ID_MASK
ROOT = Path(".")


def main():
    folders = [Path(p) for p in sys.argv[1:]]
    claimed = {int(x, 16) & M for x in (ROOT / "state/claimed.txt").read_text().split() if x}
    mine = {f.resolve() for f in folders}
    unnamed_cache, snap_cache = {}, {}

    # every name anybody else has ever submitted, per game folder tag
    prior = defaultdict(set)
    for sub in (ROOT / "submissions").iterdir():
        if not sub.is_dir() or sub.resolve() in mine:
            continue
        tag = sub.name.split("_")[-2] if sub.name.count("_") >= 2 else ""
        for f in sub.glob("*.txt"):
            for line in f.open(encoding="utf-8", errors="replace"):
                prior[tag.upper()].add(line.rstrip("\r\n").partition(",")[2].lower())

    total = defaultdict(int)
    for folder in folders:
        game = folder.name.split("_")[-2].upper()
        for f in sorted(folder.glob("*.txt")):
            kind = f.name.rsplit("_", 1)[0]
            key = (game, kind)
            if key not in unnamed_cache:
                snap_cache[key] = {i & M for i in
                                   snapshot.read(f"snapshots/{game.lower()}.ids").by_pool().get(kind, [])}
                dump = ROOT / f"state/an/{game}_{kind}.unnamed"
                if dump.exists():
                    unnamed_cache[key] = {int(x, 16) for x in dump.read_text().split()}
                else:
                    # no pre-run dump (BO4/CW): unnamed = in the capture and not in any table
                    known = {h & M for h in snapshot.known_hashes(game=game)}
                    unnamed_cache[key] = snap_cache[key] - known
            seen = {}
            for line in f.open(encoding="utf-8"):
                stored, _, name = line.rstrip("\r\n").partition(",")
                if not name:
                    continue
                h = snapshot.fnv1a(name, game, kind) & M
                c = total
                c[game, "names"] += 1
                if int(stored, 16) & M != h:
                    c[game, "BAD stored hash"] += 1
                if h not in snap_cache[key]:
                    c[game, "NOT in capture"] += 1
                if h not in unnamed_cache[key]:
                    c[game, "ALREADY NAMED before today"] += 1
                if h in claimed:
                    c[game, "CLAIMED in an open PR"] += 1
                if h in seen and seen[h] != name.lower():
                    c[game, "two names one id"] += 1
                seen[h] = name.lower()
                if name.lower() in prior[game]:
                    c[game, "already in someone's submission"] += 1
    for game in sorted({g for g, _ in total}):
        problems = {k: v for (g, k), v in total.items() if g == game and k != "names"}
        print(f"{game}: {total[game, 'names']:,} names checked -> "
              + (", ".join(f"{k}: {v}" for k, v in problems.items()) if problems else "all clean"))


if __name__ == "__main__":
    main()
