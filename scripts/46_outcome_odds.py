"""Section 6, Table 6: how likely each outcome of the five-year window is under each forecast. The annualized log growth of a
window of T years is taken as normal around the forecast's compound rate with standard deviation sigma/sqrt(T), sigma = 42%.
This paper: 9.5% compounded. Age rule: 25% compounded, the middle of its 22-28% range. Output: outcome_odds.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
from math import log, sqrt, erf
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
SIGMA, T, PAPER, AGE = 0.42, 5, 0.095, 0.25
BANDS = (("25% a year or more", 0.25, None), ("17% to 25%", 0.17, 0.25), ("4% to 17%", 0.04, 0.17), ("below 4%", None, 0.04))
def probs(c, sigma=SIGMA, years=T):
    g, sd = log(1 + c), sigma / sqrt(years); o = []
    for _, lo, hi in BANDS:
        a = Phi((log(1 + lo) - g) / sd) if lo is not None else 0.0; b = Phi((log(1 + hi) - g) / sd) if hi is not None else 1.0; o.append(b - a)
    return o
with open(os.path.join(OUT, "outcome_odds.txt"), "w") as out:
    def p(s=""):
        print(s); out.write(s + "\n")
    p(f"Five-year window, volatility {100*SIGMA:.0f}%: standard deviation of the annualized compound return {100*SIGMA/sqrt(T):.1f} points")
    p(f"gap between the forecasts in log growth: {100*(log(1+AGE)-log(1+PAPER)):.1f} points")
    pp, pa = probs(PAPER), probs(AGE)
    p(f"{'compound return':22s}{'this paper':>12s}{'age rule':>10s}{'odds':>22s}")
    for (lab, _, _), x, y in zip(BANDS, pp, pa):
        r = y / x; p(f"{lab:22s}{100*x:11.0f}%{100*y:9.0f}%" + (f"{r:14.1f} to 1 age rule" if r >= 1 else f"{1/r:14.1f} to 1 this paper"))
    p(f"zero or less: this paper {100*Phi((0-log(1+PAPER))/(SIGMA/sqrt(T))):.0f}%, age rule {100*Phi((0-log(1+AGE))/(SIGMA/sqrt(T))):.0f}%")
    for c in (0.22, 0.28):
        q = probs(c); p(f"age rule at {100*c:.0f}% compounded: " + ", ".join(f"{lab} {100*x:.0f}%" for (lab, _, _), x in zip(BANDS, q)))
    p(f"years of returns needed to separate the two forecasts by two standard errors: {(2*SIGMA/(log(1+AGE)-log(1+PAPER)))**2:.0f}")
