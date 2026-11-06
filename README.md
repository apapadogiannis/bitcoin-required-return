# Bitcoin's Required Return: The Graveyard, the Holders, and the End of the Age Rule

Replication package for the working paper by Agisilaos Papadogiannis (November 2026).
Paper: `paper/manuscript.pdf` (SSRN link to be added).

## What this is

Two measurements and one pricing condition:

1. **The graveyard.** Survival analysis of 1,815 cryptoassets (2010–2026, 520 curated
   deaths) from the Coin Metrics community dataset: mortality hazard by age (the Lindy
   hypothesis is rejected; hazard *rises* with age), by size, and for the ever-top-20
   elite (all-cause 3.5%/yr; jump-collapse 0.30%/yr: LUNA, UST, FTT).
2. **The marginal-holder condition.** Bitcoin's required return measured from its
   holders' portfolio shares (Fed/Cleveland Fed surveys), their stated expectations,
   and option-implied bounds, with the mortality term calibrated from the graveyard.

## Layout

```
scripts/    numbered pipeline (see below)
outputs/    asset-level panel and all result tables used in the paper
figures/    all paper exhibits
paper/      the manuscript PDF
data/       NOT included; created by step 0 below
```

## Reproducing

Requirements: Python 3.11+, `pip install -r requirements.txt` (pandas, numpy,
lifelines, statsmodels, scipy, matplotlib).

```bash
# 0. data (~260 MB)
git clone --depth 1 https://github.com/coinmetrics/data.git data/cmdata

# 1. pipeline (env vars optional; these are the defaults)
export CM_CSV_DIR=data/cmdata/csv OUT_DIR=outputs
python scripts/03_rebuild_panel.py    # birth/death panel from 2,258 asset files
python scripts/06_voldeath.py         # volume-collapse deaths, unified definition
python scripts/07_curated.py          # migration/catastrophe curation -> panel_v3.csv
python scripts/05_size_elite.py       # size quartiles, ever-top-N cohorts
python scripts/08_cohorts.py          # buy-at-birth cohort return curves
python scripts/09_figures.py          # exhibits 1-4
python scripts/11_km_figure.py        # exhibit 5 (Kaplan-Meier by size)
python scripts/10_robustness.py       # cohort-FE, Weibull/log-logistic (Appendix B.1)
python scripts/12_audit.py            # re-checks every number quoted in the paper
python scripts/20_calibrate.py        # marginal-holder calibration, wedge table
```

`scripts/12_audit.py` prints a PASS/CHECK line for every quantitative claim in the
paper; all lines should read PASS.

## Data and licensing

- Crypto price/volume data: [Coin Metrics community data](https://github.com/coinmetrics/data)
  (CC BY-NC 4.0; not redistributed here — step 0 downloads it from the source).
  The dataset snapshot used in the paper ends 2026-05-24.
- Survey anchors, wealth aggregates, and option-implied figures are quoted in the
  paper from their published sources (Cleveland Fed WP 26-16; Fed SCPC/SHED; Pew;
  OeNB Bulletin Q4/25; UBS GWR; arXiv:2410.15195; Deribit DVOL).
- Code: MIT License. Output tables (`outputs/`): CC BY 4.0, cite the paper.

## Death-definition summary (paper Section 3, Appendix A)

Feed death (feed ends >180 d before dataset end), price death (<1% of ATH, no
recovery), volume death (3-month volume <1% of peak AND <$250k/day, no recovery);
ticker migrations are not deaths (holders received successor tokens); known
catastrophes (LUNA, UST, FTT, SRM, ANC, MIR, CEL) entered at their public-record
dates. Full per-death audit table: paper Appendix A; machine-readable flags in
`outputs/elite_top20_curated.csv` and `outputs/panel_v3.csv`.

## Citation

> Papadogiannis, A. (2026). "Bitcoin's Required Return: The Graveyard, the Holders,
> and the End of the Age Rule." Working paper.

## Disclaimer

Independent research; no funding, no institutional position. Not investment advice.
