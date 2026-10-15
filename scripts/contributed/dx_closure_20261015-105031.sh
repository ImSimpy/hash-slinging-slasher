#!/usr/bin/env bash
# One closure round of the operator-dialogue methods (34, alias grid, text borrow) over every
# modern title, each fed by whatever the previous step confirmed. Run from the repo root; pass
# --anyway through as $1 when the futility ledger is tripped by an unrelated dead end.
set -u
P=${PYTHON:-python}
ANY=${1:-}
G="MODWAR22 YAMYAMOK BLACKOP7 MODWAR7 BLACKOP6"
total=0
$P contrib/dx_alias_from_files.py > contrib/out/dx_alias.txt
for g in $G; do
  ./bin/windows/confirm_list.exe contrib/out/dx_alias.txt --game $g $ANY \
    --label "operator dialogue aliases derived from dialogue file names" \
    --script contrib/dx_alias_from_files.py > logs/dxc_a_$g.log 2>&1
  n=$(grep -oE 'this run added [0-9]+' logs/dxc_a_$g.log | tail -1 | grep -oE '[0-9]+$'); total=$((total + ${n:-0}))
done
$P contrib/dx_alias_grid.py > /dev/null
for g in $G; do
  ./bin/windows/confirm_plan.exe plans/dxg.txt --game $g $ANY > logs/dxc_g_$g.log 2>&1
  n=$(grep -oE 'this run added [0-9]+' logs/dxc_g_$g.log | tail -1 | grep -oE '[0-9]+$'); total=$((total + ${n:-0}))
done
for g in $G; do
  $P contrib/dx_text_borrow.py $g 2>/dev/null
  ./bin/windows/confirm_plan.exe plans/dtb_$g.txt --game $g $ANY > logs/dxc_t_$g.log 2>&1
  n=$(grep -oE 'this run added [0-9]+' logs/dxc_t_$g.log | tail -1 | grep -oE '[0-9]+$'); total=$((total + ${n:-0}))
done
echo "closure round added $total"
