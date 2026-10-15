"""Modern non-dialogue sound aliases from sound-file basenames (and the basename minus 1-2 tokens or
its take number). Reproduces ~5% of resolved non-dx aliases (2026-10-15); cheap, 356 K candidates.

    python contrib/aliases_from_file_bases.py | confirm_list - --game <GAME>
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
out = set()
paths = [ROOT / "state" / "an" / f"{g}_sound_asset.named" for g in
         ("MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7")]
paths += list((ROOT / "findings").rglob("sound_asset*.txt"))
for p in paths:
    for l in p.open(encoding="utf-8", errors="replace"):
        l = l.strip().lower()
        n = TAIL.sub("", l.partition(",")[2] if "," in l else l).replace("/", ".")
        b = n.rsplit(".", 1)[-1]
        if not b:
            continue
        out.add(b)
        t = b.split("_")
        for k in (1, 2):
            if len(t) > k + 1:
                out.add("_".join(t[:-k]))
        out.add(re.sub(r"_\d{1,3}$", "", b))
print("\n".join(sorted(out)))
