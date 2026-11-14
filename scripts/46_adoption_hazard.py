"""Appendix C.2: the death rate of cryptoassets by stage of adoption, measured by dollar trading volume.
For every asset-month, the trailing twelve-month average of daily dollar volume (known at the start of the month) places the
asset in a volume band; the outcome is whether the asset is dead within the following 24 months (curated death definition).
Asset-months of living assets with less than 24 months of data ahead are left out. A second version keeps only asset-months
in which the volume is at least a third of the asset's own earlier peak, so that assets already fading are excluded.
Output: adoption_hazard.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
import numpy as np, pandas as pd
V = pd.read_pickle(f"{OUT}/volume_monthly.pkl")
P = pd.read_csv(f"{OUT}/panel_v3.csv", parse_dates=["birth", "last", "death_cur_date"]).set_index("asset")
core = P[~P.stable & ~P.stable2 & ~P.tokstock & ~P.wrapped_like]; A = [a for a in core.index if a in V.columns]
T = V[A].rolling(12, min_periods=3).mean().shift(1); PK = V[A].cummax().shift(1); H = 24
rows = []
for a in A:
    b = core.loc[a, "birth"]; dead = bool(core.loc[a, "dead_cur"]); end = core.loc[a, "death_cur_date"] if dead else core.loc[a, "last"]
    idx = T.index[(T.index >= b) & (T.index <= end + pd.offsets.MonthEnd(0))]; n = len(idx)
    if n == 0: continue
    left = n - 1 - np.arange(n)                                   # months until the asset's last observation
    rows.append(pd.DataFrame({"v": T.loc[idx, a].values, "near": (T.loc[idx, a] / PK.loc[idx, a]).values,
                              "dies": dead & (left <= H) & (left > 0), "obs": (left >= H) | (dead & (left > 0))}))
X = pd.concat(rows).dropna(); X = X[X.obs]
BANDS = ((1e4, 1e5, "$10,000 to $100,000"), (1e5, 1e6, "$100,000 to $1 million"), (1e6, 1e7, "$1 to $10 million"), (1e7, 1e8, "$10 to $100 million"), (1e8, 1e9, "$100 million to $1 billion"))
bt = V["btc"].rolling(12, min_periods=3).mean()
with open(f"{OUT}/adoption_hazard.txt", "w") as fh:
    def say(t=""):
        print(t); fh.write(t + "\n")
    say(f"{'daily dollar volume':28s}{'asset-months':>13s}{'dead in 2y':>11s}{'rate/yr':>9s} |{'not fading':>12s}{'dead in 2y':>11s}{'rate/yr':>9s}")
    for lo, hi, lab in BANDS:
        s1 = X[(X.v > lo) & (X.v <= hi)]; s2 = s1[s1.near >= 1/3]; f1, f2 = s1.dies.mean(), s2.dies.mean()
        say(f"{lab:28s}{len(s1):13d}{100*f1:10.0f}%{-50*np.log(1-f1):8.0f}% |{len(s2):12d}{100*f2:10.0f}%{-50*np.log(1-f2):8.0f}%")
    say("Bitcoin, trailing twelve-month average daily volume at mid-year: " + ", ".join(f"{y}: ${bt[pd.Timestamp(f'{y}-06-30')]/1e6:,.2f}m" for y in (2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018)))
