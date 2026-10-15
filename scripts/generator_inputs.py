"""Shared, local seed inputs for contributed generators and analysis helpers.

Read the configured tables/findings and committed submissions. A measured game/type
set is rehashed against that capture's own pool map; private state/an exports and
contrib/out seed dumps are not prerequisites. These functions never write findings,
run a search, access a game, fetch data, or submit anything.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import re
import struct

import snapshot

ROOT = Path(__file__).resolve().parent.parent
MODERN = ("MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7")
TABLES = {"image":"fnv1a_ximages_v2", "material":"fnv1a_xmaterials_v2",
          "xanim":"fnv1a_xanims_v2", "sound_asset":"fnv1a_xsounds_v2",
          "sound_alias":"fnv1a_soundbanks_aliases_v2"}
TAIL = re.compile(r"\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+$")


def modern_game(value):
    game = value.upper()
    if game not in MODERN:
        raise ValueError("Choose one supported modern game: " + ", ".join(MODERN))
    return game


@lru_cache(maxsize=None)
def capture(game):
    shots = []
    for path in snapshot.snapshots():
        with open(path, "rb") as handle:
            head = handle.read(10)
            if len(head) != 10 or head[:6] != b"CODIDS" or struct.unpack_from("<H", head, 6)[0] != 1:
                raise ValueError(f"Invalid capture header: {path}")
            length = struct.unpack_from("<H", head, 8)[0]
            if not 0 < length <= 64:
                raise ValueError(f"Invalid capture game tag: {path}")
            tag = handle.read(length).decode("ascii")
        if tag == game:
            shots.append(snapshot.read(path))
    if len(shots) != 1:
        raise ValueError(f"Expected one configured capture for {game}; got {len(shots)}")
    return shots[0]


@lru_cache(maxsize=None)
def seeds(kind):
    if kind not in TABLES:
        raise ValueError("Unsupported seed pool: " + kind)
    return frozenset(snapshot.table_names(TABLES[kind])) | frozenset(snapshot.confirmed_names(kind))


@lru_cache(maxsize=None)
def named_names(game, kind):
    game = modern_game(game)
    held = {key & snapshot.ID_MASK for key in capture(game).by_pool().get(kind, [])}
    return frozenset(name for name in seeds(kind)
                     if snapshot.fnv1a(name, game, kind) & snapshot.ID_MASK in held)


def modern_names(kind):
    return sorted(set().union(*(named_names(game, kind) for game in MODERN)))


def all_known_names():
    # These generators previously consumed every_game_transfer output, including
    # legacy names. Keep that reach while using source-verified CSV spellings.
    tables = sorted(path.stem for path in Path(snapshot.settings.tables_csv()).glob("fnv1a_*.csv"))
    return sorted(set(snapshot.table_names(*tables)) | set(snapshot.confirmed_names()))


def sound_lists(game):
    """All known modern heads, target separators, target tails seen >=3 times."""
    game = modern_game(game)
    heads, tails = set(), Counter()
    for source in MODERN:
        for name in named_names(source, "sound_asset"):
            match = TAIL.search(name)
            if match and match.start():
                head = name[:match.start()].replace("/", ".")
                heads.add(head if game in {"MODWAR22", "YAMYAMOK"} else head.replace(".", "/"))
                if source == game:
                    tails[name[match.start():]] += 1
    endings = sorted(tail for tail, count in tails.items() if count >= 3)
    if not endings:
        raise ValueError(f"{game}: no sound tails measured at least three times")
    return sorted(heads), endings


def output_dir():
    out = ROOT / "contrib" / "out"
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / "plans").mkdir(parents=True, exist_ok=True)
    return out
