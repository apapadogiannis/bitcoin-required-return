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

# 1. The census of cryptoasset deaths (Section 3, Appendix C).
for f in 03_rebuild_panel 05_size_elite 06_voldeath 07_curated 08_cohorts 09_figures \
         11_km_figure 10_robustness 12_audit 21_final_figs; do
  echo "== $f"; python3 -I "scripts/$f.py"
done
# figures written to OUT_DIR by the census scripts are drafts; the paper's versions come from step 2
rm -f "$OUT_DIR"/fig*.pdf "$OUT_DIR"/fig*.png

# 2. The required-return model (Sections 4 to 7, Appendices A, B, D, E).
echo "== 23_uncertainty"; python3 -I scripts/23_uncertainty.py > "$OUT_DIR/uncertainty_propagation.txt"
for f in 22_pretty_figs 26_holder_weight 27_monthly_test 28_cryptowide_backcast 29_required_fig \
         30_inputs_fig 31_cross_section 33_activity_beta 34_beta_windows 35_option_bound \
         36_ownership_sensitivity 37_age_rule_exponent 38_grouping_robustness 39_index_exposure \
         40_death_date_check 41_volatility_table 43_band_table 44_holders_and_comovement 45_euro_table 46_adoption_hazard; do
  echo "== $f"; python3 -I "scripts/$f.py"
done

# 3. The audit of every number quoted in the paper against the regenerated results.
echo "== 13_model_audit"; python3 -I scripts/13_model_audit.py
rm -f "$FIG_DIR"/fig_wedge.* "$FIG_DIR"/fig2_size.* "$FIG_DIR"/fig4_timeline.* "$FIG_DIR"/fig6_eth.*   # earlier figures, not in the paper
