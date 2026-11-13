"""Appendix D.2: the monthly test under other groupings of the 172 months (calendar years, two-year and four-year periods).
Table 5 of the paper uses three-year periods. Output: grouping_robustness.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd
src = open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
mo = lambda mu: np.exp(mu/12) - 1
D = pd.DataFrame({"r": px.shift(-1)/px - 1, "lo": mo(foc_lo), "mid": mo(req_mid), "hi": mo(req_hi)}).dropna(); D = D[D.index >= "2012-01-01"]
out = open(os.path.join(OUT,"grouping_robustness.txt"), "w")
def p(s=""):
    print(s); out.write(s + "\n")
def row(a, b):
    s = D.loc[a:b]; e = s.r - s.mid; d = 1200*s.r.mean(); lo = 1200*s.lo.mean(); hi = 1200*s.hi.mean(); g = 1200*e.mean(); se = 1200*e.std(ddof=1)/np.sqrt(len(e))
    where = "inside" if lo <= d <= hi else ("above" if d > hi else "below")
    p(f"  {a}{'' if a == b else '-' + b[2:]:4s} months {len(s):2d}  delivered {d:5.0f}  band {lo:3.0f}-{hi:3.0f}  midpoint {1200*s.mid.mean():3.0f}  gap {g:+5.0f} (se {se:3.0f}, t {g/se:+.1f})  {where}")
    return where, g, se
p("calendar years"); R = [row(str(y), str(y)) for y in range(2012, 2027)]
p(f"  inside the band {sum(r[0] == 'inside' for r in R)}, above {sum(r[0] == 'above' for r in R)}, below {sum(r[0] == 'below' for r in R)}; gaps {min(r[1] for r in R):+.0f} to {max(r[1] for r in R):+.0f}; standard errors {min(r[2] for r in R):.0f} to {max(r[2] for r in R):.0f}; |t| > 2 in {sum(abs(r[1]/r[2]) > 2 for r in R)} years")
p("two-year periods"); [row(str(a), str(a + 1)) for a in range(2012, 2026, 2)]
p("three-year periods (Table 5)"); [row(a, b) for a, b in (("2012", "2014"), ("2015", "2017"), ("2018", "2020"), ("2021", "2023"), ("2024", "2026"))]
p("four-year periods"); [row(a, b) for a, b in (("2012", "2015"), ("2016", "2019"), ("2020", "2023"), ("2024", "2026"))]
out.close()
