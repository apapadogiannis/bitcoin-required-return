"""Does Bitcoin's equity beta run through use of the network? (Appendix E.2)
Monthly log returns of Bitcoin on those of the S&P 500 (VOO), gold (GLD) and the growth of on-chain activity
(daily active addresses, monthly mean; Coin Metrics community data). Output: activity_beta.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, statsmodels.api as sm, sys
def etf(f):
    x = pd.read_csv(f"{DATA}/{f}_monthly.csv", parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]
    r = np.log(x).diff(); r.index = r.index.to_period("M"); return r
d = pd.read_csv(os.path.join(CSV,"btc.csv"), parse_dates=["time"]).set_index("time")
m = pd.DataFrame({"btc": d.PriceUSD.resample("ME").last(), "act": d.AdrActCnt.resample("ME").mean()}); m.index = m.index.to_period("M")
g = np.log(m).diff(); g["spx"] = etf("voo"); g["gold"] = etf("gld"); g = g["2012-01":"2026-04"].dropna()
out = open(os.path.join(OUT,"activity_beta.txt"), "w")
def p(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
def ols(y, X, lab):
    r = sm.OLS(y, sm.add_constant(X)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    p(f"  {lab:34s}" + ", ".join(f"{k} {r.params[k]:5.2f} (t {r.tvalues[k]:4.1f})" for k in X.columns) + f" | R2 {r.rsquared:.2f}"); return r
res = {}
for lab, s in (("since 2020", g["2020-01":]), ("before 2020", g[:"2019-12"]), ("full sample", g)):
    p(f"{lab}: {len(s)} months; corr(activity growth, equity return) {s.act.corr(s.spx):.2f}; corr(activity growth, Bitcoin return) {s.act.corr(s.btc):.2f}")
    a = ols(s.btc, s[["spx", "gold"]], "btc ~ equity + gold"); b = ols(s.btc, s[["spx", "gold", "act"]], "btc ~ equity + gold + activity")
    l = s.assign(btc1=s.btc.shift(1), act1=s.act.shift(1)).dropna()
    c = ols(l.btc, l[["act1", "btc1"]], "btc ~ lagged activity, lagged btc"); e = ols(l.act, l[["btc1", "act1"]], "activity ~ lagged btc, lagged act")
    res[lab] = (s.act.corr(s.spx), a.params["spx"], b.params["spx"], c.tvalues["act1"], e.tvalues["btc1"])
y = d.assign(fee=d.FeeTotNtv * d.PriceUSD).resample("YE").agg({"AdrActCnt": "mean", "CapMrktCurUSD": "mean", "fee": "sum"}); y.index = y.index.year
y["fee_pct_cap"] = 100 * y.fee / y.CapMrktCurUSD
p("\nyear  active addresses/day  capitalization $bn  fees, % of capitalization")
for k in range(2013, 2026): p(f"{k}  {y.AdrActCnt[k]:12,.0f}  {y.CapMrktCurUSD[k]/1e9:12,.0f}  {y.fee_pct_cap[k]:8.2f}")
p(f"\ncapitalization 2025 / 2017: {y.CapMrktCurUSD[2025]/y.CapMrktCurUSD[2017]:.1f}; active addresses 2025 / 2017: {y.AdrActCnt[2025]/y.AdrActCnt[2017]:.2f}")
out.close()
