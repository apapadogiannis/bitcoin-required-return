import os
"""Census audit: recompute the census numbers quoted in the paper (Section 3, Appendix C) from the
saved panel and print PASS/CHECK lines."""
import numpy as np, pandas as pd
from scipy import stats

OUT = os.environ.get("OUT_DIR","outputs"); YR = 365.25
panel = pd.read_csv(f"{OUT}/panel_v3.csv", parse_dates=["birth", "last", "death_cur_date"])
core = panel[~panel["stable2"] & ~panel["tokstock"] & ~panel["wrapped_like"]].copy()
core = core[(core["last"] - core["birth"]).dt.days >= 30]
dataset_end = panel["last"].max()

records = []          # every check, for outputs/results.json
def _plain(v):
    v = v.item() if hasattr(v, "item") else v
    try:
        return float(v) if isinstance(v, str) else v      # "16.0" is a number; "2.48-4.90" stays text
    except ValueError:
        return v

def chk(label, got, claimed):
    ok = "PASS" if str(got) == str(claimed) else "** CHECK **"
    records.append({"claim": label, "computed": _plain(got), "paper": _plain(claimed)})
    print(f"{ok:12s} {label}: computed={got}  manuscript={claimed}")

chk("core universe", len(core), 1624)
chk("curated deaths", int(core["dead_cur"].sum()), 471)
chk("death share %", round(100 * core["dead_cur"].mean()), 29)

# asset-months of life (to dataset end or death)
end = np.where(core["dead_cur"], pd.to_datetime(core["death_cur_date"]),
               dataset_end)
months = ((pd.to_datetime(end) - core["birth"]).dt.days / 30.44).clip(lower=1)
print(f"{'INFO':12s} asset-months (curated exposure): {months.sum():,.0f} (manuscript: 'about 65,400')")

# jump count
chk("jump-collapses in core", int(core["catastrophe"].sum()), 8)

# hazard buckets table 4.1
hb = pd.read_csv(f"{OUT}/hazard_buckets_curated.csv")
merged12 = hb[(hb["a"] >= 1.0) & (hb["b"] <= 2.0)]
chk("deaths age 1-2", int(merged12["deaths"].sum()), 104)
chk("exposure age 1-2", round(merged12["exp"].sum()), 1169)
for a, b, d, e, lam in [(2.0, 3.0, 100, 875, "11.4"), (4.0, 5.0, 69, 482, "14.3"), (7.0, 9.0, 31, 205, "15.1")]:
    row = hb[(hb["a"] == a) & (hb["b"] == b)].iloc[0]
    chk(f"bucket {a}-{b} deaths", int(row["deaths"]), d)
    chk(f"bucket {a}-{b} hazard %", round(100 * row["lam"], 1), lam)

# size quartiles
sz = pd.read_csv(f"{OUT}/hazard_by_size_curated.csv")
for q, lam in [("Q1", 16.2), ("Q2", 12.8), ("Q3", 7.9), ("Q4", 2.8)]:
    row = sz[sz["q"] == q].iloc[0]
    chk(f"size {q} hazard %", round(100 * row["lam"], 1), lam)
    chk(f"size {q} n", int(row["n"]), {"Q1": 406, "Q2": 406, "Q3": 405, "Q4": 406}[q])

# elite
E = pd.read_csv(f"{OUT}/elite_top20_curated.csv")
X = E["exp_yr"].sum(); d = int(E["death"].sum()); dj = int(E["cat"].sum())
chk("elite n", len(E), 216)
chk("elite exposure", round(X), 1011)
chk("elite deaths", d, 35)
chk("elite all-cause %", round(100 * d / X, 2), 3.46)
lo = stats.chi2.ppf(0.025, 2 * d) / 2 / X; hi = stats.chi2.ppf(0.975, 2 * (d + 1)) / 2 / X
chk("elite CI", f"{100*lo:.2f}-{100*hi:.2f}", "2.41-4.81")
chk("jump deaths", dj, 3)
chk("jump hazard %", round(100 * dj / X, 2), 0.30)
lo = stats.chi2.ppf(0.025, 2 * dj) / 2 / X; hi = stats.chi2.ppf(0.975, 2 * (dj + 1)) / 2 / X
chk("jump CI", f"{100*lo:.2f}-{100*hi:.2f}", "0.06-0.87")
contested = {"flow", "icp", "sushi", "nano"}
ds = int(E.loc[~E["asset"].isin(contested), "death"].sum())
chk("excl contested deaths", ds, 31)
chk("excl contested hazard %", round(100 * ds / X, 2), 3.07)

# top-50
E50 = pd.read_csv(f"{OUT}/elite_top50_curated.csv")
X50 = E50["exp_yr"].sum(); d50 = int(E50["death"].sum()); dj50 = int(E50["cat"].sum())
chk("top50 n", len(E50), 493)
chk("top50 hazard %", round(100 * d50 / X50, 1), 5.0)
chk("top50 jump hazard %", round(100 * dj50 / X50, 2), 0.23)

# survival at 14y under elite hazard
import math
print(f"{'INFO':12s} S(14y) at 3.5%: {math.exp(-0.0347*14):.2f} (manuscript: 'around 0.6')")

# cumulative Pareto khat from KM slope: recompute
from lifelines import KaplanMeierFitter
T = np.where(core["dead_cur"],
             (pd.to_datetime(core["death_cur_date"]) - core["birth"]).dt.days / YR,
             (dataset_end - core["birth"]).dt.days / YR)
T = np.clip(T, 1/365.25, None)
km = KaplanMeierFitter().fit(T, core["dead_cur"].astype(int))
sf = km.survival_function_
t = sf.index.values; s = sf.iloc[:, 0].values
m = (t >= 1) & (t <= 10) & (s > 0)
sl = np.polyfit(np.log(t[m]), np.log(s[m]), 1)[0]
print(f"{'INFO':12s} KM log-log slope 1-10y (curated): {sl:.2f} (manuscript: -0.21 (strict) to -0.49 (curated))")

# cohort numbers quoted in Sec 6
res = np.load(f"{OUT}/cohort_res.npy", allow_pickle=True).item()
r = res["2010-14"]
i = 120
print(f"{'INFO':12s} 2010-14 cohort mean CAGR @10y: {r['mean'][i]**(1/10)-1:+.0%} (manuscript +167%)")
print(f"{'INFO':12s} 2010-14 cohort median CAGR @10y: {r['med'][i]**(1/10)-1:+.0%} (manuscript +50%)")
import pandas as pd
PM = pd.read_pickle(f"{OUT}/prices_monthly.pkl")
btc = PM["btc"].dropna(); mult10 = btc.iloc[120] / btc.iloc[0]
print(f"{'INFO':12s} BTC CAGR @10y from first price: {mult10**(1/10)-1:+.0%} (manuscript +233%)")

# ---- further numbers quoted in Section 3 and Appendix C ----
chk("S3 assets with a price history of 90 days or more", int((core["n_px"] >= 90).sum()), 79)
chk("S3 feed ended, before curation", int(core["feed_dead"].sum()), 220)
chk("S3 price below 1% of its peak, before curation", int(core["econ_dead"].fillna(False).astype(bool).sum()), 25)
chk("S3 volume collapsed, before curation", int(core["vol_dead_c"].sum()), 374)
chk("S3 asset-months, rounded to hundreds", int(round(months.sum(), -2)), 65400)
chk("Table 1 quarters: assets", int(sz["n"].sum()), 1623)
chk("Table 1 quarters: deaths", int(sz["deaths"].sum()), 471)
for q, dq in [("Q1", 158), ("Q2", 148), ("Q3", 110), ("Q4", 55)]:
    chk(f"size {q} deaths", int(sz.loc[sz["q"] == q, "deaths"].iloc[0]), dq)
for a_, b_, d_, e_, l_ in [(0.1, 0.5, 4, 641, "0.6"), (0.5, 1.0, 36, 736, "4.9"), (3.0, 4.0, 71, 643, "11.0"), (5.0, 7.0, 52, 501, "10.4"), (9.0, 12.0, 4, 53, "7.5")]:
    row = hb[(hb["a"] == a_) & (hb["b"] == b_)].iloc[0]
    chk(f"bucket {a_}-{b_} deaths", int(row["deaths"]), d_); chk(f"bucket {a_}-{b_} exposure", round(row["exp"]), e_)
    chk(f"bucket {a_}-{b_} hazard %", f"{100 * row['lam']:.1f}", l_)
chk("bucket 1-2 hazard %", f"{100 * merged12['deaths'].sum() / merged12['exp'].sum():.1f}", "8.9")
chk("C.1 exposure in the brackets shown, rounded to tens", int(round(hb.loc[hb["a"] < 12, "exp"].sum(), -1)), 5300)
_yrs = ((pd.to_datetime(end) - core["birth"]).dt.days / YR).sum()
chk("C.1 exposure of the census, rounded to tens", int(round(_yrs, -1)), 5450)
_E = E.copy(); _E["death_date"] = pd.to_datetime(_E["death_date"])
_d25 = int((_E["death_date"].dt.year == 2025).sum()); chk("C.1 top-twenty deaths in 2025", _d25, 11)
chk("C.1 top-twenty deaths in 2022", int((_E["death_date"].dt.year == 2022).sum()), 9)
def _ci(n_, x_): return f"{100 * stats.chi2.ppf(0.025, 2 * n_) / 2 / X:.2f}-{100 * stats.chi2.ppf(0.975, 2 * (n_ + 1)) / 2 / X:.2f}"
chk("C.3 excl contested CI", _ci(ds, X), "2.08-4.35")
chk("C.3 without the 2025 deaths, hazard %", round(100 * (d - _d25) / X, 2), 2.37); chk("C.3 without the 2025 deaths, CI", _ci(d - _d25, X), "1.52-3.53")
_xu = X - float(_E.loc[_E["asset"] == "ust", "exp_yr"].iloc[0])
chk("C.3 without TerraUSD, hazard %", round(100 * (d - 1) / _xu, 2), 3.36); chk("C.3 without TerraUSD, sudden collapses %", round(100 * (dj - 1) / _xu, 2), 0.20)
chk("C.2 top50 deaths", d50, 109)
chk("C.2 top50 CI", f"{100 * stats.chi2.ppf(0.025, 2 * d50) / 2 / X50:.1f}-{100 * stats.chi2.ppf(0.975, 2 * (d50 + 1)) / 2 / X50:.1f}", "4.1-6.1")
chk("C.3 left out: tokenized shares, funds and gold", int(panel["tokstock"].sum()), 228)
chk("C.3 left out: wrapped, staked and second files", int(panel["wrapped_like"].sum()), 38)
chk("C.3 left out: stablecoins", int(panel["stable2"].sum()), 73)
chk("C.3 left out: observed for less than thirty days", int(((panel["last"] - panel["birth"]).dt.days < 30)[~panel["stable2"] & ~panel["tokstock"] & ~panel["wrapped_like"]].sum()), 54)
_dy = pd.to_datetime(core.loc[core["dead_cur"], "death_cur_date"]).dt.year
chk("C.4 deaths dated 2025", int((_dy == 2025).sum()), 240); chk("C.4 deaths dated 2026", int((_dy == 2026).sum()), 94)
_mech = core["feed_dead"] | core["vol_dead_c"] | core["econ_dead"].fillna(False).astype(bool)
chk("S3 migrations among the assets the rules count as dead", int((core["migration"] & _mech).sum()), 48)
_ec = open(f"{OUT}/earlier_censuses.txt").read()
def _row(label): return [l for l in _ec.splitlines() if l.strip().startswith(label)][0].split(":", 1)[1].replace("|", " ").split()
for _lab, _v24 in (("smallest quarter", "6.7"), ("second quarter", "5.5"), ("third quarter", "4.1"), ("largest quarter", "1.0"), ("ever top twenty", "2.58"), ("sudden collapses", "0.39"), ("all assets", "3.6")):
    chk(f"Table 1, census to December 2024: {_lab}", _row(_lab)[1], _v24)
chk("C.4 all assets, whole census, % a year", _row("all assets")[3], "8.6"); chk("C.4 deaths to December 2024", _row("all assets")[0], "137"); chk("C.3 top-twenty deaths to December 2024", _row("ever top twenty")[0], "20")
_yr = {l.split(":")[0].strip(): l.split()[-1] for l in _ec.splitlines() if l.strip()[:4].isdigit() and l.strip()[4] == ":"}
chk("C.4 death rate 2025, % a year", _yr["2025"], "20.2"); chk("C.4 death rate 2026, % a year", _yr["2026"], "16.7"); chk("C.4 highest yearly death rate to 2024", max(float(_yr[str(y)]) for y in range(2018, 2025)), 6.1)
_late = [l for l in _ec.splitlines() if l.startswith("Deaths dated 2025 or 2026")][0]
chk("C.4 late deaths", _late.split(":")[1].split()[0], "334"); chk("C.4 late deaths: feed ended", _late.split("feed ended")[1].split(";")[0].strip(), "107"); chk("C.4 late deaths: volume alone", _late.split("volume rule alone")[1].split(",")[0].strip(), "214")

# The checks above, as data: outputs/results.json (13_model_audit.py adds the model's checks to it).
import json
with open(f"{OUT}/results.json", "w", encoding="utf-8") as _f:
    json.dump({"census_checks": records}, _f, indent=2, ensure_ascii=False)
