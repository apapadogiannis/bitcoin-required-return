"""Figure: the time-varying inputs of equation (1), month by month (volatility, beta, holder weight, risk-free rate)."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
exec(open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read().split("# ============ FIG 1")[0])
src=open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
mm=(age>=3.0)&(age<=17.45); A=age[mm].values
etf_age=(pd.Timestamp("2024-01-11")-GEN).days/365.25
plt.rcParams["axes.titlepad"]=16
fig,axs=plt.subplots(2,2,figsize=(7.6,5.4),sharex=True)
def mark(ax,lo,hi,lab):
    if lo==hi: ax.plot([17.75],[lo],marker="o",color=INK,ms=4,clip_on=False,zorder=6)
    else: ax.plot([17.75,17.75],[lo,hi],color=INK,lw=2.2,solid_capstyle="butt",clip_on=False,zorder=6)
    ax.text(17.95,(lo+hi)/2,lab,fontsize=7.8,va="center",ha="left",color=INK)
ax=axs[0,0]; ax.plot(A,100*np.sqrt(sig2[mm]),color=BLUE,lw=1.8); ax.set_ylim(0,220); ax.set_title("(a) Volatility, σ (% a year)"); mark(ax,42,42,"42%")
ax=axs[0,1]; ax.plot(A,beta_roll[mm],color=BLUE,lw=1.8); ax.set_ylim(-0.1,3.3); ax.set_title("(b) Beta to the S&P 500, four-year window"); mark(ax,1.5,2.0,"1.5–2.0"); ax.text(5.6,3.08,"capped at 3",fontsize=7.8,color=INK2,ha="center",va="bottom")
ax=axs[1,0]
ax.fill_between(A,100*w_lo[mm],100*w_hi[mm],color=SEQ[100],alpha=0.8,lw=0)
ax.plot(A,100*w_hi[mm],color=BLUE,lw=1.8); ax.plot(A,100*w_lo[mm],color=SEQ[650],lw=1.8)
ax.plot(A,100*seg[mm],color=INK,lw=1.4,ls=(0,(4,2)),zorder=4); ax.text(6.2,92,"early holder",fontsize=7.8,color=INK,ha="center",va="top")
ax.set_ylim(0,105); ax.set_title("(c) Holder weight, w (%): two readings"); mark(ax,8,19,"8–19%")
ax.text(16.25,44,"average owner,\nowners only",fontsize=7.8,color=BLUE,ha="center",va="bottom"); ax.annotate("average owner, with ETF\nand treasury investors",xy=(15.9,11.0),xytext=(10.6,70),fontsize=7.8,color=SEQ[650],ha="left",arrowprops=dict(arrowstyle="-",lw=0.6,color=SEQ[650]))
ax.plot([2014.5-2009,2018.5-2009,2021.75-2009,2023.5-2009,2025.4-2009],[1.2]*5,marker="^",color=INK2,ms=4.5,ls="none",zorder=6,clip_on=False)
ax.plot([12.75],[19],marker="D",color="#008300",ms=5,zorder=6); ax.annotate("survey: 19%\n(2021Q3)",xy=(12.75,19),xytext=(10.0,46),fontsize=7.8,color="#008300",arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"))
ax=axs[1,1]; ax.plot(A,100*rf[mm],color=BLUE,lw=1.8); ax.set_ylim(0,6); ax.set_title("(d) Risk-free rate (ten-year Treasury yield, %)"); mark(ax,5,5,"5%")
for ax in axs.ravel():
    ax.set_xlim(3,17.6); ax.grid(axis="y",alpha=1.0); ax.set_axisbelow(True); ax.axvline(etf_age,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
    sec=ax.secondary_xaxis("top",functions=(lambda x:x+2009.0,lambda y:y-2009.0)); sec.set_xticks([2013,2016,2019,2022,2025]); sec.tick_params(labelsize=7.5,colors=MUT,length=0,pad=1); sec.spines["top"].set_visible(False)
for ax in axs[1]: ax.set_xlabel("Bitcoin age (years)")
fig.subplots_adjust(left=0.06,right=0.90,top=0.93,bottom=0.09,hspace=0.42,wspace=0.42)
fig.savefig(f"{FIG}/fig_inputs.pdf"); fig.savefig(f"{FIG}/fig_inputs.png",dpi=140)
i=lambda d: px.index.get_indexer([pd.Timestamp(d)],method="nearest")[0]
print("sigma 2013 %.0f 2017 %.0f 2021 %.0f 2026 %.0f | max w_hi %.0f%% w_hi last %.0f w_lo last %.0f"%(100*np.sqrt(sig2.iloc[i("2013-06-30")]),100*np.sqrt(sig2.iloc[i("2017-06-30")]),100*np.sqrt(sig2.iloc[i("2021-09-30")]),100*np.sqrt(sig2.iloc[-1]),100*w_hi[mm].max(),100*w_hi.iloc[-1],100*w_lo.iloc[-1]))
