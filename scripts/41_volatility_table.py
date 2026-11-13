"""Appendix A.7: how volatility is measured for every asset of Table 7, and how it changes with the window and the currency.
Monthly log returns (total-return ETFs for the equity indices and gold; Coin Metrics prices for Bitcoin and Ether), annualized with sqrt(12).
Windows end in April 2026. 'Recent months weighted' is the paper's measure for Bitcoin and Ether: squared returns, exponentially
weighted with a half-life of nine months. Euro figures convert each return at the month-end EUR/USD rate. Output: volatility_table.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, io, contextlib, runpy
def etf(f):
    z = pd.read_csv(f, parse_dates=["Date"]).sort_values("Date").set_index("Date"); z = z["AdjClose"] if "AdjClose" in z else z["Close"]
    z.index = z.index + pd.offsets.MonthEnd(0); return np.log(z).diff()
src = open(os.path.join(SCRIPTS, "22_pretty_figs.py")).read(); exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
with contextlib.redirect_stdout(io.StringIO()): cs = runpy.run_path(os.path.join(SCRIPTS, "31_cross_section.py"))
D = pd.DataFrame({"Global equities (ACWI)": etf(os.path.join(DATA, "acwi_monthly.csv")), "S&P 500": etf(os.path.join(DATA, "voo_monthly.csv")), "Nasdaq-100": etf(os.path.join(DATA, "qqq_monthly.csv")),
                  "Russell 2000": etf(os.path.join(DATA, "iwm_monthly.csv")), "Gold": etf(os.path.join(DATA, "gld_monthly.csv")), "Bitcoin": np.log(px).diff(), "Ether": np.log1p(cs["Rn"]["eth"])})
fx = etf(os.path.join(DATA, "eurusd_monthly.csv"))                      # log change of the dollar price of one euro
def table(X, end="2026-04"):
    X = X[:end]; o = {"2012-01 to 2026-04": X["2012-01":].std() * 12**.5}
    for y in (5, 3, 1): o[f"last {y}y"] = X.iloc[-12 * y:].std() * 12**.5
    o["recent months weighted"] = np.sqrt(X.pow(2).ewm(halflife=9).mean().iloc[-1] * 12)
    return (100 * pd.DataFrame(o)).round(1)
out = open(os.path.join(OUT, "volatility_table.txt"), "w")
def line(s=""):
    print(s); out.write(s + "\n")
line("US dollars"); line(table(D).to_string())
line(); line("Euros"); line(table(D.sub(fx.reindex(D.index), axis=0)).iloc[:2].to_string())
line(); line(f"Bitcoin, recent months weighted, May 2026: {100*np.sqrt(D['Bitcoin'][:'2026-05'].pow(2).ewm(halflife=9).mean().iloc[-1]*12):.1f}")
X = D["2012-01":"2026-04"]
line(f"EUR/USD volatility 2012-01 to 2026-04: {100*fx['2012-01':'2026-04'].std()*12**.5:.1f}; correlation of the euro's monthly change with returns: ACWI {X.iloc[:,0].corr(fx):.2f}, S&P 500 {X.iloc[:,1].corr(fx):.2f}")
for lab, x in (("2012-01 to 2026-04", X), ("since 2020", X["2020":])):
    g = x[["Gold", "S&P 500"]].dropna(); b = g.cov().iloc[0, 1] / g["S&P 500"].var(); e = g["Gold"] - g["Gold"].mean() - b * (g["S&P 500"] - g["S&P 500"].mean())
    line(f"Gold beta on the S&P 500, {lab}: {b:.2f} (s.e. {np.sqrt(e.var(ddof=2)/((g['S&P 500']-g['S&P 500'].mean())**2).sum()):.2f}), correlation {g.corr().iloc[0,1]:.2f}")
# Why the gap between the two indices depends on the currency: the rest of the world backed out of the global index at a US weight of 60% (simple returns)
S = np.expm1(X[["Global equities (ACWI)", "S&P 500"]]); f = np.expm1(fx.reindex(X.index)); rest = (S.iloc[:, 0] - 0.6 * S.iloc[:, 1]) / 0.4
line(f"Rest of the world (US weight 60%): volatility {100*rest.std()*12**.5:.1f} in dollars, {100*((1+rest)/(1+f)-1).std()*12**.5:.1f} in euros")
bad = S.iloc[:, 1] < -0.05
line(f"Months with the S&P 500 down more than 5%: {int(bad.sum())}; mean change of the euro against the dollar in those months {100*f[bad].mean():.1f}%")
out.close()
