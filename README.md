# Bitcoin's Required Return

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24003938.svg)](https://doi.org/10.5281/zenodo.24003938)
[![replication](https://github.com/apapadogiannis/bitcoin-required-return/actions/workflows/replicate.yml/badge.svg)](https://github.com/apapadogiannis/bitcoin-required-return/actions/workflows/replicate.yml)

Replication package for the working paper by Agisilaos Papadogiannis (November 2026).
Paper: `paper/manuscript.pdf`. Archived on Zenodo: [doi:10.5281/zenodo.24003938](https://doi.org/10.5281/zenodo.24003938) (concept DOI, always resolves to the latest version; v0.1 is 10.5281/zenodo.24003939).

## What this is

The paper asks what return Bitcoin's holders should require, given the risks they bear, and checks the answer against what Bitcoin delivered.

1. **The MCM equation.** The required return is the risk-free rate plus three risk terms:
   market risk (beta to the S&P 500 times the equity risk premium), concentration risk (risk
   aversion times variance times the share of wealth that holders keep in the asset, from Federal
   Reserve and Cleveland Fed household surveys) and mortality risk (from the census below).
   For 2026: about 18% a year on average (90% range 15–22%), about 9.5% compounded.
2. **The census of deaths.** Survival analysis of 1,815 cryptoassets (2010–2026, 520
   deaths) from the Coin Metrics community dataset: the hazard by age (tracked assets do not
   become safer with age; the Lindy hypothesis is rejected), by size, and for assets that
   were ever in the top twenty (3.5% a year by any cause; 0.30% a year for sudden collapses:
   LUNA, UST, FTT).
3. **The test.** The required return evaluated at every month-end since 2012 and compared
   with Bitcoin's return over the following month (172 observations). Since 2018 the two
   differ by less than one standard error.
4. **Other assets.** The same equation for Ether and other cryptoassets, with four equity
   indices and gold priced on the same inputs for comparison, and the table restated for a
   euro investor.

## Layout

```
scripts/    numbered pipeline (see below)
outputs/    asset-level panel and all result tables used in the paper
figures/    the paper's figures
paper/      the manuscript (PDF and LaTeX source)
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
| `23_uncertainty.py` | Propagation of the input ranges; sensitivities | Section 4 (Table 3), Section 6 (Table 6), Appendices D.1 and E.1 |
| `26_holder_weight.py` | The holder weight through time and its figure | Appendix B, Appendix D.3 and D.4 |
| `27_monthly_test.py` | The monthly test and its figure | Section 5 (Table 5, Figure 3) |
| `28_cryptowide_backcast.py` | Back-cast on total crypto capitalization | Appendix D.4 |
| `29_required_fig.py` | The required return since 2012; `required_band_monthly.csv` | Section 5 (Figure 2) |
| `30_inputs_fig.py` | The inputs that move with time | Section 5 (Figure 1) |
| `31_cross_section.py` | Ether and other cryptoassets: the holder weight of each asset (crypto share times kappa), the term-by-term sums, delivered returns | Section 6 (Table 6) |
| `33_activity_beta.py` | On-chain activity and the equity beta | Appendix A.3 |
| `34_beta_windows.py` | Beta by estimation window and against a global index; correlation by sub-period | Appendix A.2 and A.3 |
| `35_option_bound.py` | Option-implied cap on the probability of a collapse | Appendix C.5 |
| `36_ownership_sensitivity.py` | Alternative ownership path | Appendix D.4 |
| `37_age_rule_exponent.py`, `38_grouping_robustness.py` | Real-time age-rule exponent; other groupings of the monthly test | Appendix D.2 and D.3 |
| `39_index_exposure.py` | Bitcoin exposure inside the S&P 500 | Appendix A.6 |
| `40_death_date_check.py` | Collapse dates moved within their documented windows | Appendix C.3 |
| `41_volatility_table.py` | Volatility by window and by currency | Appendix A.7 |
| `43_band_table.py` | The band worked out at five dates: inputs, both candidates for the upper edge, midpoint | Section 5 (Table 4) |
| `44_holders_and_comovement.py` | Bitcoin's correlation with the S&P 500 against the share of supply held through funds and by public companies | Appendix A.3 |
| `45_euro_table.py` | Table 7 for a euro investor: euro risk-free rate, same premia, volatility in euros | Appendix E.4 |
| **3. The audit** | | |
| `13_model_audit.py` | 1,119 checks: recomputes every number the paper quotes from the model (prints PASS or FAIL per claim) | all sections |

`24_terms_fig.py`, `25_wedge_log.py`, `32_eth_fig.py` and `42_beta_fig.py` draw earlier figures that are not in the paper. All scripts
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
  yield (`data/tnx_monthly.csv`, the CBOE TNX index), from Yahoo Finance, retrieved November 2026. Used for beta and for the equity and gold figures of the paper's Table 7.
- Survey anchors, wealth aggregates, and option-implied figures are quoted in the
  paper from their published sources (Cleveland Fed WP 26-16; Fed SCPC/SHED; Pew;
  OeNB Bulletin Q4/25; UBS GWR; arXiv:2410.15195; Deribit DVOL).
- Code: MIT License. Output tables (`outputs/`): CC BY 4.0, cite the paper.

## Death-definition summary (paper Section 3, Appendix C)

Feed death (feed ends >180 d before dataset end), price death (<1% of ATH, no
recovery), volume death (3-month volume <1% of peak AND <$250k/day, no recovery);
ticker migrations are not deaths (holders received successor tokens); known
catastrophes (LUNA, UST, FTT, SRM, ANC, MIR, CEL) entered at their public-record
dates. The table of every top-twenty death: paper Appendix C.3; machine-readable flags in
`outputs/elite_top20_curated.csv` and `outputs/panel_v3.csv`.

## Citation

> Papadogiannis, A. (2026). "Bitcoin's Required Return." Working paper.
> https://doi.org/10.5281/zenodo.24003938

## Disclaimer

Independent research; no funding, no institutional position. Not investment advice.
