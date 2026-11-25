# Bitcoin's Required Return: Market Risk, Concentration and Mortality

[![Zenodo](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.24003938-007ec6)](https://doi.org/10.5281/zenodo.24003938)
[![SSRN](https://img.shields.io/badge/SSRN-10.2139%2Fssrn.7705239-1f4e79)](https://doi.org/10.2139/ssrn.7705239)
[![replication](https://github.com/apapadogiannis/bitcoin-required-return/actions/workflows/replicate.yml/badge.svg)](https://github.com/apapadogiannis/bitcoin-required-return/actions/workflows/replicate.yml)

Replication package for the working paper by Agisilaos Papadogiannis (November 2026).
Paper: `paper/manuscript.pdf`; preprint on SSRN: [doi:10.2139/ssrn.7705239](https://doi.org/10.2139/ssrn.7705239).
Archived on Zenodo: [doi:10.5281/zenodo.24003938](https://doi.org/10.5281/zenodo.24003938) (concept DOI, always resolves to the latest version; each release also has its own DOI, listed on the Zenodo record).
Current version: 3.0.0 (November 25, 2026), paper and replication package.

## Changes since version 2.0.0

Version 3.0.0 measures the holder weight differently, so printed numbers change.

- The subtitle changes to "Market Risk, Concentration and Mortality", the three terms of the equation
  (it was "Pricing a New Asset Beside Equities and Gold").
- The surveyed owners' portfolio weight is held at its survey value, 19% of financial assets, at every
  date. Before, owners' wealth was carried from its 2021 value with the ownership rate and an assumed
  path of wealth per owner, so the weight followed Bitcoin's market value (0.7% in 2012, 80% at the
  end of 2017, 34% in mid-2025). Surveys that ask owners what their holdings are worth show holdings
  per owner moving little with the price (UK Financial Conduct Authority, four waves; Bank of Canada,
  five waves): a higher market value shows up as more owners.
- For 2026 the range of the holder weight is 7 to 19% (it was 8 to 19%) and the required return 18.1%
  a year, 90% range 15.2 to 21.8% (18.3%, 15.4 to 21.9%); compounded, 9.3% (9.5%).
- The monthly test since 2018 is unchanged in substance: the gap between delivered and required
  returns is 15 points a year (standard error 23), and the MCM equation explains 94% of Bitcoin's excess
  return (96%). Over 2012 to 2017 the lower edge of the band is higher (44% on average, it was 25%) and
  the gap to the midpoint is 101 points (109). Over five-year windows the correlation of the required
  return with the return that followed is 0.43 (0.28).
- Affected: the abstract, Sections 4 to 8, Tables 3 to 7, Figures 1 to 3 and 5, Appendices B and D
  (Tables 15 and 16), and the euro table of Appendix E (Table 17).
- New: `data/holder_surveys.csv` with its sources, `scripts/49_holder_surveys.py` and
  `scripts/50_holder_weight_variants.py` (the weight at 12% and at 8%, and the earlier construction, side by
  side). Removed: `28_cryptowide_backcast.py` and `36_ownership_sensitivity.py`, whose results applied to
  the earlier construction.

## Changes in version 2.0.0 (since 1.1.2)

Version 2.0.0 corrects the census of cryptoasset deaths, so printed numbers change. The required
return for Bitcoin and the tables of Sections 4, 5 and 7 are unchanged.

- The census now leaves out what the paper says it leaves out. Assets without a price history could
  not be identified by the price test and are named one by one: the Lithuanian litas (a national
  currency), 116 tokenized shares and funds, three gold tokens, 57 stablecoins, and 17 wrapped copies
  or second files of an asset. A further 27 ticker changes and token swaps, each confirmed by an
  announcement, are no longer counted as deaths. The census has 1,624 assets and 471 deaths (it had
  1,815 and 520); among the assets ever in the top twenty, 35 deaths in 216 assets, 3.46% a year
  (36 in 219, 3.54%). The mortality term stays at 0.3 to 3.5 points.
- Affected: Table 1 (which gains the rates with the census ended at December 2024), Section 6 and
  Table 6 (77 priced cryptoassets instead of 84; the altcoin columns), and the tables and figures of
  Appendix C. The age elasticity of the death rate is +0.36 (it was +0.42).
- The rolling beta is estimated from January 2012 on the months available. Before, the estimate of
  July 2012 was also used for the six months before it. No printed number of the monthly test changes.
- New results: `outputs/age_elasticity.txt` (the table of age elasticities, now reproduced in full)
  and `outputs/earlier_censuses.txt` (death rates by calendar year, and the census retaken at earlier
  dates).

## For AI agents and programs

Read [`llms.txt`](llms.txt) first. It says what the package holds, what it adds over reading the
paper or recomputing, which file to use and what not to use it for. To quote a number of the paper,
use [`outputs/results.json`](outputs/results.json): it lists every figure the paper quotes that the
code recomputes (1,322 of them), each with the computed value and the paper's figure, opens with a
short `headline` list of the figures most often asked for, and carries
the paper, the identifiers, the version, the licence and the citation under its `package` key. Both
files are written by the pipeline (`12_audit.py`, `13_model_audit.py`, `make_guide.py`) and both are
covered by the check. The same equation, recomputed each month from live sources, is at the
[Crypto Observatory](https://apapadogiannis.github.io/crypto-observatory/).

## What this is

The paper asks what return Bitcoin's holders should require, given the risks they bear, and checks the answer against what Bitcoin delivered.

1. **The MCM equation.** The required return is the risk-free rate plus three risk terms:
   market risk (beta to the S&P 500 times the equity risk premium), concentration risk (risk
   aversion times variance times the share of wealth that holders keep in the asset, from the
   Cleveland Fed household survey, held at its survey value) and mortality risk (from the census below).
   For 2026: about 18% a year on average (90% range 15–22%), about 9.3% compounded.
2. **The census of deaths.** Survival analysis of 1,624 cryptoassets (2010–2026, 471
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
llms.txt    guide for AI agents and programs, generated; guide.toml holds its statements about this package
data/       all input data: the Coin Metrics snapshot the paper used (data/cmdata), ETF price files (VOO, ACWI, VT, QQQ, IWM,
            GLD), EUR/USD, the Treasury yield and the survey figures on what owners hold (see Data and licensing)
```

## Reproducing

Requirements: Python 3.11+, `pip install -r requirements.txt` (pandas, numpy, lifelines,
statsmodels, scipy, matplotlib). `requirements-lock.txt` lists
the exact versions under which `outputs/` were generated.

```bash
./run_all.sh    # about three minutes; no downloads
```

All input data are in the repository, so the script needs no network access; it runs every
step below in order. Re-running
reproduces every result file in `outputs/` (see "How the check works"). A GitHub Actions workflow does this on
every push and monthly, and fails if a script stops, a data file differs from its recorded checksum, any stored result is not reproduced or any audit line is not PASS; the
badge above shows the latest run.

| Script | What it produces | Where it appears |
|---|---|---|
| **1. The census of cryptoasset deaths** | | |
| `03_rebuild_panel.py` | Birth and death panel from the Coin Metrics asset files | Section 3 |
| `05_size_elite.py` | Monthly volume matrix; size quartiles and ever-top-N cohorts | Section 3 (Table 1), Appendix C.2 |
| `06_voldeath.py` | Volume-collapse deaths; unified death definition | Section 3, Appendix C |
| `07_curated.py` | Migrations and dated collapses; `panel_v3.csv`, hazards, the elite death table | Section 3, Appendix C.3 |
| `08_cohorts.py` | Buy-at-birth cohort returns | Appendix C |
| `10_robustness.py` | The age elasticity under each definition of death, cohort fixed effects, Weibull and log-logistic fits (`outputs/age_elasticity.txt`) | Appendix C.4 |
| `12_audit.py` | 94 checks of the census numbers quoted in the paper | Section 3, Appendix C |
| `09_figures.py`, `11_km_figure.py`, `21_final_figs.py` | Draft figures and `wedge_table.csv` from an earlier calibration, kept for the record | not in the paper |
| **2. The required-return model** | | |
| `22_pretty_figs.py` | The shared construction of the required-return band (inputs, holder weight, edges), used by the scripts below; hazard and survival figures. The surveyed owners' weight is held at 19%; the environment variables `W_OWNERS` (another weight) and `W_PATH=constructed` (a weight that follows the market value) give the alternatives of Appendix D.4 | Sections 3 and 5, Appendix C |
| `23_uncertainty.py` | Propagation of the input ranges; sensitivities | Section 4 (Table 3), Section 6 (Table 6), Appendices D.1 and E.1 |
| `26_holder_weight.py` | The holders through time and their figure: the share of adults who own crypto, and what owners hold against Bitcoin's price in the survey waves | Appendix B, Appendix D.3 |
| `27_monthly_test.py` | The monthly test and its figure | Section 5 (Table 5, Figure 3) |
| `29_required_fig.py` | The required return since 2012; `required_band_monthly.csv` | Section 5 (Figure 2) |
| `30_inputs_fig.py` | The inputs that move with time | Section 5 (Figure 1) |
| `31_cross_section.py` | Ether and other cryptoassets: the holder weight of each asset (crypto share times kappa), the term-by-term sums, delivered returns | Section 6 (Table 6) |
| `33_activity_beta.py` | On-chain activity and the equity beta | Appendix A.3 |
| `34_beta_windows.py` | Beta by estimation window and against a global index; correlation by sub-period | Appendix A.2 and A.3 |
| `35_option_bound.py` | Option-implied cap on the probability of a collapse | Appendix C.5 |
| `37_age_rule_exponent.py`, `38_grouping_robustness.py` | Real-time age-rule exponent; other groupings of the monthly test | Appendix D.2 and D.3 |
| `39_index_exposure.py` | Bitcoin exposure inside the S&P 500 | Appendix A.6 |
| `40_death_date_check.py` | Collapse dates moved within their documented windows | Appendix C.3 |
| `41_volatility_table.py` | Volatility by window and by currency | Appendix A.7 |
| `43_band_table.py` | The band worked out at five dates: inputs, both candidates for the upper edge, midpoint | Section 5 (Table 4) |
| `44_holders_and_comovement.py` | Bitcoin's correlation with the S&P 500 against the share of supply held through funds and by public companies | Appendix A.3 |
| `45_euro_table.py` | Table 7 for a euro investor: euro risk-free rate, same premia, volatility in euros | Appendix E.4 |
| `46_adoption_hazard.py` | Death within two years by trading volume, as a measure of adoption | Appendix C.2 |
| `47_equity_premium.py` | The band and the monthly test with the equity premium implied by stock prices month by month, and with fixed 3% to 6% | Robustness to Section 4 (revision; not in the public package) |
| `48_earlier_censuses.py` | Death rates by calendar year, the rates of Table 1 with the census ended at December 2024, and the census retaken at earlier dates (`outputs/earlier_censuses.txt`) | Table 1, Appendix C.4 |
| `49_holder_surveys.py` | Holdings per owner against Bitcoin's price in repeated surveys (UK Financial Conduct Authority, Bank of Canada), from `data/holder_surveys.csv` (`outputs/holder_surveys.txt`) | Section 4, Appendix B.2 |
| `50_holder_weight_variants.py` | The band, the monthly test and the five-year comparison with the owners' weight at 12% and 8%, with a weight that follows the market value, and with another ownership path (`outputs/holder_weight_variants.txt`) | Appendix D.4 |
| **3. The audit** | | |
| `13_model_audit.py` | 1,228 checks: recomputes every number the paper quotes from the model (prints PASS or FAIL per claim) | all sections |
| **4. For programs** | | |
| `make_guide.py` | The `package` header of `outputs/results.json` (the checks of `12_audit.py` and `13_model_audit.py` as data) and `llms.txt` | not in the paper |

`24_terms_fig.py`, `25_wedge_log.py`, `32_eth_fig.py` and `42_beta_fig.py` draw earlier figures that are not in the paper. All scripts
locate `data/`, `outputs/` and `figures/` relative to the repository; the environment variables
`DATA_DIR`, `OUT_DIR`, `FIG_DIR` and `CM_CSV_DIR` override them.

## How the check works

```bash
python3 check_outputs.py --also llms.txt    # reruns ./run_all.sh, then compares
```

1. The result tables and audit files in `outputs/` are stored in this repository exactly as they were when the
   paper's numbers were taken from them.
2. `check_outputs.py` sets the stored copies aside, reruns `./run_all.sh` on the files in `data/`,
   and compares the fresh files with the stored ones, number by number.
3. A number counts as reproduced if it agrees with the stored one to nine significant digits
   (relative tolerance 1e-9). Text, labels and whole numbers must match exactly. Any other
   difference is listed and the check fails.

Why a tolerance and not a character-by-character match: the last digits of a floating-point
result depend on the processor and on the build of the numerical libraries, so two correct runs
on different machines can differ in the 12th to 16th significant digit. The check reports
how many numbers differed in this way and by how much. For the same reason, a value printed with
a fixed number of decimals may differ by one unit in its last printed place; such cases are listed.

The workflow behind the badge runs the pipeline on a new machine with the pinned package
versions, on every push and once a month, and applies the same comparison. The stored results
are also frozen in the Zenodo archive, which cannot be altered after release.

Two limits. The comparison is between regenerated and stored results, not with the paper's
PDF: to connect the two, use the script table above, which says where each output appears in
the paper. And figures are redrawn from the same values but are not compared, because image files can
differ slightly between versions of the plotting library.

## Data and licensing

- Crypto price, volume and network data (`data/cmdata/csv`, 2,258 asset files): the
  [Coin Metrics community dataset](https://github.com/coinmetrics/data), by Coin Metrics, Inc.,
  licensed [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (non-commercial use,
  with attribution; licence notice in `data/cmdata/LICENSE`). The files are an unmodified copy of
  the `csv/` directory at upstream commit `f1a36afb962731c387bb03982758ab0103063da5`
  ("Update CSV 2026-05-24", data ending 2026-05-24), kept here so that the paper's results do not
  depend on the upstream archive. The archive stopped updating on 24 May 2026, and this snapshot is
  its last commit. `data/cmdata/MANIFEST.sha256` lists
  the checksum of every file: `cd data/cmdata && sha256sum --quiet -c MANIFEST.sha256`.
- ETF prices (`data/voo_monthly.csv`, `data/acwi_monthly.csv`, `data/vt_monthly.csv`,
  `data/qqq_monthly.csv`, `data/iwm_monthly.csv`, `data/gld_monthly.csv`): monthly adjusted close
  (and close, where given) of the Vanguard S&P 500 ETF, the iShares MSCI ACWI ETF, the Vanguard
  Total World Stock ETF, the Invesco QQQ (Nasdaq-100), the iShares Russell 2000 ETF, and SPDR Gold Shares, the
  month-end euro/dollar rate (`data/eurusd_monthly.csv`) and the month-end ten-year Treasury
  yield (`data/tnx_monthly.csv`, the CBOE TNX index), from Yahoo Finance, retrieved November 2026. Used for beta and for the equity and gold figures of the paper's Table 7.
- Holdings per owner in repeated household surveys (`data/holder_surveys.csv`): figures read from the published
  reports of the UK Financial Conduct Authority (cryptoasset consumer research, waves 2 to 5, and its freedom of
  information response FOI2025/00604) and of the Bank of Canada (Staff Discussion Papers 2022-10, 2023-14 and 2025-4),
  on 25 November 2026. `data/holder_surveys_SOURCE.md` gives each source, its address and what each column is.
- Other survey anchors, wealth aggregates, and option-implied figures are quoted in the
  paper from their published sources (Cleveland Fed WP 26-16; Fed SCPC/SHED; Pew;
  OeNB Bulletin Q4/25; UBS GWR; arXiv:2410.15195; Deribit DVOL).
- Code: MIT License. Output tables (`outputs/`): CC BY 4.0, cite the paper. The Coin Metrics
  files in `data/cmdata` keep their own licence (CC BY-NC 4.0) and are not covered by either.

## Death-definition summary (paper Section 3, Appendix C)

Feed death (feed ends >180 d before dataset end), price death (<1% of ATH, no
recovery), volume death (3-month volume <1% of peak AND <$250k/day, no recovery);
ticker migrations are not deaths (holders received successor tokens); known
catastrophes (LUNA, UST, FTT, SRM, ANC, MIR, CEL) entered at their public-record
dates. The table of every top-twenty death: paper Appendix C.3; machine-readable flags in
`outputs/elite_top20_curated.csv` and `outputs/panel_v3.csv`.

## Citation

> Papadogiannis, A. (2026). "Bitcoin's Required Return: Market Risk, Concentration and Mortality." Working paper, version 3.0.
> SSRN: https://doi.org/10.2139/ssrn.7705239

Code and data:

> Papadogiannis, A. (2026). "Bitcoin's Required Return: replication package." Zenodo.
> https://doi.org/10.5281/zenodo.24003938

## Disclaimer

Independent research; no funding, no institutional position. Not investment advice.
