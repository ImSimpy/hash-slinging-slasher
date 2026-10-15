#!/usr/bin/env bash
# Audit the configured aggregate findings, then use the standard submission pipeline.
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(git -C "$HERE" rev-parse --show-toplevel)
cd "$ROOT"
P=${PYTHON:-python}
"$P" "$HERE/split_wrong_game_20261015-110216.py" --check BLACKOP6 BLACKOP7 MODWAR22 YAMYAMOK MODWAR7 BLKOPS04 BLKOPSCW
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) TOOL=bin/windows/submit.exe ;;
  Darwin*) TOOL=bin/macos/submit ;;
  *) TOOL=bin/linux/submit ;;
esac
if [[ -x "$TOOL" ]]; then exec "$TOOL"; fi
exec cargo run --release --locked --bin submit
