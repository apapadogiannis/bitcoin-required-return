"""Robustness (Appendix D.6): the holder-weight back-cast on total cryptoasset capitalization instead of Bitcoin's alone.
The surveys measure the share of crypto as a whole in owners' financial assets; this version clears the whole asset class
(panel assets with a reported capitalization, excluding stablecoins and wrapped or tokenized claims) against participating wealth.
Writes cryptowide_backcast.txt."""
import numpy as np, pandas as pd, matplotlib, io, sys
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
out=[]
out.append("Bitcoin share of the class: "+", ".join(f"{d[:7]} {100*dom.loc[d]:.0f}%" for d in ["2013-06-30","2017-06-30","2021-09-30","2023-06-30","2026-05-31"]))
for d in ["2013-06-30","2017-06-30","2021-09-30","2023-06-30","2026-05-31"]:
    out.append(f"{d}: baseline w {100*w_hi.loc[d]:.1f}% (with institutions {100*w_lo.loc[d]:.1f}%) | crypto-wide w {100*w_hi_cw.loc[d]:.1f}% (with institutions {100*w_lo_cw.loc[d]:.1f}%)")
fl=rf+0.85*beta_term+G_LO*sig2*w_lo_cw+0.003; fh=rf+1.15*beta_term+G_HI*sig2*w_hi_cw+0.03; rh=np.maximum(fh,rf+seg*sig2); rm=0.5*(fl+rh)
r=px.shift(-1)/px-1; mo=lambda mu: np.exp(mu/12)-1
def gap(mid,a,b):
    D=pd.DataFrame({"r":r,"m":mo(mid)}).dropna(); D=D[D.index>="2012-01-01"][a:b]; return 1200*(D.r-D.m).mean()
for a,b in [("2012","2026"),("2012","2017"),("2018","2026")]:
    out.append(f"monthly gap to midpoint {a}-{b}: baseline {gap(req_mid,a,b):+.0f}, crypto-wide {gap(rm,a,b):+.0f}")
out.append(f"2026 band: baseline {100*foc_lo.iloc[-1]:.0f}-{100*req_hi.iloc[-1]:.0f}%, crypto-wide {100*fl.iloc[-1]:.0f}-{100*rh.iloc[-1]:.0f}%")
exec(open("/home/claude/model/23_uncertainty.py").read().split('if __name__')[0])
buf=io.StringIO(); so=sys.stdout; sys.stdout=buf
run("Bitcoin, baseline w 0.08-0.19",0.42,1.5,2.0,0.08,0.19,0.003,0.03)
run(f"Bitcoin, crypto-wide w {w_lo_cw.iloc[-1]:.3f}-{w_hi_cw.iloc[-1]:.3f}",0.42,1.5,2.0,float(w_lo_cw.iloc[-1]),float(w_hi_cw.iloc[-1]),0.003,0.03)
sys.stdout=so; out.append(buf.getvalue().strip())
open("/home/claude/model/cryptowide_backcast.txt","w").write("\n".join(out)+"\n"); print("\n".join(out))
