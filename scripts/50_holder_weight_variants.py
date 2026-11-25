"""Appendix D.4: other choices for the holder weight. The baseline holds the surveyed owners' weight at the survey mean
(19%). Recomputed here with the weight held at 12% and at 8% (about the survey median), with the path that carries
owners' wealth from 2021Q3 with the ownership rate and an assumed wealth per owner (so that the weight follows the
market value), and with ownership of 3% instead of 11% in 2021Q3 (which now moves only the early holder).
For each: the weights, the band, the monthly test and the five-year comparison. Output: holder_weight_variants.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import io, contextlib
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import statsmodels.api as sm
SRC = open(os.path.join(SCRIPTS, "22_pretty_figs.py")).read()
A = 'pd.Timestamp("2021-09-30"):0.11,'
assert SRC.count(A) == 1
def build(env, src=SRC):
    old = {k: os.environ.get(k) for k in ("W_OWNERS", "W_PATH")}
    for k in old: os.environ.pop(k, None)
    os.environ.update(env); ns = {"__file__": __file__}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(src.split("# ============ FIG 1")[0], ns); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")], ns)
    finally:
        for k, v in old.items():
            os.environ.pop(k, None)
            if v is not None: os.environ[k] = v
    return ns
_voo = pd.read_csv(os.path.join(DATA, "voo_monthly.csv"), parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; _voo.index = _voo.index + pd.offsets.MonthEnd(0)
PER = (("2012", "2026", "2012-26"), ("2012", "2017", "2012-17"), ("2018", "2026", "2018-26"))
def test(ns):
    """The monthly test of 27_monthly_test.py and the five-year comparison of 26_holder_weight.py, for one construction."""
    px, rf = ns["px"], ns["rf"]; mo = lambda mu: np.exp(mu/12) - 1; r = px.shift(-1)/px - 1
    D = pd.DataFrame({"r": r, "lo": mo(ns["foc_lo"]), "mid": mo(ns["req_mid"]), "hi": mo(ns["req_hi"])}).dropna(); D = D[D.index >= "2012-01-01"]
    RG = pd.DataFrame({"r": r, "s": _voo.pct_change().shift(-1), "rf": mo(rf), "extra": mo(ns["req_mid"] - ns["beta_term"])}).dropna(); RG = RG[RG.index >= "2012-01-01"]
    RG["bt"] = ns["beta_roll"].reindex(RG.index); RG["ex"] = RG.r - RG.rf
    RG["capm"] = RG.ex - RG.bt*(RG.s - RG.rf); RG["mcm"] = RG.r - RG.extra - RG.bt*(RG.s - RG.rf)
    o = {}
    for a, b, lab in PER:
        s = D[a:b]; e = s.r - s.mid; x = RG[a:b]
        f = sm.OLS(x.r - x.extra, sm.add_constant(x.s - x.rf)).fit()
        o[lab] = dict(real=1200*s.r.mean(), lo=1200*s.lo.mean(), hi=1200*s.hi.mean(), mid=1200*s.mid.mean(), g_lo=1200*(s.r - s.lo).mean(), g_mid=1200*e.mean(),
                      se=1200*e.std(ddof=1)/np.sqrt(len(e)), g_hi=1200*(s.r - s.hi).mean(), alpha=1200*f.params.iloc[0], alpha_se=1200*f.bse.iloc[0],
                      share=100 - 100*x.mcm.mean()/x.ex.mean(), share_capm=100 - 100*x.capm.mean()/x.ex.mean())
    o["corr"] = np.corrcoef(D.r, D.mid)[0, 1]
    mm = (ns["age"] >= 3.0) & ns["fwd_mu"].notna(); fm, mid, ar = ns["fwd_mu"][mm], ns["req_mid"][mm], ns["age_rule"][mm]
    o["five"] = dict(n=int(mm.sum()), miss=100*(fm - mid).abs().mean(), corr=np.corrcoef(fm, mid)[0, 1], closer=100*(np.abs(fm - ar) < np.abs(fm - mid)).mean())
    return o
CASES = (("Baseline: owners' weight held at 19% (survey mean)", {}, SRC),
         ("Owners' weight held at 12%", {"W_OWNERS": "0.12"}, SRC),
         ("Owners' weight held at 8% (about the survey median)", {"W_OWNERS": "0.08"}, SRC),
         ("Owners' wealth carried from 2021Q3 (the weight follows the market value)", {"W_PATH": "constructed"}, SRC),
         ("Baseline with ownership of 3% in 2021Q3 and 11% by mid-2022 (moves the early holder only)", {}, SRC.replace(A, 'pd.Timestamp("2021-09-30"):0.03,pd.Timestamp("2022-06-30"):0.11,')))
with open(os.path.join(OUT, "holder_weight_variants.txt"), "w") as out:
    def p(s=""):
        print(s); out.write(s + "\n")
    for lab, env, src in CASES:
        ns = build(env, src); at = lambda d: ns["px"].index.get_indexer([pd.Timestamp(d)], method="nearest")[0]
        p(lab)
        for d in ("2013-06-30", "2017-06-30", "2017-12-31", "2019-06-30", "2021-09-30", "2022-12-31", "2025-06-30", "2026-05-31"):
            i = at(d); p(f"  {d[:7]}: owners' weight {100*ns['w_hi'].iloc[i]:5.1f}%  with funds {100*ns['w_lo'].iloc[i]:5.1f}%  early holder {ns['seg'].iloc[i]:4.2f}  band {100*ns['foc_lo'].iloc[i]:5.1f}-{100*ns['req_hi'].iloc[i]:5.1f}%  midpoint {100*ns['req_mid'].iloc[i]:5.1f}%")
        wl, wh = 100*ns["w_lo"].iloc[-1], 100*ns["w_hi"].iloc[-1]
        p(f"  May 2026 weights, whole percent: {wl:.0f}-{wh:.0f}%; owners' wealth ${ns['Wp'].iloc[-1]/1e12:.2f} trillion")
        t = test(ns)
        for k, _, lab2 in [(x[2], 0, x[2]) for x in PER]:
            v = t[k]; p(f"  {lab2}: delivered {v['real']:4.0f}  band {v['lo']:3.0f}-{v['hi']:3.0f}  midpoint {v['mid']:3.0f}  gaps: lower {v['g_lo']:+4.0f}  midpoint {v['g_mid']:+4.0f} (se {v['se']:.0f})  upper {v['g_hi']:+4.0f}"
                          f" | MCM alpha {v['alpha']:+4.0f} (se {v['alpha_se']:.0f})  share of excess return explained: CAPM {v['share_capm']:.0f}%, MCM {v['share']:.0f}%")
        f5 = t["five"]; p(f"  correlation of the monthly return with the midpoint {t['corr']:.2f}")
        p(f"  five-year windows ({f5['n']}): the midpoint misses the delivered average by {f5['miss']:.0f} points on average; correlation {f5['corr']:.2f}; age rule closer in {f5['closer']:.0f}% of windows")
        p()
