"""Figure 5 (wedge) on a log scale of the return, with a legend box."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
from matplotlib.patches import Patch
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])
src=open("/home/claude/model/22_pretty_figs.py").read()
data=src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")]
exec(data)
def G(x): return np.maximum(x,0.02)
fig,ax=plt.subplots(figsize=(7.6,5.9))
ax.set_yscale("log")
ax.fill_between(age[m],G(foc_lo[m]),G(req_hi[m]),color=SEQ[100],alpha=0.55,zorder=1,lw=0)
mm=m&fwd5.notna()
ax.fill_between(age[mm],G(req_mid[mm]),G(fwd5[mm]),where=(fwd5[mm]>req_mid[mm]),color=AQUA,alpha=0.30,zorder=2,lw=0)
ax.fill_between(age[mm],G(req_mid[mm]),G(fwd5[mm]),where=(fwd5[mm]<=req_mid[mm]),color=RED,alpha=0.24,zorder=2,lw=0)
l_req,=ax.plot(age[m],G(req_mid[m]),color=BLUE,lw=2.0,zorder=4)
l_real,=ax.plot(age[m],G(fwd5[m]),color=INK,lw=1.2,zorder=4)
l_age,=ax.plot(age[m],G(age_rule[m]),color=RED,lw=1.6,zorder=4)
etf_age=(pd.Timestamp("2024-01-11")-GEN).days/365.25
ax.axvline(etf_age,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
ax.text(etf_age+0.12,0.031,"spot ETFs approved\n(Jan 2024)",fontsize=8.0,color=INK2,va="bottom")
pts=[(2021.75,0.22,"22%",12.95,0.125),(2025.4,0.138,"13.8%",16.05,0.095)]
for (yr,val,lab,tx,ty) in pts:
    A=yr-2009.0
    l_surv,=ax.plot([A],[G(val)],marker="D",color="#008300",ms=5.5,ls="none",zorder=5)
    ax.annotate(lab,xy=(A,G(val)),xytext=(tx,ty),fontsize=8.3,color="#008300",
                arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"))
ax.plot([17.4],[0.15],marker="o",color=BLUE,ms=5.5,zorder=6)
ax.annotate("forecast 15%\n(90% range 12–18%)",xy=(17.4,0.15),xytext=(16.35,0.046),fontsize=8.3,color=BLUE,
            arrowprops=dict(arrowstyle="-",lw=0.6,color=BLUE))
ax.annotate("age rule 32%",xy=(17.4,0.33),xytext=(16.3,0.56),fontsize=8.3,color=RED,
            arrowprops=dict(arrowstyle="-",lw=0.6,color=RED))
handles=[l_real,l_req,Patch(facecolor=SEQ[100],alpha=0.8,label="required-return band"),l_age,
         Patch(facecolor=AQUA,alpha=0.45),Patch(facecolor=RED,alpha=0.35),l_surv]
labels=["realized forward 5-yr CAGR","required return of the marginal holder\n(midpoint of the band)",
        "required-return band: holder condition (γ 1.7–2.8) up to\nthe option-implied all-in bound",
        "age rule forecast, β/A","wedge: realized above required","wedge: realized below required",
        "holders' surveyed expectations (2021, 2025)"]
leg=ax.legend(handles,labels,loc="upper center",bbox_to_anchor=(0.5,-0.13),ncol=2,fontsize=8.0,frameon=True,
              framealpha=1.0,edgecolor=GRID,borderpad=0.8,labelspacing=0.5,handlelength=1.8,columnspacing=1.6)
ticks=[0.03,0.05,0.10,0.20,0.50,1.0,2.0,4.0]
ax.yaxis.set_major_locator(FixedLocator([G(t) for t in ticks]))
ax.yaxis.set_major_formatter(FixedFormatter([f"{int(round(100*t))}%" for t in ticks]))
ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.025,4.8); ax.set_xlim(3,18.5)
ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% per year (log scale)")
ax.set_title("The age rule tracks the decaying wedge, not a risk premium")
ax.text(0,1.018,"monthly series from age 3 (January 2012); logarithmic vertical scale, so equal distances are equal ratios",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
finish(fig,[ax],f"{MD}/fig_wedge")
