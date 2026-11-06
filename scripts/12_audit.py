import os
"""Number audit: recompute every quantitative claim in the manuscript from the
saved panel and print PASS/CHECK lines."""
import numpy as np, pandas as pd
from scipy import stats

OUT = os.environ.get("OUT_DIR","outputs"); YR = 365.25
panel = pd.read_csv(f"{OUT}/panel_v3.csv", parse_dates=["birth", "last", "death_cur_date"])
core = panel[~panel["stable2"] & ~panel["tokstock"] & ~panel["wrapped_like"]].copy()
core = core[(core["last"] - core["birth"]).dt.days >= 30]
dataset_end = panel["last"].max()

def chk(label, got, claimed):
    ok = "PASS" if str(got) == str(claimed) else "** CHECK **"
    print(f"{ok:12s} {label}: computed={got}  manuscript={claimed}")

chk("core universe", len(core), 1815)
chk("curated deaths", int(core["dead_cur"].sum()), 520)
chk("death share %", round(100 * core["dead_cur"].mean()), 29)

# asset-months of life (to dataset end or death)
end = np.where(core["dead_cur"], pd.to_datetime(core["death_cur_date"]),
               dataset_end)
months = ((pd.to_datetime(end) - core["birth"]).dt.days / 30.44).clip(lower=1)
print(f"{'INFO':12s} asset-months (curated exposure): {months.sum():,.0f} (manuscript: 'about 67,700')")

# jump count
chk("jump-collapses in core", int(core["catastrophe"].sum()), 8)

# hazard buckets table 4.1
hb = pd.read_csv(f"{OUT}/hazard_buckets_curated.csv")
merged12 = hb[(hb["a"] >= 1.0) & (hb["b"] <= 2.0)]
chk("deaths age 1-2", int(merged12["deaths"].sum()), 111)
chk("exposure age 1-2", round(merged12["exp"].sum()), 1213)
for a, b, d, e, lam in [(2.0, 3.0, 106, 905, "11.7"), (4.0, 5.0, 78, 488, "16.0"), (7.0, 9.0, 33, 198, "16.7")]:
    row = hb[(hb["a"] == a) & (hb["b"] == b)].iloc[0]
    chk(f"bucket {a}-{b} deaths", int(row["deaths"]), d)
    chk(f"bucket {a}-{b} hazard %", round(100 * row["lam"], 1), lam)

# size quartiles
sz = pd.read_csv(f"{OUT}/hazard_by_size_curated.csv")
for q, lam in [("Q1", 17.4), ("Q2", 13.0), ("Q3", 9.8), ("Q4", 3.2)]:
    row = sz[sz["q"] == q].iloc[0]
    chk(f"size {q} hazard %", round(100 * row["lam"], 1), lam)
    chk(f"size {q} n", int(row["n"]), {"Q1": 452, "Q2": 451, "Q3": 451, "Q4": 452}[q])

# elite
E = pd.read_csv(f"{OUT}/elite_top20_curated.csv")
X = E["exp_yr"].sum(); d = int(E["death"].sum()); dj = int(E["cat"].sum())
chk("elite n", len(E), 219)
chk("elite exposure", round(X), 1017)
chk("elite deaths", d, 36)
chk("elite all-cause %", round(100 * d / X, 2), 3.54)
lo = stats.chi2.ppf(0.025, 2 * d) / 2 / X; hi = stats.chi2.ppf(0.975, 2 * (d + 1)) / 2 / X
chk("elite CI", f"{100*lo:.2f}-{100*hi:.2f}", "2.48-4.90")
chk("jump deaths", dj, 3)
chk("jump hazard %", round(100 * dj / X, 2), 0.30)
lo = stats.chi2.ppf(0.025, 2 * dj) / 2 / X; hi = stats.chi2.ppf(0.975, 2 * (dj + 1)) / 2 / X
chk("jump CI", f"{100*lo:.2f}-{100*hi:.2f}", "0.06-0.86")
contested = {"flow", "icp", "sushi", "nano"}
ds = int(E.loc[~E["asset"].isin(contested), "death"].sum())
chk("excl contested deaths", ds, 32)
chk("excl contested hazard %", round(100 * ds / X, 2), 3.15)

# top-50
E50 = pd.read_csv(f"{OUT}/elite_top50_curated.csv")
X50 = E50["exp_yr"].sum(); d50 = int(E50["death"].sum()); dj50 = int(E50["cat"].sum())
chk("top50 n", len(E50), 499)
chk("top50 hazard %", round(100 * d50 / X50, 1), 5.5)
chk("top50 jump hazard %", round(100 * dj50 / X50, 2), 0.23)

# survival at 14y under elite hazard
import math
print(f"{'INFO':12s} S(14y) at 3.5%: {math.exp(-0.0354*14):.2f} (manuscript: 'around 0.6')")

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
