#!/usr/bin/env bash
# Reproduces every table and figure in the paper from the Coin Metrics snapshot the
# paper used. Step 0 fetches that snapshot (about 260 MB) if it is not already present.
set -e
cd "$(dirname "$0")"
export CM_CSV_DIR="${CM_CSV_DIR:-data/cmdata/csv}" OUT_DIR="${OUT_DIR:-outputs}" FIG_DIR="${FIG_DIR:-figures}"
CM_COMMIT=f1a36afb962731c387bb03982758ab0103063da5   # coinmetrics/data, "Update CSV 2026-05-24"

if [ ! -f "$CM_CSV_DIR/btc.csv" ]; then
  echo "== fetching Coin Metrics community data at $CM_COMMIT"
  mkdir -p "$(dirname "$CM_CSV_DIR")"
  git -C "$(dirname "$CM_CSV_DIR")" init -q
  git -C "$(dirname "$CM_CSV_DIR")" fetch -q --depth 1 https://github.com/coinmetrics/data.git "$CM_COMMIT"
  git -C "$(dirname "$CM_CSV_DIR")" checkout -q FETCH_HEAD -- csv
fi

mkdir -p "$OUT_DIR" "$FIG_DIR"
for f in 03_rebuild_panel 06_voldeath 07_curated 05_size_elite 08_cohorts 09_figures \
         11_km_figure 10_robustness 12_audit 21_final_figs 22_pretty_figs; do
  echo "== $f"; python3 -I "scripts/$f.py"
done
# paper exhibits produced in OUT_DIR
mv -f "$OUT_DIR"/fig5_km_size.pdf "$OUT_DIR"/fig5_km_size.png "$OUT_DIR"/fig_wedge.pdf "$OUT_DIR"/fig_wedge.png "$FIG_DIR"/
rm -f "$OUT_DIR"/fig6_eth.pdf "$OUT_DIR"/fig6_eth.png   # the final version is written to FIG_DIR by 22_pretty_figs
