#!/usr/bin/env bash
# submit, guarded: refuse if any game's aggregate findings hold names that do not hash into that
# game's capture (the 2026-10-15 leak), and verify every new submission folder afterwards.
set -u
P=${PYTHON:-python}
G="BLACKOP6 BLACKOP7 MODWAR22 YAMYAMOK MODWAR7 BLKOPS04 BLKOPSCW"
if ls -d findings/*/run_*_recovered >/dev/null 2>&1; then
  echo "REFUSING: recovered run folders present -- inspect before sending:"; ls -d findings/*/run_*_recovered
  exit 1
fi
PYTHONPATH=scripts $P contrib/split_wrong_game.py --check $G || { echo "REFUSING: wrong-game names in findings"; exit 1; }
before=$(mktemp); ls -d submissions/ImSimpy_* | sort > "$before"
./bin/windows/submit.exe > logs/submit_last.log 2>&1
echo "submit exit=$?"
grep -E "^--- |names to send|dropped|submitted:" logs/submit_last.log
new=$(ls -d submissions/ImSimpy_* | sort | comm -13 "$before" -)
[ -n "$new" ] && PYTHONPATH=scripts $P contrib/verify_batch.py $new
