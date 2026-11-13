"""Table 4: the required-return band worked out at five dates. For each date: the inputs (risk-free rate, volatility,
beta, the average owner's weight with and without ETF and treasury investors, the early holder's weight) and the
resulting lower edge, the two candidates for the upper edge, the upper edge and the midpoint. Output: band_table.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import io, contextlib
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
SRC = open(os.path.join(SCRIPTS, "22_pretty_figs.py")).read()
ns = {"__file__": __file__}
with contextlib.redirect_stdout(io.StringIO()):
    exec(SRC.split("# ============ FIG 1")[0], ns); exec(SRC[SRC.index("# ============ FIG 5"):SRC.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")], ns)
px, rf, sig2, beta = ns["px"], ns["rf"], ns["sig2"], ns["beta_roll"]
early = rf + ns["seg"]*sig2                                  # (b) the early holder's requirement
DATES = (("Mid-2013", "2013-06-30"), ("Mid-2017", "2017-06-30"), ("Mid-2019", "2019-06-30"), ("2021Q3", "2021-09-30"), ("May 2026", "2026-05-31"))
ROWS = (("Risk-free rate, %", lambda i: 100*rf.iloc[i]), ("Volatility, %", lambda i: 100*np.sqrt(sig2.iloc[i])), ("Beta", lambda i: beta.iloc[i]),
        ("Average owner's weight, with ETF and treasury investors, %", lambda i: 100*ns["w_lo"].iloc[i]),
        ("Average owner's weight, surveyed owners only, %", lambda i: 100*ns["w_hi"].iloc[i]),
        ("Early holder's weight, %", lambda i: 100*ns["seg"].iloc[i]),
        ("Lower edge: average owner, low inputs", lambda i: 100*ns["foc_lo"].iloc[i]),
        ("Upper edge (a): average owner, high inputs", lambda i: 100*ns["foc_hi"].iloc[i]),
        ("Upper edge (b): early holder", lambda i: 100*early.iloc[i]),
        ("Upper edge: the larger of (a) and (b)", lambda i: 100*ns["req_hi"].iloc[i]),
        ("Midpoint", lambda i: 100*ns["req_mid"].iloc[i]))
idx = [px.index.get_indexer([pd.Timestamp(d)])[0] for _, d in DATES]
with open(os.path.join(OUT, "band_table.txt"), "w") as out:
    def p(s=""):
        print(s); out.write(s + "\n")
    p("Table 4: the required-return band at five dates (required returns in % a year)")
    p(f"{'':60s}" + "".join(f"{lab:>10s}" for lab, _ in DATES))
    for lab, f in ROWS:
        p(f"{lab:60s}" + "".join(f"{f(i):10.2f}" for i in idx))
    hi = (early >= ns["foc_hi"])[px.index >= "2011-12-31"].dropna()
    p(); p(f"The early holder sets the upper edge in {100*hi.mean():.0f}% of the months, for the last time in {hi[hi].index[-1]:%B %Y}.")
