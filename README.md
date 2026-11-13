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
   2026: about 18% a year (90% range 15–22%), about 9.5% compounded.
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
./run_all.sh    # fetches the data snapshot (about 260 MB) on first run, then about three minutes
```

The script fetches the Coin Metrics community dataset at the exact commit the paper used
(`f1a36af`, data ending 2026-05-24), then runs every step below in order. Re-running
reproduces every CSV in `outputs/` byte-for-byte. A GitHub Actions workflow does this on
every push and monthly, and fails if a script stops, any table differs or any audit line is not PASS; the
badge above shows the latest run.

| Script | What it produces | Where it appears |
|---|---|---|
| **1. The census of cryptoasset deaths** | | |
| `03_rebuild_panel.py` | Birth and death panel from the Coin Metrics asset files | Section 3 |
| `05_size_elite.py` | Monthly volume matrix; size quartiles and ever-top-N cohorts | Section 3 (Table 1), Appendix C.2 |
| `06_voldeath.py` | Volume-collapse deaths; unified death definition | Section 3, Appendix C |
| `07_curated.py` | Migrations and dated collapses; `panel_v3.csv`, hazards, the elite death table | Section 3, Appendix C.3 |
| `08_cohorts.py` | Buy-at-birth cohort returns | Appendix C |
| `10_robustness.py` | Cohort fixed effects, Weibull and log-logistic fits | Appendix C.4 |
| `12_audit.py` | 33 checks of the census numbers quoted in the paper | Section 3, Appendix C |
| `09_figures.py`, `11_km_figure.py`, `21_final_figs.py` | Draft figures and `wedge_table.csv` from an earlier calibration, kept for the record | not in the paper |
| **2. The required-return model** | | |
| `22_pretty_figs.py` | The shared construction of the required-return band (inputs, holder weight, edges), used by the scripts below; hazard and survival figures | Sections 3 and 5, Appendix C |
| `23_uncertainty.py` | Propagation of the input ranges; sensitivities | Section 4, Tables 7 and 8, Appendix D.1 |
| `26_holder_weight.py` | The holder weight through time | Appendix B |
| `27_monthly_test.py` | The monthly test and its figure | Section 5 (Table 5) |
| `28_cryptowide_backcast.py` | Back-cast on total crypto capitalization | Appendix D.5 |
| `29_required_fig.py` | The required return since 2012; `required_band_monthly.csv` | Section 5 |
| `30_inputs_fig.py` | The inputs that move with time | Section 5 |
| `31_cross_section.py`, `32_eth_fig.py` | Ether and other cryptoassets | Section 7 |
| `33_activity_beta.py` | On-chain activity and the equity beta | Appendix E.2 |
| `34_beta_windows.py`, `42_beta_fig.py` | Beta by estimation window and against a global index; rolling beta figure | Appendix A.1 to A.3 |
| `35_option_bound.py` | Option-implied cap on the probability of a collapse | Appendix C.5 |
| `36_ownership_sensitivity.py` | Alternative ownership path | Appendix D.4 |
| `37_age_rule_exponent.py`, `38_grouping_robustness.py` | Real-time age-rule exponent; other groupings of the monthly test | Appendix D.2 |
| `39_index_exposure.py` | Bitcoin exposure inside the S&P 500 | Appendix A.6 |
| `40_death_date_check.py` | Collapse dates moved within their documented windows | Appendix C.3 |
| `41_volatility_table.py` | Volatility by window and by currency | Appendix A.7 |
| `43_band_table.py` | The band worked out at five dates: inputs, both candidates for the upper edge, midpoint | Table 4 |
| **3. The audit** | | |
| `13_model_audit.py` | 948 checks: recomputes every number the paper quotes from the model (prints PASS or FAIL per claim) | all sections |

`24_terms_fig.py` and `25_wedge_log.py` draw earlier figures that are not in the paper. All scripts
locate `data/`, `outputs/` and `figures/` relative to the repository; the environment variables
`DATA_DIR`, `OUT_DIR`, `FIG_DIR` and `CM_CSV_DIR` override them.

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
