"""Modern footstep files as a full grid: surface x action x side x npc x take x tail.

`core/fly/foot/<surface>/[npc/]step_<action>_<surface>[_l|_r][_npc]_<NN>.<tail>` -- measured
2026-10-16 from BO7's link table: `step_mp_*` / `stepstair*` aliases play ~4,000 unnamed files
against ~1,200 resolved. Surfaces come from every modern title's resolved footstep files and from
`step_mp_<surface>_...` aliases; actions, take ranges and tails from the resolved files.

    python contrib/footstep_grid.py <GAME> | confirm_list - --game <GAME>
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

MODERN = ["MODWAR22", "YAMYAMOK", "BLACKOP6", "BLACKOP7", "MODWAR7"]
FOOT = re.compile(r"^core[./]fly[./]foot[./]([a-z0-9_]+)[./](?:npc[./])?step_([a-z]+)_(\1)((?:_[lr])?)((?:_npc)?)_(\d{2})"
                  r"(\.[a-z]{1,4}\.\d{1,3}\.\d{4,6}\.[a-z_]+)$")
STEP_ALIAS = re.compile(r"^step(?:stair(?:up|down))?_mp_([a-z0-9_]+?)_(?:ally|enemy|plr|npc|default)")


def main():
    game = sys.argv[1].upper()
    sep = "." if game in ("MODWAR22", "YAMYAMOK") else "/"
    surfaces, actions = set(), set()
    takes = defaultdict(int)
    tails = defaultdict(set)
    for g in MODERN:
        for line in (ROOT / "state" / "an" / f"{g}_sound_asset.named").open(encoding="utf-8"):
            m = FOOT.match(line.strip())
            if not m:
                continue
            surf, act, _, side, npc, take, tail = m.groups()
            surfaces.add(surf)
            actions.add(act)
            takes[act] = max(takes[act], int(take))
            if g == game:
                tails[(act, bool(npc))].add(tail)
        for line in (ROOT / "state" / "an" / f"{g}_sound_alias.named").open(encoding="utf-8"):
            m = STEP_ALIAS.match(line.strip())
            if m:
                surfaces.add(m.group(1))
    all_tails = set().union(*tails.values()) if tails else set()
    out = sys.stdout
    n = 0
    for surf in surfaces:
        for act in actions:
            for npc in ("", "_npc"):
                tl = tails.get((act, bool(npc))) or all_tails
                folder = f"core{sep}fly{sep}foot{sep}{surf}{sep}" + (f"npc{sep}" if npc else "")
                for side in ("", "_l", "_r"):
                    for k in range(1, max(takes[act], 6) + 3):
                        for t in tl:
                            out.write(f"{folder}step_{act}_{surf}{side}{npc}_{k:02d}{t}\n")
                            n += 1
    print(f"{game}: {len(surfaces)} surfaces x {len(actions)} actions -> {n:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
