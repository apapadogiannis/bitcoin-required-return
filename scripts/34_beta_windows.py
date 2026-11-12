"""Appendix A.2: Bitcoin's beta on the S&P 500 by estimation window (monthly log returns, to May 2026). Output: beta_windows.txt"""
import numpy as np, pandas as pd
src = open("/home/claude/model/22_pretty_figs.py").read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])   # the shared block: px (month-end price) and _d (Bitcoin and S&P 500 returns)
def stats(x):
    b = np.cov(x.b, x.s)[0, 1] / x.s.var(); a = x.b.mean() - b * x.s.mean(); e = x.b - a - b * x.s
    return len(x), b, np.sqrt(e.var(ddof=2) / ((x.s - x.s.mean())**2).sum()), x.b.corr(x.s)
out = open("/home/claude/model/beta_windows.txt", "w")
print(f"last month: {_d.index[-1]:%Y-%m}")
for lab, x in (("Last 2 years", _d.iloc[-24:]), ("Last 3 years", _d.iloc[-36:]), ("Last 4 years", _d.iloc[-48:]), ("Last 5 years", _d.iloc[-60:]),
               ("Since 2020", _d["2020":]), ("Since 2016", _d["2016":]), ("Since 2012", _d["2012":])):
    n, b, se, c = stats(x); s = f"{lab:14s} months {n:3d}  beta {b:.2f}  s.e. {se:.2f}  correlation {c:.2f}"; print(s); out.write(s + "\n")
out.close()
