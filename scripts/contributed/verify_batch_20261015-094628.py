"""Check explicit submission folders against exact-game captures and prior exclusions.

Run after start with one or more folders. A saved state/an/<GAME>_<type>.unnamed
file is optional: when present it additionally checks the before-run set. It is
not trusted for game, pool or hash validation. This diagnostic never edits findings
or submits. Duplicate/claimed rows are reported separately from invalid rows.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts/snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts/snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
sys.path.insert(0, str(ROOT / 'scripts'))
import snapshot

GAMES = snapshot.MODERN | {'BLKOPS04', 'BLKOPSCW'}
MASK = snapshot.ID_MASK

def game_for(folder):
    found = [g for g in GAMES if g in folder.name.upper().split('_')]
    if len(found) != 1:
        raise ValueError(f'{folder}: expected exactly one supported game tag')
    return found[0]

def key_for(name, game, kind):
    full = (snapshot.fnv1a_nofold(name) if game == 'BLKOPS04' and kind == 'sound_asset'
            else snapshot.fnv1a(name, game, kind))
    return full if game in snapshot.MODERN and kind == 'sound_alias' else full & MASK

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folders', nargs='+', type=Path)
    args = parser.parse_args(argv)
    folders = [p.resolve() if p.is_absolute() else (ROOT / p).resolve() for p in args.folders]
    if any(not p.is_dir() for p in folders):
        parser.error('Every input must be an existing submission folder')
    claims = ROOT / 'state/claimed.txt'
    if not claims.is_file():
        parser.error('Run start first to refresh open-PR exclusions')
    claimed = {int(row, 16) & MASK for row in claims.read_text().split()}
    prior = defaultdict(set)
    for sub in (ROOT / 'submissions').iterdir():
        if not sub.is_dir() or sub.resolve() in folders: continue
        try: game = game_for(sub)
        except ValueError: continue
        for path in sub.glob('*.txt'):
            kind = re.sub(r'_\d{8}[-_]\d{6}$', '', path.stem)
            for row in path.read_text(encoding='utf8').splitlines():
                raw, sep, name = row.partition(',')
                if sep:
                    try: prior[game, kind].add(int(raw, 16) & MASK)
                    except ValueError: pass
    stats = defaultdict(int)
    cache, seen, published = {}, {}, {}
    for folder in folders:
        game = game_for(folder)
        if game not in published:
            published[game] = {key & MASK for key in snapshot.known_hashes(game=game)}
        for path in sorted(folder.glob('*.txt')):
            kind = re.sub(r'_\d{8}[-_]\d{6}$', '', path.stem)
            if kind not in snapshot.IMPORTANT or not snapshot.searchable(game, kind):
                raise ValueError(f'{path}: unsupported submission asset type')
            group = game, kind
            if group not in cache:
                shot = snapshot.read(ROOT / 'snapshots' / (game.lower() + '.ids'))
                if shot.game != game: raise ValueError('Capture game differs from submitted game')
                held = {key & MASK for key in shot.by_pool().get(kind, [])}
                before = ROOT / 'state/an' / f'{game}_{kind}.unnamed'
                unnamed = {int(row, 16) & MASK for row in before.read_text().split()} if before.is_file() else None
                cache[group] = held, unnamed
            held, unnamed = cache[group]
            for row in path.read_text(encoding='utf8').splitlines():
                if not row.strip(): continue
                stats[game, 'rows'] += 1
                raw, sep, name = row.partition(',')
                if not sep or not name or name != name.strip() or any(ord(c) < 32 for c in name):
                    stats[game, 'invalid spelling'] += 1; continue
                try: stored = int(raw, 16)
                except ValueError:
                    stats[game, 'invalid key'] += 1; continue
                expected = key_for(name, game, kind)
                if stored != expected:
                    stats[game, 'incorrect key or width'] += 1
                key = expected & MASK
                if key not in held: stats[game, 'absent from exact pool'] += 1
                if key in published[game]: stats[game, 'already published'] += 1
                if unnamed is not None and key not in unnamed: stats[game, 'already in before-run set'] += 1
                if key in claimed: stats[game, 'claimed'] += 1
                identity = game, kind, key
                if identity in seen: stats[game, 'duplicate batch key'] += 1
                seen[identity] = name
                if key in prior[group]: stats[game, 'previously submitted'] += 1
    problems = sum(v for (game, label), v in stats.items() if label != 'rows')
    for game in sorted({g for g, label in stats}):
        issues = {label:v for (g,label),v in stats.items() if g == game and label != 'rows'}
        print(f'{game}: {stats[game, "rows"]:,} rows; ' + (str(issues) if issues else 'all clean'))
    if not stats:
        parser.error('No submission rows were found')
    return 1 if problems else 0

if __name__ == '__main__':
    raise SystemExit(main())
