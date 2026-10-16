"""Unnamed sound files next to linked siblings: sibling prefix x the event words of that context.

The link table (bank, alias, sound) groups files by the alias family that plays them. Measured
2026-10-16 on BO7: a numbered alias plays event-named files (`fly_npc_..._ext02_12` plays
`fly_plr_..._ext02_magout`), so where an alias family has resolved files and unnamed ones, the
unnamed files are that family's prefix with other event words. For every alias family (alias minus
its last token) with at least one unnamed linked sound, each resolved file it plays gives
(folder, prefix = basename minus last token, tail); the prefix is offered with every last token seen
anywhere after the same two-token context (the two tokens before the last), keeping the sibling's
folder and tail.

    python contrib/linked_event_fill.py <GAME> <links.tsv.gz> | confirm_list - --game <GAME>
"""
from collections import defaultdict
import gzip
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot  # noqa: E402

M = snapshot.ID_MASK
TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
MAX_VOCAB = 300


def split(name):
    m = TAIL.search(name)
    if not m:
        return None
    head = name[:m.start()]
    cut = max(head.rfind("/"), head.rfind("."))
    return head[:cut + 1], head[cut + 1:], name[m.start():]


def main():
    game, links = sys.argv[1].upper(), sys.argv[2]
    an = ROOT / "state" / "an"
    files = {}
    vocab = defaultdict(set)
    for line in (an / f"{game}_sound_asset.named").open(encoding="utf-8"):
        n = line.strip()
        p = split(n)
        if not p:
            continue
        files[snapshot.fnv1a(n, game, "sound_asset") & M] = p
        t = p[1].split("_")
        if len(t) >= 3:
            vocab["_".join(t[-3:-1])].add(t[-1])
    aliases = {}
    for line in (an / f"{game}_sound_alias.named").open(encoding="utf-8"):
        n = line.strip()
        aliases[snapshot.fnv1a(n, game, "sound_alias") & M] = n
    unnamed = {int(x, 16) for x in (an / f"{game}_sound_asset.unnamed").read_text().split()}

    fam_files = defaultdict(set)
    fam_open = set()
    for line in gzip.open(links, "rt"):
        _, a, s = (int(x, 16) & M for x in line.split("\t")[:3])
        fam = aliases.get(a, f"#{a:x}").rsplit("_", 1)[0] if a in aliases else f"#{a:x}"
        if s in files:
            fam_files[fam].add(files[s])
        elif s in unnamed:
            fam_open.add(fam)
    seen = set()
    out = sys.stdout
    for fam in fam_open:
        for folder, base, tail in fam_files.get(fam, ()):
            t = base.split("_")
            if len(t) < 3:
                continue
            words = vocab.get("_".join(t[-3:-1]), ())
            if len(words) > MAX_VOCAB:
                continue
            prefix = "_".join(t[:-1])
            for w in words:
                c = f"{folder}{prefix}_{w}{tail}"
                if c not in seen:
                    seen.add(c)
                    out.write(c + "\n")
    print(f"{game}: {len(fam_open):,} open alias families -> {len(seen):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
