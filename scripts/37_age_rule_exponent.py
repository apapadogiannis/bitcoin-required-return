"""Appendix D.2 and D.3: the age rule with its exponent re-estimated in real time.
The paper holds the power-law exponent at 5.62 at every date. Here it is re-estimated at each month-end by least squares of
log price on log age, on the daily prices available up to that date, and the age-rule comparisons are recomputed.
Output: age_rule_exponent.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd
src = open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
d = pd.read_csv(os.path.join(CSV,"btc.csv"), parse_dates=["time"]).set_index("time")["PriceUSD"].dropna()
if d.index.tz is not None: d.index = d.index.tz_localize(None)
fit = lambda x: np.polyfit(np.log((x.index - GEN).days/365.25), np.log(x.values), 1)[0]
bt = pd.Series({t: fit(d[:t]) for t in px.index if t >= pd.Timestamp("2011-12-31")}).reindex(px.index)
out = open(os.path.join(OUT,"age_rule_exponent.txt"), "w")
def p(s=""):
    print(s); out.write(s + "\n")
p("real-time exponent: " + ", ".join(f"{t[:4]} {bt[t]:.2f}" for t in ("2012-01-31", "2013-06-30", "2014-12-31", "2016-12-31", "2018-12-31", "2020-12-31", "2022-12-31", "2024-12-31", "2026-04-30")))
p(f"range 2012-14: {bt['2012':'2014'].min():.2f}-{bt['2012':'2014'].max():.2f}; 2015: {bt['2015'].min():.2f}-{bt['2015'].max():.2f}; since 2016: {bt['2016':].min():.2f}-{bt['2016':].max():.2f}; full sample to May 2026: {bt.iloc[-1]:.2f}")
D = pd.DataFrame({"r": px.shift(-1)/px - 1, "fix": ((age + 1/12)/age)**5.62 - 1, "rt": ((age + 1/12)/age)**bt - 1}).dropna(); D = D[D.index >= "2012-01-01"]
p("\nmonthly test, delivered minus age rule (points a year): exponent fixed at 5.62 | re-estimated each month")
for a, b in (("2012", "2026"), ("2012", "2014"), ("2015", "2017"), ("2018", "2020"), ("2021", "2023"), ("2024", "2026"), ("2012", "2017"), ("2018", "2026")):
    s = D[a:b]; p(f"  {a}-{b[2:]}: {1200*(s.r - s.fix).mean():+5.0f} | {1200*(s.r - s.rt).mean():+5.0f}")
W = pd.DataFrame({"f": fwd_mu, "mid": req_mid, "fix": (1 + 5/age)**(5.62/5) - 1, "rt": (1 + 5/age)**(bt/5) - 1}).dropna()["2012":]
p(f"\nfive-year windows ({len(W)}): mean absolute miss, correlation with the realized average, share of windows closer than the midpoint")
for k in ("mid", "fix", "rt"):
    p(f"  {k:3s}: {100*(W.f - W[k]).abs().mean():3.0f} points, {W.f.corr(W[k]):.2f}" + ("" if k == "mid" else f", {100*((W.f - W[k]).abs() < (W.f - W.mid).abs()).mean():.0f}%"))
out.close()
