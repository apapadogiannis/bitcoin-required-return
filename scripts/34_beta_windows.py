"""Appendix A.2: Bitcoin's beta on the S&P 500 by estimation window (monthly log returns, to May 2026). Output: beta_windows.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd
src = open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])   # the shared block: px (month-end price) and _d (Bitcoin and S&P 500 returns)
def stats(x):
    b = np.cov(x.b, x.s)[0, 1] / x.s.var(); a = x.b.mean() - b * x.s.mean(); e = x.b - a - b * x.s
    return len(x), b, np.sqrt(e.var(ddof=2) / ((x.s - x.s.mean())**2).sum()), x.b.corr(x.s)
out = open(os.path.join(OUT,"beta_windows.txt"), "w")
print(f"last month: {_d.index[-1]:%Y-%m}")
for lab, x in (("Last 2 years", _d.iloc[-24:]), ("Last 3 years", _d.iloc[-36:]), ("Last 4 years", _d.iloc[-48:]), ("Last 5 years", _d.iloc[-60:]),
               ("Since 2020", _d["2020":]), ("Since 2016", _d["2016":]), ("Since 2012", _d["2012":])):
    n, b, se, c = stats(x); s = f"{lab:14s} months {n:3d}  beta {b:.2f}  s.e. {se:.2f}  correlation {c:.2f}"; print(s); out.write(s + "\n")
out.close()
# The same beta against a global equity index (iShares MSCI ACWI ETF), to check the choice of the S&P 500 as the market proxy (Appendix A.1)
_ac = pd.read_csv(os.path.join(DATA,"acwi_monthly.csv"), parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]
_ac.index = _ac.index + pd.offsets.MonthEnd(0)
_dg = pd.DataFrame({"b": _d.b, "s": np.log(_ac).diff(), "sp": _d.s}).dropna()
out = open(os.path.join(OUT,"beta_windows.txt"), "a")
for lab, x in (("Last 4 years", _dg.iloc[-48:]), ("Last 5 years", _dg.iloc[-60:]), ("Since 2020", _dg["2020":]), ("Since 2012", _dg["2012":])):
    n, b, se, c = stats(x); s = f"ACWI {lab:14s} months {n:3d}  beta {b:.2f}  s.e. {se:.2f}  correlation {c:.2f}  corr(ACWI, S&P 500) {x.s.corr(x.sp):.2f}"; print(s); out.write(s + "\n")
out.close()
