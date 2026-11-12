"""Appendix D.4: the ownership rate at the 2021Q3 anchor. Baseline 11% (Federal Reserve SHED: 12% in 2021);
alternative 3% in 2021Q3 rising to 11% by mid-2022, the path of the Candia et al. (2026) panel.
Recomputes the weights, the band and the monthly test. Output: ownership_sensitivity.txt"""
import numpy as np, pandas as pd
SRC = open("/home/claude/model/22_pretty_figs.py").read()
A = 'pd.Timestamp("2021-09-30"):0.11,'
assert SRC.count(A) == 1
def build(src):
    ns = {}
    exec(src.split("# ============ FIG 1")[0], ns); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")], ns)
    return ns
def test(ns):
    px, age = ns["px"], ns["age"]; mo = lambda mu: np.exp(mu/12) - 1
    D = pd.DataFrame({"r": px.shift(-1)/px - 1, "lo": mo(ns["foc_lo"]), "mid": mo(ns["req_mid"]), "hi": mo(ns["req_hi"])}).dropna(); D = D[D.index >= "2012-01-01"]
    out = {}
    for a, b, lab in (("2012", "2026", "2012-26"), ("2012", "2017", "2012-17"), ("2018", "2026", "2018-26")):
        s = D[a:b]; e = s.r - s.mid
        out[lab] = (1200*s.r.mean(), 1200*s.lo.mean(), 1200*s.hi.mean(), 1200*s.mid.mean(), 1200*(s.r - s.lo).mean(), 1200*e.mean(), 1200*e.std(ddof=1)/np.sqrt(len(e)), 1200*(s.r - s.hi).mean())
    return out
out = open("/home/claude/model/ownership_sensitivity.txt", "w")
def p(s=""):
    print(s); out.write(s + "\n")
for lab, src in (("baseline: 11% in 2021Q3", SRC), ("alternative: 3% in 2021Q3, 11% by mid-2022", SRC.replace(A, 'pd.Timestamp("2021-09-30"):0.03,pd.Timestamp("2022-06-30"):0.11,'))):
    ns = build(src); at = lambda d: ns["px"].index.get_indexer([pd.Timestamp(d)], method="nearest")[0]
    p(lab)
    for d in ("2013-06-30", "2017-06-30", "2019-06-30", "2021-09-30", "2023-06-30", "2026-05-31"):
        i = at(d); p(f"  {d[:7]}: owners' weight {100*ns['w_hi'].iloc[i]:5.1f}%  with funds {100*ns['w_lo'].iloc[i]:5.1f}%  early holder {ns['seg'].iloc[i]:4.2f}  band {100*ns['foc_lo'].iloc[i]:4.0f}-{100*ns['req_hi'].iloc[i]:4.0f}%")
    for k, v in test(ns).items():
        p(f"  {k}: delivered {v[0]:4.0f}  band {v[1]:3.0f}-{v[2]:3.0f}  midpoint {v[3]:3.0f}  gaps: lower {v[4]:+4.0f}  midpoint {v[5]:+4.0f} (se {v[6]:.0f})  upper {v[7]:+4.0f}")
    p()
out.close()
