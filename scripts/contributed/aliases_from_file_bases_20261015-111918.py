"""Modern non-dialogue sound aliases from sound-file basenames (and the basename minus 1-2 tokens or
its take number). Reproduces ~5% of resolved non-dx aliases (2026-10-15); cheap, 356 K candidates.

    python scripts/contributed/aliases_from_file_bases_20261015-111918.py | confirm_list - --game <GAME>
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from generator_inputs import all_known_names, modern_game, modern_names, named_names, output_dir, sound_lists
TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")
out = set()
for l in modern_names("sound_asset"):
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
