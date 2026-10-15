"""Read-only exact-game/pool/key audit of aggregate findings. Never edits results.

Usage: python THIS_SCRIPT --check GAME ...
Malformed rows, wrong hash width and BO4 sound folding errors fail closed.
Quarantine/move mode was removed because aggregate results must only grow.
"""
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run inside a hash-slinging-slasher checkout")
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from generator_inputs import all_known_names, modern_game, modern_names, named_names, output_dir, sound_lists

import snapshot
import settings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', required=True)
    parser.add_argument('games', nargs='+', choices=sorted(snapshot.MODERN | {'BLKOPS04','BLKOPSCW'}))
    args = parser.parse_args()
    root = Path(settings.path('findings', 'findings'))
    errors = 0
    shots = {}
    for source in snapshot.snapshots():
        shot = snapshot.read(source)
        if shot.game in shots: raise ValueError('Multiple captures for '+shot.game)
        shots[shot.game] = shot
    for game in args.games:
        shot = shots.get(game)
        if shot is None: raise ValueError('Missing exact-game capture: '+game)
        pools = shot.by_pool()
        for path in sorted((root/game.lower()).glob('*.txt')):
            kind = path.stem
            held = {key & snapshot.ID_MASK for key in pools.get(kind, [])}
            for line, row in enumerate(path.read_text(encoding='utf8').splitlines(),1):
                raw, sep, name = row.partition(',')
                good = bool(sep and name and name == name.strip() and not any(ord(c)<32 or ord(c)==127 for c in name))
                try: stored = int(raw,16)
                except ValueError: good = False; stored = -1
                full = snapshot.fnv1a_nofold(name) if game == 'BLKOPS04' and kind == 'sound_asset' else snapshot.fnv1a(name,game,kind)
                expected = full if game in snapshot.MODERN and kind == 'sound_alias' else full & snapshot.ID_MASK
                if not good or stored != expected or expected & snapshot.ID_MASK not in held:
                    print(f'{game} {kind} line {line}: invalid key/spelling or absent from exact captured pool')
                    errors += 1
    print('invalid aggregate rows:',errors)
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
