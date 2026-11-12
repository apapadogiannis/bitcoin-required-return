"""Figure 1: the required return against realized returns (a), and the terms of equation (1)
in levels (b) and as shares (c), on one time axis."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
def G(x): return np.maximum(x,0.02)
plt.rcParams["axes.titlepad"]=6
fig=plt.figure(figsize=(7.6,9.9))
gs=fig.add_gridspec(3,1,height_ratios=[3.5,2.3,2.0],left=0.085,right=0.985,top=0.965,bottom=0.045,hspace=0.0)
# manual placement so the legend of (a) sits between (a) and (b)
axa=fig.add_axes([0.085,0.648,0.775,0.292]); axb=fig.add_axes([0.085,0.282,0.775,0.20]); axc=fig.add_axes([0.085,0.045,0.775,0.168])
XL=(3,18.5); etf_age=(pd.Timestamp("2024-01-11")-GEN).days/365.25
halv=[(pd.Timestamp(h)-GEN).days/365.25 for h in ["2012-11-28","2016-07-09","2020-05-11","2024-04-20"]]
# ---------- (a) band against realized ----------
ax=axa; ax.set_yscale("log")
ax.fill_between(age[m],G(foc_lo[m]),G(req_hi[m]),color=SEQ[100],alpha=0.55,zorder=1,lw=0)
l_req,=ax.plot(age[m],G(req_mid[m]),color=BLUE,lw=2.0,zorder=4)
_r=12*px.pct_change().shift(-1); _r=_r[(_r.index>="2012-01-01")&(_r.index<="2026-04-30")]   # the monthly test's observations
real_c=_r.rolling(36,center=True,min_periods=18).mean()                                     # centered three-year average
l_real,=ax.plot(age.reindex(real_c.index),G(real_c),color=INK,lw=1.5,zorder=5)
_per=[("2012","2014"),("2015","2017"),("2018","2020"),("2021","2023"),("2024","2026")]
_pa=[age.reindex(_r[a:b].index).mean() for a,b in _per]; _pv=[_r[a:b].mean() for a,b in _per]
l_per,=ax.plot(_pa,_pv,marker="o",mfc="white",mec=INK,mew=1.3,ms=6.5,ls="none",zorder=7)
print("period averages",[round(100*v) for v in _pv])
l_age,=ax.plot(age[m],G(age_rule[m]),color=RED,lw=1.6,zorder=4)
ax.text(etf_age+0.12,0.031,"spot ETFs approved\n(Jan 2024)",fontsize=8.0,color=INK2,va="bottom")
for ha in halv: ax.plot([ha],[7.4],marker="v",color=MUT,ms=5,ls="none",zorder=6,clip_on=False)
for (yr,val,lab,tx,ty) in [(2021.75,0.22,"22%",12.2,0.125),(2025.4,0.138,"13.8%",15.3,0.105)]:
    A_=yr-2009.0
    l_surv,=ax.plot([A_],[G(val)],marker="D",color="#008300",ms=5.5,ls="none",zorder=5)
    ax.annotate(lab,xy=(A_,G(val)),xytext=(tx,ty),fontsize=8.3,color="#008300",arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"))
ax.plot([17.4],[0.18],marker="o",color=BLUE,ms=5.5,zorder=6)
ax.annotate("forecast 18%\n(90% range 15–22%)",xy=(17.4,0.18),xytext=(16.2,0.072),fontsize=8.3,color=BLUE,arrowprops=dict(arrowstyle="-",lw=0.6,color=BLUE))
ax.annotate("age rule 32%",xy=(17.4,0.33),xytext=(16.3,0.56),fontsize=8.3,color=RED,arrowprops=dict(arrowstyle="-",lw=0.6,color=RED))
h_halv=Line2D([],[],color=BASE,lw=0.9,marker="v",mfc=MUT,mec=MUT,ms=5)
ax.legend([l_real,l_per,l_req,Patch(facecolor=SEQ[100],alpha=0.8),l_age,l_surv,h_halv],
          ["realized average return: monthly returns, annualized, as a\ncentered three-year average (to April 2026)","realized average return by three-year period (the monthly test)",
           "required return (midpoint of the band)","required-return band: the average owner (lower edge)\nto the early holder (upper edge until 2018)",
           "age rule forecast","holders' surveyed expectations (2021, 2025)","halvings (Nov 2012, Jul 2016, May 2020, Apr 2024)"],
          loc="upper center",bbox_to_anchor=(0.56,-0.075),ncol=2,fontsize=7.8,frameon=True,framealpha=1.0,edgecolor=GRID,borderpad=0.6,labelspacing=0.4,handlelength=1.8,columnspacing=1.4)
ticks=[0.03,0.05,0.10,0.20,0.50,1.0,2.0,4.0,8.0]
ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_major_formatter(FixedFormatter([f"{int(round(100*t))}%" for t in ticks])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.025,8.0); ax.set_ylabel("% per year (log scale)")
ax.set_title("(a) Required return and realized average return",pad=22)
# ---------- terms ----------
beta_t=beta_term.copy(); mort_t=pd.Series(0.5*(0.003+0.03),index=px.index)
conc_t=(req_mid-rf-beta_t-mort_t).clip(lower=0)
mm=(age>=3.0)&(age<=17.45)
A=age[mm].values; parts=[100*rf[mm].values,100*beta_t[mm].values,100*conc_t[mm].values,100*mort_t[mm].values]
names=["risk-free rate","market risk","concentration risk","mortality risk"]; cols=[BASE,BLUE,ORANGE,AQUA]
tot=sum(parts); shares=[p/tot for p in parts]
ax=axb; ax.set_yscale("log")
ax.plot(A,tot,color=INK,lw=2.0,zorder=5); ax.plot(A,parts[2],color=ORANGE,lw=1.8,zorder=4)
ax.plot(A,parts[0],color=BASE,lw=1.8,zorder=3); ax.plot(A,parts[1],color=BLUE,lw=1.8,zorder=3); ax.plot(A,parts[3],color=AQUA,lw=1.8,ls=(0,(4,2)),zorder=3)
tk=[1,2,5,10,20,50,100,200]
ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter([f"{t}%" for t in tk])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.9,330); ax.set_ylabel("% per year (log scale)")
ax.set_title("(b) The required return, term by term",pad=16)
for y,lab,c in [(tot[-1],"total",INK),(8.6,"market risk",BLUE),(5.6,"concentration risk",ORANGE),(3.7,"risk-free rate",INK2),(1.65,"mortality risk",AQUA)]:
    ax.text(17.55,y,lab,fontsize=8.2,va="center",ha="left",color=c,weight="bold")
ax.plot([17.47,17.53],[parts[1][-1],8.6],color=BLUE,lw=0.6); ax.plot([17.47,17.53],[parts[2][-1],5.6],color=ORANGE,lw=0.6); ax.plot([17.47,17.53],[parts[0][-1],3.7],color=MUT,lw=0.6)
ax=axc
ax.stackplot(A,*[100*s for s in shares],colors=cols,alpha=0.92,lw=0)
ax.set_ylabel("share of required return (%)"); ax.set_ylim(0,100); ax.set_xlabel("Bitcoin age (years)")
ax.set_title("(c) Each term's share of the total",pad=16)
i26=int(np.argmin(np.abs(A-(2026.3-2009.0))))
cum=np.zeros_like(A)
for s,lab,c in zip(shares,names,cols):
    ax.text(17.55,(cum+50*s)[i26],f"{lab} {100*s[i26]:.0f}%",fontsize=8.2,va="center",ha="left",color=c if c!=BASE else INK2,weight="bold")
    cum=cum+100*s
for ax in (axa,axb,axc):
    ax.set_xlim(*XL); ax.grid(axis="y",alpha=1.0); ax.set_axisbelow(True)
    if ax is not axc:
        ax.axvline(etf_age,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
        for ha in halv: ax.axvline(ha,color=BASE,lw=0.9,zorder=1)
for ax in (axa,axb): ax.tick_params(labelbottom=True)
for ax_,pd_ in ((axa,10),(axb,2),(axc,2)):
    sec=ax_.secondary_xaxis("top",functions=(lambda x:x+2009.0,lambda y:y-2009.0))
    sec.set_xticks([2013,2015,2017,2019,2021,2023,2025]); sec.tick_params(labelsize=8,colors=MUT,length=0,pad=pd_); sec.spines["top"].set_visible(False)
axb.annotate("beta near zero on the four years\nto early 2020 (clipped at zero)",xy=(10.8,1.25),xytext=(4.6,4.3),fontsize=7.8,color=BLUE,va="bottom",arrowprops=dict(arrowstyle="-",lw=0.6,color=BLUE))
fig.savefig(f"{MD}/fig_required.pdf"); fig.savefig(f"{MD}/fig_required.png",dpi=130)
print("2026 shares",[round(100*s[-1]) for s in shares], "last parts",[round(p[-1],2) for p in parts], round(tot[-1],1))

# the monthly series behind the figure
_o=pd.DataFrame({"age_years":age,"risk_free":rf,"volatility":np.sqrt(sig2),"beta_4y":beta_roll,"w_lower_edge":w_lo,"w_upper_edge":w_hi,
                 "required_lower":foc_lo,"required_upper":req_hi,"required_midpoint":req_mid,"age_rule":age_rule})[mm]
_o.index.name="month_end"; _o.round(4).to_csv(f"{MD}/required_band_monthly.csv"); print("rows",len(_o))
