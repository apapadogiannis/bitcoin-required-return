"""Appendix E.4: Table 8 for a euro investor. The premium of each asset over the risk-free rate is the one of Table 8
(covered interest parity for a hedged investor; uncovered interest parity on average for an unhedged one). The risk-free
rate is the ten-year German Bund yield, 3.4% (3.58% on September 30, 3.34% on October 30 and about 3.3% on November 11-12,
2026, as reported by Investing.com and Trading Economics). Volatility is measured on returns converted to euros at
month-end exchange rates, over the same windows as Table 8. Output: euro_table.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, io, contextlib, runpy
import matplotlib; matplotlib.use("Agg")
def etf(f):
    z = pd.read_csv(f, parse_dates=["Date"]).sort_values("Date").set_index("Date"); z = z["AdjClose"] if "AdjClose" in z else z["Close"]
    z.index = z.index + pd.offsets.MonthEnd(0); return np.log(z).diff()
src = open(os.path.join(SCRIPTS, "22_pretty_figs.py")).read()
with contextlib.redirect_stdout(io.StringIO()):
    exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
    cs = runpy.run_path(os.path.join(SCRIPTS, "31_cross_section.py"))
RF_USD, RF_EUR, ERP_PTS = 5.0, 3.4, 4.0   # percent; set after the shared block, which defines its own names
D = pd.DataFrame({"Global equities (MSCI ACWI)": etf(os.path.join(DATA, "acwi_monthly.csv")), "S&P 500": etf(os.path.join(DATA, "voo_monthly.csv")), "Nasdaq-100": etf(os.path.join(DATA, "qqq_monthly.csv")),
                  "Russell 2000": etf(os.path.join(DATA, "iwm_monthly.csv")), "Gold": etf(os.path.join(DATA, "gld_monthly.csv")), "Bitcoin": np.log(px).diff(), "Ether": np.log1p(cs["Rn"]["eth"])})
fx = etf(os.path.join(DATA, "eurusd_monthly.csv"))            # log change of the dollar price of one euro
def vols(X):
    w = X["2012-01":"2026-04"]; v = {c: 100 * w[c].std() * 12**.5 for c in X.columns[:5]}
    v["Bitcoin"] = 100 * np.sqrt(X["Bitcoin"][:"2026-05"].pow(2).ewm(halflife=9).mean().iloc[-1] * 12)   # recent-weighted, May 2026, as in Table 8
    v["Ether"] = 100 * np.sqrt(X["Ether"][:"2026-04"].pow(2).ewm(halflife=9).mean().iloc[-1] * 12)       # recent-weighted, April 2026
    return v
v_usd, v_eur = vols(D), vols(D.sub(fx.reindex(D.index), axis=0))
w = D["2012-01":"2026-04"]; sp = w["S&P 500"]
beta = {c: w[c].cov(sp) / sp.var() for c in D.columns[:4]}
# premia over the risk-free rate, as in Table 8: CAPM for the equity indices; the MCM equation for gold (upper bound), Bitcoin and Ether
prem = {c: ERP_PTS * round(beta[c], 2) for c in beta}; prem.update({"Gold": 5.5 - RF_USD, "Bitcoin": 18.3 - RF_USD, "Ether": 23.4 - RF_USD})
out = open(os.path.join(OUT, "euro_table.txt"), "w")
def line(s=""):
    print(s); out.write(s + "\n")
line(f"Table 8 for a euro investor: risk-free rate {RF_EUR}% (ten-year Bund), premia as in Table 8 (dollar risk-free rate {RF_USD}%)")
line(f"{'':30s}{'premium':>8s}{'average':>9s}{'vol EUR':>9s}{'drag':>7s}{'compound':>10s}{'Sharpe':>8s}{'Sharpe c.':>10s} |{'vol USD':>8s}{'avg USD':>9s}")
for c in D.columns:
    sg = round(v_eur[c], 0 if c in ("Bitcoin", "Ether") else 1); mu = round(RF_EUR + prem[c], 1); dr = sg**2 / 200   # as in Table 8: displayed average and volatility
    line(f"{c:30s}{prem[c]:8.2f}{mu:9.2f}{sg:9.1f}{dr:7.2f}{mu-dr:10.2f}{(mu-RF_EUR)/sg:8.3f}{(mu-dr-RF_EUR)/sg:10.3f} |{v_usd[c]:8.2f}{RF_USD+prem[c]:9.2f}")
line(); line("volatility in euros, unrounded: " + ", ".join(f"{c} {v_eur[c]:.2f}" for c in D.columns))
line("correlation of the euro's monthly change against the dollar with each asset's dollar return, 2012-01 to 2026-04: " + ", ".join(f"{c} {w[c].corr(fx):.2f}" for c in D.columns[:5]) + f", Bitcoin {D['Bitcoin']['2012-01':'2026-04'].corr(fx):.2f}")
line(f"interest differential (dollar less euro risk-free rate): {RF_USD-RF_EUR:.1f} points; volatility of the euro against the dollar {100*fx['2012-01':'2026-04'].std()*12**.5:.1f}%")
out.close()
