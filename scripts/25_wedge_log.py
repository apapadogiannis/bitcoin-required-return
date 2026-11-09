"""Figure 5 (wedge) on a log scale of gross return, 1+r, with tick labels in r%."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])
src=open("/home/claude/model/22_pretty_figs.py").read()
data=src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")]
exec(data)   # builds px, age, foc_lo, req_hi, req_mid, age_rule, fwd5, m, etc.

def G(x): return np.maximum(x,0.02)   # log scale on r itself, floored for plotting
fig,ax=plt.subplots(figsize=(7.6,5.0))
ax.set_yscale("log")
ax.fill_between(age[m],G(foc_lo[m]),G(req_hi[m]),color=SEQ[100],alpha=0.7,zorder=1,lw=0)
mm=m&fwd5.notna()
ax.fill_between(age[mm],G(req_mid[mm]),G(fwd5[mm]),where=(fwd5[mm]>req_mid[mm]),color=AQUA,alpha=0.28,zorder=2,lw=0)
ax.fill_between(age[mm],G(req_mid[mm]),G(fwd5[mm]),where=(fwd5[mm]<=req_mid[mm]),color=RED,alpha=0.22,zorder=2,lw=0)
ax.plot(age[m],G(req_mid[m]),color=BLUE,lw=2.0,zorder=4)
ax.plot(age[m],G(fwd5[m]),color=INK,lw=1.2,zorder=4)
ax.plot(age[m],G(age_rule[m]),color=RED,lw=1.6,zorder=4)
etf_age=(pd.Timestamp("2024-01-11")-GEN).days/365.25
ax.axvline(etf_age,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
ax.text(etf_age+0.12,3.6,"spot ETFs\n(Jan 2024)",fontsize=8.3,color=INK2,va="top")
for (yr,val,lab,tx,ty) in [(2021.75,0.22,"holders expected 22%",13.1,0.118),(2025.4,0.138,"holders expected 13.8%",14.6,0.072)]:
    A=yr-2009.0
    ax.plot([A],[G(val)],marker="D",color="#008300",ms=5,zorder=5)
    ax.annotate(lab,xy=(A,G(val)),xytext=(tx,G(ty)),fontsize=8.3,color="#008300",
                arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"))
ax.text(6.2,2.1,"realized forward 5-yr CAGR",color=INK,fontsize=8.8,weight="bold")
ax.text(9.3,0.74,"age rule forecast",color=RED,fontsize=8.8,weight="bold",rotation=-14)
ax.text(12.9,0.60,"required return of the\nmarginal holder (band + mid)",color=BLUE,fontsize=8.8,weight="bold")
ax.text(4.3,0.062,"wedge: realized − required\n(green +, red −)",color="#117a55",fontsize=8.6)
# forecast marker
ax.plot([17.4],[G(0.15)],marker="o",color=BLUE,ms=5,zorder=6)
ax.annotate("forecast 15%\n(90% range 12–18%)",xy=(17.4,G(0.15)),xytext=(16.5,0.046),fontsize=8.3,color=BLUE,
            arrowprops=dict(arrowstyle="-",lw=0.6,color=BLUE))
ax.annotate("age rule 32%",xy=(17.4,G(0.33)),xytext=(16.2,0.9),fontsize=8.3,color=RED,
            arrowprops=dict(arrowstyle="-",lw=0.6,color=RED))
ticks=[0.03,0.05,0.10,0.20,0.50,1.0,2.0,4.0]
ax.yaxis.set_major_locator(FixedLocator([G(t) for t in ticks]))
ax.yaxis.set_major_formatter(FixedFormatter([f"{int(round(100*t))}%" for t in ticks]))
ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.025,4.8)
ax.set_xlim(3,18.5)
ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% per year (log scale)")
ax.set_title("The age rule tracks the decaying wedge, not a risk premium")
ax.text(0,1.018,"required-return band: holder first-order condition (γ 1.7–2.8) up to the option-implied all-in bound",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
finish(fig,[ax],f"{MD}/fig_wedge")
