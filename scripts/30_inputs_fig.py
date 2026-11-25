"""Figure 1: the time-varying inputs of equation (1), month by month (volatility, beta, holder weight, risk-free rate)."""
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
mm=(age>=3.0)&(age<=17.45); A=age[mm].values
etf_age=(pd.Timestamp("2024-01-11")-GEN).days/365.25
plt.rcParams["axes.titlepad"]=16
# Layout: the three inputs read directly from the data on the top row; the holder weight, which is built, full width below.
fig=plt.figure(figsize=(7.6,5.9)); gs=fig.add_gridspec(2,3,height_ratios=[1.0,1.35])
axa,axb,axc=[fig.add_subplot(gs[0,j]) for j in range(3)]; axd=fig.add_subplot(gs[1,:])
def mark(ax,lo,hi,lab,x=17.75,dx=0.3):
    if lo==hi: ax.plot([x],[lo],marker="o",color=INK,ms=4,clip_on=False,zorder=6)
    else: ax.plot([x,x],[lo,hi],color=INK,lw=2.2,solid_capstyle="butt",clip_on=False,zorder=6)
    ax.text(x+dx,(lo+hi)/2,lab,fontsize=7.8,va="center",ha="left",color=INK)
c19_age=(pd.Timestamp("2020-03-31")-GEN).days/365.25      # the month Bitcoin's co-movement with equities appears (Appendix A.3)
split_age=(pd.Timestamp("2013-09-30")-GEN).days/365.25    # the Grayscale trust starts in September 2013: fund holdings are zero before
mstr_age=(pd.Timestamp("2020-08-11")-GEN).days/365.25     # MicroStrategy's first purchase
ax=axa; ax.plot(A,100*np.sqrt(sig2[mm]),color=BLUE,lw=1.8); ax.set_ylim(0,220); ax.set_title("(a) Volatility, σ (%)"); mark(ax,42,42,"42%")
ax=axb; ax.plot(A,beta_roll[mm],color=BLUE,lw=1.8); ax.set_ylim(-0.1,3.3); ax.set_title("(b) Beta to the S&P 500"); mark(ax,1.5,2.0,"1.5–2.0"); ax.text(8.2,3.06,"capped at 3",fontsize=7.8,color=INK2,ha="left",va="bottom")
ax.annotate("rises from\nMarch 2020",xy=(c19_age+0.15,0.3),xytext=(12.6,0.12),fontsize=7.8,color=INK2,ha="left",va="bottom",arrowprops=dict(arrowstyle="-",lw=0.6,color=INK2))
ax=axc; ax.plot(A,100*rf[mm],color=BLUE,lw=1.8); ax.set_ylim(0,6); ax.set_title("(c) Risk-free rate (%)"); mark(ax,5,5,"5%")
ax=axd; WB=dict(fc="white",ec="none",pad=1.5); ax.set_yscale("log")
_sets=((rf+seg*sig2)>=foc_hi)[mm]; last_set=_sets[_sets].index[-1]; last_age=float(age[last_set])   # the last month the early holder sets the upper edge of the band
print("early holder last sets the upper edge:",last_set.strftime("%B %Y"))
_Av=np.asarray(A); _e=_Av<=last_age+1e-9; _we=100*seg[mm].values; _wh=100*w_hi[mm].values; _wl=100*w_lo[mm].values
_up=np.where(_e,_we,_wh)                                                            # the weight behind the upper edge, month by month
ax.fill_between(_Av,_wl,_up,color=SEQ[100],alpha=0.9,lw=0,zorder=1)                 # shaded: from the lower-edge weight to the upper-edge weight
# thick and solid where a holder sets an edge; thin and dashed where she does not
ax.plot(_Av[_e],_we[_e],color=INK,lw=2.6,zorder=5,solid_capstyle="butt"); ax.plot(_Av[~_e],_we[~_e],color=MUT,lw=1.1,ls=(0,(4,2)),zorder=3)
ax.plot(_Av[~_e],_wh[~_e],color=BLUE,lw=2.6,zorder=5,solid_capstyle="butt"); ax.plot(_Av[_e],_wh[_e],color=BLUE,lw=1.1,ls=(0,(4,2)),zorder=3)
ax.plot(_Av,_wl,color=SEQ[650],lw=2.6,zorder=4)
ax.plot([last_age,last_age],[_wh[_e][-1],_we[_e][-1]],color=INK2,lw=1.0,ls=(0,(1,1.5)),zorder=4)   # the month the upper edge passes from one holder to the other
ax.text(5.0,82,"UPPER EDGE until "+last_set.strftime("%B %Y")+":\nthe early holder, all her wealth in Bitcoin (γ = 1)",fontsize=7.8,color=INK,ha="left",va="top",linespacing=1.3,weight="bold")
ax.text(last_age+0.25,22.3,"UPPER EDGE from "+(last_set+pd.offsets.MonthEnd(1)).strftime("%B %Y")+": surveyed owners, 19% (γ = 2.8)",fontsize=7.8,color=BLUE,ha="left",va="bottom",weight="bold",bbox=WB,zorder=6)
ax.text(5.0,22.3,"surveyed owners, 19%: not the upper edge yet",fontsize=7.6,color=BLUE,ha="left",va="bottom")
ax.text(5.0,14.4,"LOWER EDGE: surveyed owners together with\nfund and treasury investors (γ = 1)",fontsize=7.8,color=SEQ[650],ha="left",va="top",weight="bold",linespacing=1.3)
ax.text(12.9,8.6,"early holder: no longer used",fontsize=7.6,color=INK2,ha="left",va="top")
for _xa in (split_age,mstr_age): ax.axvline(_xa,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
for _xa,_t in ((split_age,"Grayscale trust\n(September 2013)"),(mstr_age,"MicroStrategy's first\npurchase (August 2020)"),(etf_age,"spot ETFs\n(January 2024)")):
    ax.text(_xa+0.12,36,_t,fontsize=7.4,color=INK2,ha="left",va="center",linespacing=1.25,zorder=2)
tk=[5,10,20,50,100]; ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter([str(t) for t in tk])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(4.6,125); ax.set_title("(d) Holder weight, w (%): whose weight sets each edge of the band (logarithmic scale)"); mark(ax,7,19,"7–19%",x=17.68,dx=0.1)
ax.plot([2014.5-2009,2018.5-2009,2021.75-2009,2023.5-2009,2025.4-2009],[4.85]*5,marker="^",color=INK2,ms=4.5,ls="none",zorder=6,clip_on=False)
ax.plot([12.75],[19],marker="D",color="#008300",ms=5.5,zorder=7); ax.annotate("survey: 19% (2021Q3)",xy=(12.75,19),xytext=(13.3,13.2),fontsize=7.8,color="#008300",arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"),zorder=7)
for ax in (axa,axb,axc,axd):
    ax.set_xlim(3,17.6); ax.grid(axis="y",alpha=1.0); ax.set_axisbelow(True); ax.axvline(etf_age,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
    yrs=[2013,2015,2017,2019,2021,2023,2025] if ax is axd else [2013,2017,2021,2025]
    sec=ax.secondary_xaxis("top",functions=(lambda x:x+2009.0,lambda y:y-2009.0)); sec.set_xticks(yrs); sec.tick_params(labelsize=7.5,colors=MUT,length=0,pad=1); sec.spines["top"].set_visible(False)
    if ax is not axd: ax.set_xticks([5,10,15])
axd.set_xlabel("Bitcoin age (years)")
fig.subplots_adjust(left=0.06,right=0.915,top=0.93,bottom=0.085,hspace=0.45,wspace=0.52)
fig.savefig(f"{FIG}/fig_inputs.pdf"); fig.savefig(f"{FIG}/fig_inputs.png",dpi=140)
i=lambda d: px.index.get_indexer([pd.Timestamp(d)],method="nearest")[0]
print("sigma 2013 %.0f 2017 %.0f 2021 %.0f 2026 %.0f | max w_hi %.0f%% w_hi last %.0f w_lo last %.0f"%(100*np.sqrt(sig2.iloc[i("2013-06-30")]),100*np.sqrt(sig2.iloc[i("2017-06-30")]),100*np.sqrt(sig2.iloc[i("2021-09-30")]),100*np.sqrt(sig2.iloc[-1]),100*w_hi[mm].max(),100*w_hi.iloc[-1],100*w_lo.iloc[-1]))
