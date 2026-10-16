"""Unnamed sound files built from the *named alias that plays them*, in their bank's folders.

A capture's link table (bank, alias, sound -- HashFinder3000's `snapshots/<game>.links.tsv.gz`, read
out of the sound banks) says which alias plays which sound file. Measured 2026-10-16 on BO7: 344,651
links run from a resolved alias to an unnamed sound, and files are named after their alias
(`weap_x_fire_plr` plays `weap_x_fire_plr_01`, an npc alias plays `fly_plr_..._<event>` files).

For every resolved alias with an unnamed linked sound this emits heads
    <folder>/<variant>
where <variant> is the alias, the alias with npc<->plr swapped, and the alias minus its last token,
and <folder> is every folder of a resolved file in the *same bank* sharing >= 2 leading tokens
with the alias (all of the bank's folders when it has <= 4). Ends are suffix x tail: "", _01.._24,
_a.._e, plus the target's measured tails.

    python contrib/linked_alias_files.py <GAME> <links.tsv.gz>  -> contrib/out/laf_<GAME>.*.txt + plan
    bin/windows/confirm_plan plans/laf_<GAME>.txt --game <GAME>
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
DOTTED = {"MODWAR22", "YAMYAMOK"}


def main():
    game, links = sys.argv[1].upper(), sys.argv[2]
    an = ROOT / "state" / "an"
    sep = "." if game in DOTTED else "/"
    files = {}
    for line in (an / f"{game}_sound_asset.named").open(encoding="utf-8"):
        n = line.strip()
        m = TAIL.search(n)
        if m:
            files[snapshot.fnv1a(n, game, "sound_asset") & M] = n[:m.start()].replace("/", ".")
    aliases = {}
    for line in (an / f"{game}_sound_alias.named").open(encoding="utf-8"):
        n = line.strip()
        aliases[snapshot.fnv1a(n, game, "sound_alias") & M] = n
    unnamed = {int(x, 16) for x in (an / f"{game}_sound_asset.unnamed").read_text().split()}

    bank_dirs = defaultdict(set)
    wanted = defaultdict(set)          # bank -> aliases with an unnamed sound
    for line in gzip.open(links, "rt"):
        b, a, s = (int(x, 16) & M for x in line.split("\t")[:3])
        if s in files:
            bank_dirs[b].add(files[s].rpartition(".")[0])
        elif s in unnamed and a in aliases:
            wanted[b].add(aliases[a])

    stems = set()
    for b, als in wanted.items():
        dirs = bank_dirs.get(b, set())
        if not dirs:
            continue
        for a in als:
            t = a.split("_")
            near = [d for d in dirs if any(seg.startswith("_".join(t[:2])) or "_".join(t[:2]) in seg
                                         for seg in d.split("."))] if len(dirs) > 4 else list(dirs)
            if not near:
                near = list(dirs) if len(dirs) <= 12 else []
            variants = {a, a.replace("_npc_", "_plr_"), a.replace("_plr_", "_npc_")}
            if len(t) > 2:
                variants.add("_".join(t[:-1]))
            for d in near:
                dd = d if sep == "." else d.replace(".", "/")
                for v in variants:
                    stems.add(f"{dd}{sep}{v}")
    tails = [l.strip() for l in (ROOT / "contrib" / "out" / f"stt2_{game}.ends.txt").open() if l.strip()]
    suffixes = [""] + [f"_{i:02d}" for i in range(1, 25)] + [f"_{c}" for c in "abcde"]
    ends = [s + t for s in suffixes for t in tails]
    out = ROOT / "contrib" / "out"
    (out / f"laf_{game}.stems.txt").write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    (out / f"laf_{game}.ends.txt").write_text("\n".join(ends) + "\n", encoding="utf-8")
    (ROOT / "plans" / f"laf_{game}.txt").write_text(
        f"label: unnamed sound files from the named alias that plays them (link table), {game}\n"
        "describe: alias variants in the folders of resolved files in the same sound bank, x take/"
        "letter suffixes x the target's tails (contrib/linked_alias_files.py)\n"
        f"game: {game.lower()}\n"
        f"stem: @contrib/out/laf_{game}.stems.txt\n"
        f"end: @contrib/out/laf_{game}.ends.txt\n"
        "bare: yes\n", encoding="utf-8")
    print(f"{game}: {sum(len(v) for v in wanted.values()):,} bank/alias pairs, {len(stems):,} heads "
          f"x {len(ends):,} ends = {len(stems) * len(ends):,}", file=sys.stderr)


if __name__ == "__main__":
    main()
