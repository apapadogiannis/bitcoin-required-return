# Bitcoin's Required Return

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24003938.svg)](https://doi.org/10.5281/zenodo.24003938)
[![replication](https://github.com/apapadogiannis/bitcoin-required-return/actions/workflows/replicate.yml/badge.svg)](https://github.com/apapadogiannis/bitcoin-required-return/actions/workflows/replicate.yml)

Replication package for the working paper by Agisilaos Papadogiannis (November 2026).
Paper: `paper/manuscript.pdf`. Archived on Zenodo: [doi:10.5281/zenodo.24003938](https://doi.org/10.5281/zenodo.24003938) (concept DOI, always resolves to the latest version; v0.1 is 10.5281/zenodo.24003939).

Related paper: [Bitcoin's Expected Return: An Age Rule That Beats Current Practice](https://github.com/apapadogiannis/bitcoin-age-rule) ([doi:10.5281/zenodo.24004326](https://doi.org/10.5281/zenodo.24004326)).

## What this is

A required return for Bitcoin built from three measured risks, and a test of it against what Bitcoin delivered:

1. **The required-return equation.** The risk-free rate plus market risk (beta to the
   S&P 500), concentration risk (Bitcoin's volatility at its holders' portfolio weights,
   from Fed and Cleveland Fed household surveys) and mortality risk. Central estimate for
   2026: about 18% a year (90% range 15–22%), about 9% compounded.
2. **The census of deaths.** Survival analysis of 1,815 cryptoassets (2010–2026, 520 curated
   deaths) from the Coin Metrics community dataset: mortality hazard by age (the Lindy
   hypothesis is rejected; hazard *rises* with age), by size, and for the ever-top-20
   elite (all-cause 3.5%/yr; jump-collapse 0.30%/yr: LUNA, UST, FTT).
3. **The test.** The required return evaluated at every month-end since 2012 and compared
   with Bitcoin's return over the following month (172 observations).

## Layout

```
scripts/    numbered pipeline (see below)
outputs/    asset-level panel and all result tables used in the paper
figures/    all paper exhibits
paper/      the manuscript PDF
data/       ETF price files (VOO, ACWI, VT, QQQ, IWM, GLD), EUR/USD and the Treasury yield; the crypto data are NOT included and are
            fetched by run_all.sh (see Data and licensing)
```

## Reproducing

Requirements: Python 3.11+, `pip install -r requirements.txt` (pandas, numpy, lifelines,
statsmodels, scipy, matplotlib). For byte-identical tables use `requirements-lock.txt`,
the exact versions under which `outputs/` were generated.

```bash
./run_all.sh    # fetches the data snapshot (about 260 MB) on first run, then about a minute
```

The script fetches the Coin Metrics community dataset at the exact commit the paper used
(`f1a36af`, data ending 2026-05-24), then runs every step below in order. Re-running
reproduces every CSV in `outputs/` byte-for-byte. A GitHub Actions workflow does this on
every push and monthly, and fails if any table differs or any audit line is not PASS; the
badge above shows the latest run.

| Script | What it produces | Where it appears |
|---|---|---|
| `03_rebuild_panel.py` | Birth/death panel from 2,258 asset files | Section 3 |
| `06_voldeath.py` | Volume-collapse deaths, unified death definition | Section 3, Appendix A |
| `07_curated.py` | Migration and catastrophe curation, `panel_v3.csv` | Appendix A |
| `05_size_elite.py` | Size quartiles, ever-top-N cohorts, elite death tables | Section 4 |
| `08_cohorts.py` | Buy-at-birth cohort return curves | Section 4 |
| `09_figures.py`, `22_pretty_figs.py` | Exhibits 1, 2 and 4 | Section 4 |
| `11_km_figure.py` | Exhibit 5, Kaplan-Meier by size | Section 4 |
| `10_robustness.py` | Cohort fixed effects, Weibull and log-logistic fits | Appendix B.1 |
| `12_audit.py` (graveyard, 33 checks) and `scripts/13_model_audit.py` (required-return model, 748 checks); together they recompute every quantitative claim in the paper. `scripts/12_audit.py` | Re-checks every number quoted in the paper (prints PASS per claim) | all sections |
| `21_final_figs.py` | Required return vs realized drift vs age rule: `fig_wedge`, `wedge_table.csv`; Ether compression exhibit | Section 6, Table 6.1, Exhibit 6 |

## Data and licensing

- Crypto price/volume data: [Coin Metrics community data](https://github.com/coinmetrics/data)
  (CC BY-NC 4.0; not redistributed here; step 0 downloads it from the source).
  The dataset snapshot used in the paper ends 2026-05-24.
- ETF prices (`data/voo_monthly.csv`, `data/acwi_monthly.csv`, `data/vt_monthly.csv`,
  `data/qqq_monthly.csv`, `data/iwm_monthly.csv`, `data/gld_monthly.csv`): monthly adjusted close
  (and close, where given) of the Vanguard S&P 500 ETF, the iShares MSCI ACWI ETF, the Vanguard
  Total World Stock ETF, the Invesco QQQ (Nasdaq-100), the iShares Russell 2000 ETF, and SPDR Gold Shares, the
  month-end euro/dollar rate (`data/eurusd_monthly.csv`) and the month-end ten-year Treasury
  yield (`data/tnx_monthly.csv`, the CBOE TNX index), from Yahoo Finance, retrieved November 2026. Used for beta and for the equity and gold figures of the paper's Table 8.
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

> Papadogiannis, A. (2026). "Bitcoin's Required Return." Working paper.
> https://doi.org/10.5281/zenodo.24003938

## Disclaimer

Independent research; no funding, no institutional position. Not investment advice.
