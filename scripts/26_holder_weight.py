"""Appendix D: how the holder weight w is measured, bounded and extrapolated.
Also recomputes Table 4's band column, B.3 (forecast metric) and B.4 (wealth pairing)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
plt.rcParams["axes.titlepad"]=8
surv={2014.5:0.004,2018.5:0.012,2021.75:0.11,2023.5:0.12,2025.5:0.13}
wealth_ramp=interp({2012:0.25,2021:1.0,2026:1.4})
Wp_retail=cap.iloc[i21]/0.19*(q/q.iloc[i21])*wealth_ramp
w_retail=(cap.reindex(px.index)/Wp_retail)
# 2026 institutional channel: ETFs ~1.25M BTC + public-company treasuries ~1.26M BTC (mid-2026) at 1.5-3% holder weights
btc_inst=2.5e6; px_last=px.iloc[-1]; inst_value=btc_inst*px_last
w_inst_lo,w_inst_hi=0.015,0.03
Wtot_lo=Wp_retail.iloc[-1]+inst_value/w_inst_lo; Wtot_hi=Wp_retail.iloc[-1]+inst_value/w_inst_hi
w26_lo=cap.iloc[-1]/Wtot_lo; w26_hi=cap.iloc[-1]/Wtot_hi
print(f"2026: cap ${cap.iloc[-1]/1e12:.2f}T; retail participating wealth ${Wp_retail.iloc[-1]/1e12:.1f}T; retail-only w={w_retail.iloc[-1]:.3f}")
print(f"      institutional channel {btc_inst/1e6:.2f}M BTC = ${inst_value/1e9:.0f}B; at 1.5-3% weights adds ${inst_value/w_inst_lo/1e12:.1f}-{inst_value/w_inst_hi/1e12:.1f}T; blended w = {w26_lo:.3f}-{w26_hi:.3f}")
for y in [2013,2015,2017,2019,2021,2023,2026]:
    i=px.index.get_indexer([pd.Timestamp(f"{y}-06-30" if y<2026 else "2026-05-31")],method="nearest")[0]
    print(f"Table4 {y}: q={100*q.iloc[i]:.1f}% w_hi={w_hi.iloc[i]:.3f} w_lo={w_lo.iloc[i]:.3f} band {100*foc_lo.iloc[i]:.0f}-{100*req_hi.iloc[i]:.0f}% mid {100*req_mid.iloc[i]:.0f}% sigma {100*np.sqrt(sig2.iloc[i]):.0f}%")
# B.3 forecast metric: survey-anchored lower edge and midpoint as 5-yr forecasts over 2012-2021 windows
mm=(age>=3.0)&fwd_mu.notna()
for lab,path in [("lower edge",foc_lo),("midpoint",req_mid)]:
    err=(fwd_mu-path)[mm]; beaten=(np.abs(fwd_mu-age_rule)<np.abs(fwd_mu-path))[mm].mean()
    print(f"B.3 {lab}: mean realized-minus-required {100*err.mean():.0f} pts; age rule closer in {100*beaten:.0f}% of windows")
# B.4 pairing: wealth per participant from US household net worth per adult (Z.1: ~$80T 2013 -> ~$170T 2026) instead of the judgment ramp
us_nw=interp({2012:72e12,2013:80e12,2016:95e12,2019:117e12,2021:150e12,2023:150e12,2026:170e12})
ramp_us=us_nw/us_nw.iloc[i21]
Wp_us=cap.iloc[i21]/0.19*(q/q.iloc[i21])*ramp_us
whi_us=(cap.reindex(px.index)/Wp_us).clip(upper=0.9); wlo_us=(cap.reindex(px.index)/(Wp_us+inst_val/0.015)).clip(upper=0.9)
lo_us=rf+0.85*beta_term+G_LO*sig2*wlo_us+0.003; hi_us=np.maximum(rf+1.15*beta_term+2.8*sig2*whi_us+0.03, rf+seg*sig2)
for y in [2013,2017,2021,2026]:
    i=px.index.get_indexer([pd.Timestamp(f"{y}-06-30" if y<2026 else "2026-05-31")],method="nearest")[0]
    print(f"B.4 {y}: band with US-wealth ramp {100*lo_us.iloc[i]:.0f}-{100*hi_us.iloc[i]:.0f}% (baseline {100*foc_lo.iloc[i]:.0f}-{100*req_hi.iloc[i]:.0f}%)")

# ---------- figure: three panels ----------
m=age>=3.0; A=age[m]
fig,axes=plt.subplots(3,1,figsize=(8.8,10.0))
ax=axes[0]; ax.set_yscale("log")
ax.plot(A,100*q[m],color=BLUE,lw=2.0,label="survey-anchored path (used)")
ax.plot(A,100*q_addr[m],color=MUT,lw=1.4,ls=(0,(3,2)),label="address count scaled to 2021Q3")
ax.scatter([k-2009.0 for k in surv],[100*v for v in surv.values()],color=INK,zorder=5,s=28,label="household surveys (US adults holding crypto)")
tk=[0.1,0.3,1,3,10,30]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter([f"{t:g}%" for t in tk])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.08,40); ax.set_xlim(3,17.5); ax.set_title("(a) Participation"); ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("share of US adults (log)")
ax.legend(fontsize=8,loc="center left",bbox_to_anchor=(1.01,0.5),frameon=False)
ax=axes[1]; ax.set_yscale("log")
ax.plot(A,Wp_retail[m]/1e12,color=BLUE,lw=2.0,label="participating wealth (survey holders)")
ax.plot(A,cap.reindex(px.index)[m]/1e12,color=INK,lw=1.6,label="Bitcoin capitalization")
ax.plot([A.iloc[-1]],[Wtot_lo/1e12],marker="v",color=ORANGE,ms=7,ls="none",label="plus ETF/treasury holders at 1.5% weight")
ax.plot([A.iloc[-1]],[Wtot_hi/1e12],marker="^",color=ORANGE,ms=7,ls="none",label="plus ETF/treasury holders at 3% weight")
tk=[0.01,0.1,1,10]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter(["$10B","$100B","$1T","$10T"])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.005,80); ax.set_xlim(3,17.5); ax.set_title("(b) Wealth behind the holders"); ax.set_xlabel("Bitcoin age (years)")
ax.legend(fontsize=8,loc="center left",bbox_to_anchor=(1.01,0.5),frameon=False)
ax=axes[2]; ax.set_yscale("log")
ax.fill_between(A,100*w_lo[m],90,color=SEQ[100],alpha=0.6,lw=0,label="band used: diluted back-cast up to all-in (0.9)")
ax.plot(A,100*w_lo[m],color=ORANGE,lw=1.6,ls=(0,(3,2)),label="back-cast with ETF/treasury holders at 1.5%")
ax.plot(A,100*w_retail[m],color=BLUE,lw=2.0,label="back-cast average weight (survey holders)")
ax.scatter([12.75],[19],color=INK,zorder=5,s=34,label="2021Q3 survey: 19%")
ax.plot([14.5,14.5],[10,25],color=AQUA,lw=3,alpha=0.8,label="Austria 2023: mostly under 20%")
ax.plot([A.iloc[-1],A.iloc[-1]],[100*w26_lo,19],color=INK,lw=3,alpha=0.9,label=f"2026 range used in Section 5: {100*w26_lo:.0f}–19%")
tk=[1,2,5,10,20,50,90]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter([f"{t}%" for t in tk])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.8,100); ax.set_xlim(3,17.5); ax.set_title("(c) Holder weight w"); ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("share of financial wealth (log)")
ax.legend(fontsize=8,loc="center left",bbox_to_anchor=(1.01,0.5),frameon=False)
fig.suptitle("How the holder weight is measured, bounded, and extrapolated",x=0.013,y=0.995,ha="left",fontsize=11,fontweight="bold")
fig.tight_layout(rect=(0,0,1,0.97))
fig.savefig(f"{MD}/fig_w.pdf"); fig.savefig(f"{MD}/fig_w.png",dpi=200); print("saved fig_w")
