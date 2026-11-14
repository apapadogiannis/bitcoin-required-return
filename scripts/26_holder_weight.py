"""Appendix B: the holder weight w through time and its figure (fig_w).
Also recomputes the band at selected dates, the five-year comparison of Appendix D.3 and the US-wealth pairing of Appendix D.4."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
exec(open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read().split("# ============ FIG 1")[0])
src=open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
plt.rcParams["axes.titlepad"]=8
surv={2014.5:0.004,2018.5:0.012,2021.75:0.11,2023.5:0.12,2025.5:0.12}
wealth_ramp=interp({2012:0.25,2021:1.0,2026:1.4})
Wp_retail=cap.iloc[i21]/0.19*(q/q.iloc[i21])*wealth_ramp
w_retail=(cap.reindex(px.index)/Wp_retail)
# 2026 fund and treasury investors: ETFs ~1.25M BTC + public-company treasuries ~1.26M BTC (mid-2026) at 1.5-3% holder weights
btc_inst=2.5e6; px_last=px.iloc[-1]; inst_value=btc_inst*px_last
w_inst_lo,w_inst_hi=0.015,0.03
Wtot_lo=Wp_retail.iloc[-1]+inst_value/w_inst_lo; Wtot_hi=Wp_retail.iloc[-1]+inst_value/w_inst_hi
w26_lo=cap.iloc[-1]/Wtot_lo; w26_hi=cap.iloc[-1]/Wtot_hi
print(f"2026: cap ${cap.iloc[-1]/1e12:.2f}T; retail participating wealth ${Wp_retail.iloc[-1]/1e12:.1f}T; retail-only w={w_retail.iloc[-1]:.3f}")
print(f"      fund and treasury investors {btc_inst/1e6:.2f}M BTC = ${inst_value/1e9:.0f}B; at 1.5-3% weights adds ${inst_value/w_inst_lo/1e12:.1f}-{inst_value/w_inst_hi/1e12:.1f}T; blended w = {w26_lo:.3f}-{w26_hi:.3f}")
for y in [2013,2015,2017,2019,2021,2023,2026]:
    i=px.index.get_indexer([pd.Timestamp(f"{y}-06-30" if y<2026 else "2026-05-31")],method="nearest")[0]
    print(f"Band {y}: q={100*q.iloc[i]:.1f}% w_hi={w_hi.iloc[i]:.3f} w_lo={w_lo.iloc[i]:.3f} band {100*foc_lo.iloc[i]:.0f}-{100*req_hi.iloc[i]:.0f}% mid {100*req_mid.iloc[i]:.0f}% sigma {100*np.sqrt(sig2.iloc[i]):.0f}%")
# D.3: the lower edge and the midpoint against the average return of the following five years, windows starting 2012 to 2021
mm=(age>=3.0)&fwd_mu.notna()
for lab,path in [("lower edge",foc_lo),("midpoint",req_mid)]:
    err=(fwd_mu-path)[mm]; beaten=(np.abs(fwd_mu-age_rule)<np.abs(fwd_mu-path))[mm].mean()
    print(f"D.3 {lab}: mean realized-minus-required {100*err.mean():.0f} pts; age rule closer in {100*beaten:.0f}% of windows")
# D.4 pairing: wealth per participant from US household net worth per adult (Z.1: ~$80T 2013 -> ~$170T 2026) instead of the judgment ramp
us_nw=interp({2012:72e12,2013:80e12,2016:95e12,2019:117e12,2021:150e12,2023:150e12,2026:170e12})
ramp_us=us_nw/us_nw.iloc[i21]
Wp_us=cap.iloc[i21]/0.19*(q/q.iloc[i21])*ramp_us
whi_us=(cap.reindex(px.index)/Wp_us).clip(upper=0.9); wlo_us=(cap.reindex(px.index)/(Wp_us+inst_val/0.015)).clip(upper=0.9)
lo_us=rf+0.85*beta_term+G_LO*sig2*wlo_us+0.003; hi_us=np.maximum(rf+1.15*beta_term+2.8*sig2*whi_us+0.035, rf+seg*sig2)
for y in [2013,2017,2021,2026]:
    i=px.index.get_indexer([pd.Timestamp(f"{y}-06-30" if y<2026 else "2026-05-31")],method="nearest")[0]
    print(f"D.4 {y}: band with US-wealth ramp {100*lo_us.iloc[i]:.0f}-{100*hi_us.iloc[i]:.0f}% (baseline {100*foc_lo.iloc[i]:.0f}-{100*req_hi.iloc[i]:.0f}%)")

# ---------- figure: two panels (the weight itself is panel (d) of the inputs figure) ----------
m=age>=3.0; A=age[m]
fig,axes=plt.subplots(1,2,figsize=(8.8,3.7))
ax=axes[0]; ax.set_yscale("log")
ax.plot(A,100*q[m],color=BLUE,lw=2.0,label="survey-anchored path (used)")
ax.plot(A,100*q_addr[m],color=MUT,lw=1.4,ls=(0,(3,2)),label="address count scaled to 2021Q3 (not used)")
ax.scatter([k-2009.0 for k in surv],[100*v for v in surv.values()],color=INK,zorder=5,s=28,label="household surveys")
tk=[0.1,0.3,1,3,10,30]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter([f"{t:g}%" for t in tk])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.08,40); ax.set_xlim(3,18.4); ax.set_title("(a) Share of US adults owning crypto",pad=18); ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% of adults (log scale)")
ax.legend(fontsize=7.8,loc="lower right",frameon=False)
ax=axes[1]; ax.set_yscale("log")
ax.plot(A,Wp_retail[m]/1e12,color=BLUE,lw=2.0,label="wealth of surveyed owners")
ax.plot(A,cap.reindex(px.index)[m]/1e12,color=INK,lw=1.6,label="Bitcoin capitalization")
ax.plot([A.iloc[-1]],[Wtot_lo/1e12],marker="v",color=ORANGE,ms=7,ls="none",label="2026, with fund and treasury\ninvestors at a 1.5% weight")
ax.plot([A.iloc[-1]],[Wtot_hi/1e12],marker="^",color=ORANGE,ms=7,ls="none",label="the same at a 3% weight")
tk=[0.01,0.1,1,10]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter(["$10B","$100B","$1T","$10T"])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.0005,80); ax.set_xlim(3,18.4); ax.set_title("(b) Wealth behind the holders",pad=18); ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("US dollars (log scale)")
ax.legend(fontsize=7.8,loc="lower right",frameon=False)
for ax in axes:
    ax.grid(axis="y",alpha=1.0); ax.set_axisbelow(True)
    sec=ax.secondary_xaxis("top",functions=(lambda x:x+2009.0,lambda y:y-2009.0)); sec.set_xticks([2013,2015,2017,2019,2021,2023,2025]); sec.tick_params(labelsize=7.5,colors=MUT,length=0,pad=1); sec.spines["top"].set_visible(False)
fig.tight_layout()
fig.savefig(f"{FIG}/fig_w.pdf"); fig.savefig(f"{FIG}/fig_w.png",dpi=200); print("saved fig_w")
