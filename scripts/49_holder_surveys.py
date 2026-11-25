"""Appendix B.2: what owners hold, wave by wave, in surveys that ask for the value of holdings.
Reads data/holder_surveys.csv (UK Financial Conduct Authority, four waves; Bank of Canada, five waves; sources in
data/holder_surveys_SOURCE.md) and sets holdings per owner beside Bitcoin's price in the months of the fieldwork.
Output: holder_surveys.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd
S = pd.read_csv(os.path.join(DATA, "holder_surveys.csv"), dtype={"price_from": str, "price_to": str})
btc = pd.read_csv(os.path.join(CSV, "btc.csv"), parse_dates=["time"], usecols=["time", "PriceUSD"]).set_index("time")["PriceUSD"].dropna()
S["btc_usd"] = [btc[a:b].mean() for a, b in zip(S.price_from, S.price_to)]       # average daily price over the fieldwork months
slope = lambda y, x: np.polyfit(np.log(x), np.log(y), 1)[0]                      # elasticity: slope of log y on log x across waves
with open(os.path.join(OUT, "holder_surveys.txt"), "w") as out:
    def p(s=""):
        print(s); out.write(s + "\n")
    for c, g in S.groupby("country", sort=False):
        g = g.reset_index(drop=True); cur = g.currency[0]
        p(f"{c}: {g.survey[0]} ({len(g)} waves; holdings in {cur}, Bitcoin's price in US dollars, average of the fieldwork months)")
        p(f"  {'wave':28s}{'own, %':>8s}{'owners, m':>11s}{'median':>9s}{'mean':>8s}{'Bitcoin, $':>12s}{'price, first wave = 100':>26s}")
        for _, r in g.iterrows():
            f = lambda v, d=0: f"{v:.{d}f}" if pd.notna(v) else "-"
            p(f"  {r.fieldwork:28s}{f(r.ownership_pct,1):>8s}{f(r.owners_million,2):>11s}{f(r.median_holding,1):>9s}{f(r.mean_holding):>8s}{r.btc_usd:12.0f}{100*r.btc_usd/g.btc_usd[0]:26.0f}")
        a, b = g.iloc[0], g.iloc[-1]
        p(f"  first wave to last: Bitcoin's price times {b.btc_usd/a.btc_usd:.1f}; median holding {100*(b.median_holding/a.median_holding-1):+.0f}%"
          + (f"; mean holding {100*(b.mean_holding/a.mean_holding-1):+.0f}%; number of owners times {b.owners_million/a.owners_million:.1f}" if pd.notna(a.mean_holding) else f"; ownership rate times {b.ownership_pct/a.ownership_pct:.1f}"))
        p(f"  lowest to highest price among the waves: times {g.btc_usd.max()/g.btc_usd.min():.1f}; median holding between {g.median_holding.min():g} and {g.median_holding.max():g}"
          + (f"; mean holding between {g.mean_holding.min():g} and {g.mean_holding.max():g}" if pd.notna(a.mean_holding) else ""))
        p(f"  elasticity of the median holding to Bitcoin's price across the waves: {slope(g.median_holding, g.btc_usd):+.2f}")
        if pd.notna(a.mean_holding):
            p(f"  elasticity of the mean holding to Bitcoin's price across the waves: {slope(g.mean_holding, g.btc_usd):+.2f}")
            tot = g.owners_million*g.mean_holding/1000                           # what the survey's owners hold together, billion
            dn, dh, dt = np.log(b.owners_million/a.owners_million), np.log(b.mean_holding/a.mean_holding), np.log(tot.iloc[-1]/tot.iloc[0])
            p(f"  owners times mean holding: {tot.iloc[0]:.1f} to {tot.iloc[-1]:.1f} billion {cur}; of the growth (in logs), {100*dn/dt:.0f}% is more owners and {100*dh/dt:.0f}% is more per owner")
        p()
    # what the 2021Q3 owners' weight would have become by mid-2025 had they simply held: the weight follows the price
    x0, x1 = btc["2021-09"].mean(), btc["2025-06"].mean(); g_ = x1/x0
    p(f"Bitcoin's price, September 2021 to June 2025: times {g_:.2f}. A holder at 19% who neither bought nor sold, other wealth unchanged, would be at {100*0.19*g_/(1+0.19*(g_-1)):.0f}%.")
    # the survey distribution of 2021Q3 (Weber et al. 2026): 40% of owners below 5%, 70% below 15%; the median by linear interpolation
    p(f"Median owner's share in 2021Q3, interpolated between 5% (40% of owners below) and 15% (70% below): {5+10*(50-40)/(70-40):.1f}%")
