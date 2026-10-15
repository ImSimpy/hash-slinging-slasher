"""Is the `~<decimal>` suffix of a packed modern image name derivable from the rest of it?
(analysis helper, not a method)

Packed images read `<a>&<b>~<decimal>`; prints, for a sample of resolved ones, whether the decimal
equals any of a handful of standard hashes of the prefix or its parts.
"""
from pathlib import Path
import random
import sys
import zlib

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from generator_inputs import all_known_names, modern_game, modern_names, named_names, output_dir, sound_lists


MASK64 = (1 << 64) - 1


def fnv1a64(s, basis=0xCBF29CE484222325):
    h = basis
    for b in s.encode():
        h = ((h ^ b) * 0x100000001B3) & MASK64
    return h


def fnv1a32(s):
    h = 0x811C9DC5
    for b in s.encode():
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h


def murmur_like(s):
    return zlib.crc32(s.encode())


game = modern_game(sys.argv[1]) if len(sys.argv) == 2 else "MODWAR22"
names = sorted(n for n in named_names(game, "image") if "~" in n)
print(f"{game}: {len(names):,} packed of resolved images")
random.seed(1)
hits = {}
for n in random.sample(names, min(300, len(names))):
    head, _, num = n.rpartition("~")
    if not num.isdigit():
        continue
    v = int(num)
    parts = [head] + head.split("&")
    for p in parts:
        for label, fn in (("fnv64", fnv1a64), ("fnv64_modern", lambda s: fnv1a64(s, 0x47F5817A5EF961BA)),
                          ("fnv32", fnv1a32), ("crc32", murmur_like)):
            for variant in (p, p + "~", p.lower()):
                h = fn(variant)
                if h == v or h & (MASK64 >> 1) == v & (MASK64 >> 1):
                    hits[label] = hits.get(label, 0) + 1
print("matches:", hits or "none")
print("examples:", *random.sample(names, min(3, len(names))), sep="\n  ")
