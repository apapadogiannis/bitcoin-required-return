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
ax=axd; _b=A>=split_age; WB=dict(fc="white",ec="none",pad=1.2)
ax.fill_between(A[_b],100*w_lo[mm].values[_b],100*w_hi[mm].values[_b],color=SEQ[100],alpha=0.9,lw=0)
ax.plot(A,100*w_hi[mm],color=BLUE,lw=1.8); ax.plot(A[_b],100*w_lo[mm].values[_b],color=SEQ[650],lw=1.8)
_sets=((rf+seg*sig2)>=foc_hi)[mm]; last_set=_sets[_sets].index[-1]; last_age=float(age[last_set])   # the last month the early holder sets the upper edge of the band
print("early holder last sets the upper edge:",last_set.strftime("%B %Y"))
_e=A<=last_age+1e-9
ax.plot(A[_e],100*seg[mm].values[_e],color=INK,lw=1.4,ls=(0,(4,2)),zorder=4)
ax.plot(A[~_e],100*seg[mm].values[~_e],color=MUT,lw=1.2,ls=(0,(4,2)),zorder=4)                        # grey once it no longer sets the upper edge
ax.text(5.0,96,"early holder, equation (4): an alternative\nreading, used for the upper edge of the\nrequired return until "+last_set.strftime("%B %Y")+" (then grey)",fontsize=7.8,color=INK,ha="left",va="top",linespacing=1.25)
ax.annotate("average owner, equation (3):\na band between two lines",xy=(7.2,5.5),xytext=(5.0,50),fontsize=7.8,color=BLUE,ha="left",va="bottom",arrowprops=dict(arrowstyle="-",lw=0.6,color=BLUE))
for _xa in (split_age,mstr_age): ax.axvline(_xa,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
ax.text(split_age-0.12,74,"Grayscale trust\n(September 2013):\nthe band opens",fontsize=7.8,color=INK2,ha="right",va="top",linespacing=1.25)
ax.text(mstr_age+0.15,97,"first corporate treasury\n(MicroStrategy, August 2020)",fontsize=7.8,color=INK2,ha="left",va="top",linespacing=1.25,bbox=WB,zorder=5)
ax.text(mstr_age+0.15,77,"upper line: surveyed owners only",fontsize=7.8,color=BLUE,ha="left",va="center",bbox=WB,zorder=5)
ax.text(mstr_age+0.15,68,"lower line: with fund and treasury investors",fontsize=7.8,color=SEQ[650],ha="left",va="center",bbox=WB,zorder=5)
ax.text(etf_age+0.12,57,"spot ETFs approved\n(January 2024):\nthe band widens",fontsize=7.8,color=INK2,ha="left",va="top",linespacing=1.25)
ax.set_ylim(0,105); ax.set_title("(d) Holder weight, w (%): two readings"); mark(ax,8,19,"8–19%",x=17.68,dx=0.1)
ax.plot([2014.5-2009,2018.5-2009,2021.75-2009,2023.5-2009,2025.4-2009],[1.2]*5,marker="^",color=INK2,ms=4.5,ls="none",zorder=6,clip_on=False)
ax.plot([12.75],[19],marker="D",color="#008300",ms=5,zorder=6); ax.annotate("survey: 19%\n(2021Q3)",xy=(12.75,19),xytext=(13.05,40),fontsize=7.8,color="#008300",bbox=WB,arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"))
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
