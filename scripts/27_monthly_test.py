"""Month-by-month test of the required return (Section 5, Appendix D.2).
At each month-end from January 2012 the required return is evaluated from that date's inputs and
compared with Bitcoin's simple return over the following month. Non-overlapping observations;
figures annualized as twelve times the monthly value. Writes outputs monthly_test.txt and fig_gap."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
exec(open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read().split("# ============ FIG 1")[0])
src=open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
r=px.shift(-1)/px-1                                   # next-month simple return
mo=lambda mu: np.exp(mu/12)-1                         # expected one-month simple return at drift mu
D=pd.DataFrame({"r":r,"lo":mo(foc_lo),"mid":mo(req_mid),"hi":mo(req_hi),"age":((age+1/12)/age)**5.62-1}).dropna()
D=D[D.index>="2012-01-01"]
def stats(s):
    o=dict(n=len(s),real=1200*s.r.mean(),se=1200*s.r.std(ddof=1)/np.sqrt(len(s)))
    for k in ["lo","mid","hi","age"]:
        e=s.r-s[k]; o[k]=1200*s[k].mean(); o["g_"+k]=1200*e.mean(); o["se_"+k]=1200*e.std(ddof=1)/np.sqrt(len(e)); o["t_"+k]=o["g_"+k]/o["se_"+k]
    return o
PER=[("2012","2014","2012–14"),("2015","2017","2015–17"),("2018","2020","2018–20"),("2021","2023","2021–23"),("2024","2026","2024–26")]
ALL=[("2012","2026","2012–26, all")]+PER+[("2012","2017","2012–17"),("2018","2026","2018–26")]
T={lab:stats(D[a:b]) for a,b,lab in ALL}
T["excl. 2013"]=stats(D[(D.index.year!=2013)])
L=[f"months {len(D)}: {D.index[0].date()} to {D.index[-1].date()} (return over the following month)",
   "period            n  realized (se)   band lo-hi   mid | gap vs lo (t)  gap vs mid (se; t)  gap vs hi (t) | gap vs age rule (t)"]
for lab,o in T.items():
    L.append(f"{lab:14s} {o['n']:4d}  {o['real']:5.0f} ({o['se']:3.0f})   {o['lo']:4.0f}-{o['hi']:4.0f}  {o['mid']:4.0f} |  {o['g_lo']:+5.0f} ({o['t_lo']:+.1f})   {o['g_mid']:+5.0f} ({o['se_mid']:3.0f}; {o['t_mid']:+.1f})   {o['g_hi']:+5.0f} ({o['t_hi']:+.1f}) |  {o['g_age']:+5.0f} ({o['t_age']:+.1f})")
L.append(f"correlation of monthly return with required midpoint {np.corrcoef(D.r,D.mid)[0,1]:.2f}; with age rule {np.corrcoef(D.r,D.age)[0,1]:.2f}")
L.append(f"largest month: {D.r.idxmax().date()} start, return {100*D.r.max():.0f}%, contributes {1200*D.r.max()/len(D):.0f} points to the full-sample annualized mean")
open(f"{OUT}/monthly_test.txt","w").write("\n".join(L)+"\n"); print("\n".join(L))

# ---------- the same test as a regression: the intercept (alpha) of the CAPM and of the MCM equation ----------
# CAPM: Bitcoin's excess return over the following month on the S&P 500's. MCM: the same regression after subtracting from
# Bitcoin's return the concentration and mortality terms of the midpoint (the midpoint less its market term), month by month.
import statsmodels.api as sm
_voo=pd.read_csv(os.path.join(DATA,"voo_monthly.csv"),parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; _voo.index=_voo.index+pd.offsets.MonthEnd(0)
RG=pd.DataFrame({"r":r,"s":_voo.pct_change().shift(-1),"rf":mo(rf),"extra":mo(req_mid-beta_term)}).dropna(); RG=RG[RG.index>="2012-01-01"]
def alpha(x,y):
    X_=sm.add_constant(x.s-x.rf); f=sm.OLS(y,X_).fit(); h=sm.OLS(y,X_).fit(cov_type="HAC",cov_kwds={"maxlags":6})
    return dict(a=1200*f.params.iloc[0],se=1200*f.bse.iloc[0],t=f.tvalues.iloc[0],thac=h.tvalues.iloc[0],b=f.params.iloc[1])
AL={lab:(alpha(RG[a_:b_],RG[a_:b_].r-RG[a_:b_].rf),alpha(RG[a_:b_],RG[a_:b_].r-RG[a_:b_].extra)) for a_,b_,lab in ALL}
L2=[f"regression intercepts, percent per year ({len(RG)} months): alpha (se; t; t with robust errors, six lags) and slope",
    "period              CAPM alpha                  slope |  MCM alpha                   slope"]
for lab,(c,m_) in AL.items():
    L2.append(f"alpha {lab:14s} {c['a']:+5.0f} ({c['se']:3.0f}; {c['t']:+.1f}; {c['thac']:+.1f})  {c['b']:5.2f} | {m_['a']:+5.0f} ({m_['se']:3.0f}; {m_['t']:+.1f}; {m_['thac']:+.1f})  {m_['b']:5.2f}")
# cumulative unexplained return: each month's return less what the model allows, with the four-year beta known at that month-end
CU=RG.copy(); CU["bt"]=beta_roll.reindex(CU.index); CU["capm"]=CU.r-CU.rf-CU.bt*(CU.s-CU.rf); CU["mcm"]=CU.r-CU.extra-CU.bt*(CU.s-CU.rf)
for a_,b_ in (("2012","2026"),("2018","2026")):
    x_=CU[a_:b_]; L2.append(f"cumulative unexplained return {a_}-{b_}, points: CAPM {100*x_.capm.sum():+.0f}, MCM {100*x_.mcm.sum():+.0f}; per year: CAPM {1200*x_.capm.mean():+.0f}, MCM {1200*x_.mcm.mean():+.0f}")
open(f"{OUT}/monthly_test.txt","a").write("\n".join(L2)+"\n"); print("\n".join(L2))

plt.rcParams["axes.titlepad"]=10
fig=plt.figure(figsize=(9.4,11.6)); _gs=fig.add_gridspec(3,2,height_ratios=[1.0,0.86,0.86],hspace=0.58,wspace=0.24)
ax=fig.add_subplot(_gs[0,0]); bx=fig.add_subplot(_gs[0,1]); cx=fig.add_subplot(_gs[1,:]); dx_=fig.add_subplot(_gs[2,0]); ex_=fig.add_subplot(_gs[2,1])
x=np.arange(len(PER)); labs=[p[2] for p in PER]; O=[T[l] for l in labs]
DOT=dict(marker="o",ms=7.5,mfc="white",mec=INK,mew=1.6,ls="none")          # delivered: the same open circle as in the figure of the required return
HW=0.30
# (a) delivered return against the band
ax.set_yscale("log")
for i,o in enumerate(O):
    ax.fill_between([i-HW,i+HW],[o["lo"]]*2,[o["hi"]]*2,color=SEQ[100],lw=0,zorder=2)
    ax.plot([i-HW,i+HW],[o["mid"]]*2,color=BLUE,lw=2.4,zorder=3,solid_capstyle="butt")
    ax.text(i+HW+0.05,o["mid"],f"{o['mid']:.0f}",fontsize=8.3,color=BLUE,va="center",ha="left")
    ax.plot([i],[o["real"]],zorder=5,**DOT)
    ax.text(i,o["real"]*1.13,f"{o['real']:.0f}",fontsize=8.8,color=INK,va="bottom",ha="center",weight="bold")
ticks=[10,20,50,100,200,400]; ax.set_yticks(ticks); ax.set_yticklabels([f"{t}%" for t in ticks]); ax.minorticks_off()
ax.set_ylim(10,480); ax.set_xlim(-0.6,len(PER)-0.3); ax.set_xticks(x); ax.set_xticklabels(labs)
ax.set_ylabel("% per year (log scale)"); ax.set_title("(a) Delivered return against the required band",loc="left")
ax.legend([plt.Line2D([],[],**DOT),Patch(facecolor=SEQ[100]),plt.Line2D([],[],color=BLUE,lw=2.4)],
          ["delivered: 12 × the average monthly return","required band, average over the period","required return used in the test: midpoint of the band"],
          loc="upper center",bbox_to_anchor=(0.5,-0.10),ncol=1,fontsize=8.2,frameon=False,handlelength=1.8,labelspacing=0.35)
# (b) the gap, delivered minus midpoint, with one and two standard errors
YL=(-130,300)
bx.axhline(0,color=BLUE,lw=1.4,zorder=2)
for i,o in enumerate(O):
    g,s=o["g_mid"],o["se_mid"]
    lo2,hi2=g-2*s,g+2*s
    bx.plot([i,i],[max(lo2,YL[0]),min(hi2,YL[1])],color=MUT,lw=1.0,zorder=3)
    bx.plot([i,i],[max(g-s,YL[0]),min(g+s,YL[1])],color=INK2,lw=4.0,zorder=4,solid_capstyle="butt")
    bx.plot([i],[g],zorder=5,**DOT)
    bx.text(i+0.14,g,f"{g:+.0f}".replace("-","−"),fontsize=8.8,color=INK,va="center",ha="left",weight="bold")
    if hi2>YL[1]: bx.annotate(f"to {hi2:+.0f}".replace("-","−"),xy=(i,YL[1]),xytext=(i+0.12,YL[1]-14),fontsize=7.8,color=MUT,va="center")
    if lo2<YL[0]: bx.annotate(f"to {lo2:+.0f}".replace("-","−"),xy=(i,YL[0]),xytext=(i+0.12,YL[0]+14),fontsize=7.8,color=MUT,va="center")
bx.set_ylim(*YL); bx.set_xlim(-0.6,len(PER)-0.3); bx.set_xticks(x); bx.set_xticklabels(labs)
bx.set_yticks([-100,0,100,200,300]); bx.set_yticklabels(["−100","0","+100","+200","+300"])
bx.set_ylabel("percentage points per year"); bx.set_title("(b) The gap: delivered minus required (the midpoint)",loc="left")
bx.legend([plt.Line2D([],[],**DOT),plt.Line2D([],[],color=INK2,lw=4.0),plt.Line2D([],[],color=MUT,lw=1.0),plt.Line2D([],[],color=BLUE,lw=1.4)],
          ["gap: circle minus blue line of panel (a)","± one standard error","± two standard errors","zero: delivered equals required"],
          loc="upper center",bbox_to_anchor=(0.5,-0.10),ncol=2,fontsize=8.2,frameon=False,handlelength=1.8,labelspacing=0.35,columnspacing=1.6)
# (c) regression intercepts: CAPM and MCM, by period and for the two long samples
GR=[p[2] for p in PER]+["2012–26, all","2018–26"]; XL=[p[2] for p in PER]+["2012–26","2018–26"]
xc=np.array([0,1,2,3,4,5.6,6.6]); YC=(-130,300)
cx.axhline(0,color=INK2,lw=0.9,zorder=2); cx.axvline(4.8,color=BASE,lw=1.0,zorder=1)
for i_ in (0,2,4,6): cx.axvspan(xc[i_]-0.5,xc[i_]+0.5,color="#f4f3ef",lw=0,zorder=0)
for i,lab in enumerate(GR):
    for k,(o,col,dx) in enumerate(((AL[lab][0],ORANGE,-0.17),(AL[lab][1],BLUE,0.17))):
        g,sd=o["a"],o["se"]; xx=xc[i]+dx
        cx.plot([xx,xx],[max(g-2*sd,YC[0]),min(g+2*sd,YC[1])],color=MUT,lw=1.0,zorder=3)
        cx.plot([xx,xx],[max(g-sd,YC[0]),min(g+sd,YC[1])],color=col,lw=4.0,zorder=4,solid_capstyle="butt",alpha=0.55)
        cx.plot([xx],[g],marker="s" if k==0 else "o",ms=7,mfc=col,mec="white",mew=1.2,ls="none",zorder=5)
        cx.text(xx+(-0.09 if k==0 else 0.09),g,f"{g:+.0f}".replace("-","−"),fontsize=8.6,color=INK,va="center",ha="right" if k==0 else "left",weight="bold")
        if g+2*sd>YC[1]: cx.text(xx+(-0.07 if k==0 else 0.07),YC[1]-16,f"to {g+2*sd:+.0f}".replace("-","−"),fontsize=7.6,color=MUT,va="center",ha="right" if k==0 else "left")
        if g-2*sd<YC[0]: cx.text(xx+(-0.07 if k==0 else 0.07),YC[0]+16,f"to {g-2*sd:+.0f}".replace("-","−"),fontsize=7.6,color=MUT,va="center",ha="right" if k==0 else "left")
cx.set_ylim(*YC); cx.set_xlim(-0.85,7.2); cx.set_xticks(xc); cx.set_xticklabels(XL)
cx.set_yticks([-100,0,100,200,300]); cx.set_yticklabels(["−100","0","+100","+200","+300"])
cx.set_ylabel("percent per year"); cx.set_title("(c) What each model leaves unexplained (alpha): CAPM and MCM side by side, for each three-year period",loc="left")
cx.text(5.0,272,"whole sample, and since 2018",fontsize=8,color=INK2,va="center"); cx.text(2.0,272,"three-year periods",fontsize=8,color=INK2,va="center",ha="center")
cx.legend([plt.Line2D([],[],marker="s",ms=7,mfc=ORANGE,mec="white",ls="none"),plt.Line2D([],[],marker="o",ms=7,mfc=BLUE,mec="white",ls="none"),plt.Line2D([],[],color=INK2,lw=4.0,alpha=0.55),plt.Line2D([],[],color=MUT,lw=1.0)],
          ["CAPM alpha","MCM alpha","± one standard error","± two standard errors"],loc="upper center",bbox_to_anchor=(0.5,-0.13),ncol=4,fontsize=8.2,frameon=False,handlelength=1.8,columnspacing=1.8)
# (d) unexplained return through time, and (e) the same as a share of Bitcoin's excess return: trailing three-year averages (display)
CU["ex"]=CU.r-CU.rf
rc=1200*CU.capm.rolling(36).mean(); rm=1200*CU.mcm.rolling(36).mean(); rx=1200*CU.ex.rolling(36).mean(); td=CU.index+pd.offsets.MonthEnd(1)
X0,X1=pd.Timestamp("2014-10-01"),pd.Timestamp("2026-06-30")
dx_.axhline(0,color=INK2,lw=0.9,zorder=2)
dx_.plot(td,rc.values,color=ORANGE,lw=2.0,zorder=4); dx_.plot(td,rm.values,color=BLUE,lw=2.0,zorder=5)
dx_.plot(td,rx.values,color=MUT,lw=1.4,zorder=3)
dx_.text(td[-1]+pd.Timedelta(40,"D"),rc.dropna().iloc[-1]+9,f"{rc.dropna().iloc[-1]:+.0f}".replace("-","−"),fontsize=8.6,color=INK,va="center",weight="bold",clip_on=False)
dx_.text(td[-1]+pd.Timedelta(40,"D"),rm.dropna().iloc[-1]-9,f"{rm.dropna().iloc[-1]:+.0f}".replace("-","−"),fontsize=8.6,color=INK,va="center",weight="bold",clip_on=False)
dx_.set_xlim(X0,X1); dx_.set_ylim(-120,330); dx_.set_yticks([-100,0,100,200,300]); dx_.set_yticklabels(["−100","0","+100","+200","+300"])
dx_.set_ylabel("percent per year"); dx_.set_title("(d) Unexplained return, in percent a year",loc="left")
# (e) the share of what Bitcoin earned that each model explains: one minus (unexplained over earned), shown between 0 and 100%
ec=(100-100*rc/rx).clip(0,100); em=(100-100*rm/rx).clip(0,100)
ex_.fill_between(td,0,ec.values,color=ORANGE,alpha=0.30,lw=0,zorder=2); ex_.fill_between(td,ec.values,em.values,color=BLUE,alpha=0.22,lw=0,zorder=2)
ex_.plot(td,ec.values,color=ORANGE,lw=2.0,zorder=4); ex_.plot(td,em.values,color=BLUE,lw=2.0,zorder=5)
ex_.axhline(100,color=INK2,lw=0.9,zorder=3)
for (a_,b_,lab_) in (("2012","2026","whole sample"),("2018","2026","since 2018")):
    x_=CU[a_:b_]; L2.append(f"share of Bitcoin's excess return explained, {lab_}: CAPM {100-100*x_.capm.mean()/x_.ex.mean():.0f}%, MCM {100-100*x_.mcm.mean()/x_.ex.mean():.0f}%; excess return {1200*x_.ex.mean():.0f}% a year")
for (a_,b_,lab_) in PER:
    x_=CU[a_:b_]; L2.append(f"share explained {lab_}: CAPM {100-100*x_.capm.mean()/x_.ex.mean():.0f}%, MCM {100-100*x_.mcm.mean()/x_.ex.mean():.0f}%")
_w=CU["2012":"2026"]; _s18=CU["2018":"2026"]
ex_.text(X0+pd.Timedelta(120,"D"),122,f"whole sample:  CAPM {100-100*_w.capm.mean()/_w.ex.mean():.0f}%,  MCM {100-100*_w.mcm.mean()/_w.ex.mean():.0f}%\nsince 2018:  CAPM {100-100*_s18.capm.mean()/_s18.ex.mean():.0f}%,  MCM {100-100*_s18.mcm.mean()/_s18.ex.mean():.0f}%",fontsize=8.3,color=INK,va="center",weight="bold")
ex_.text(X1-pd.Timedelta(60,"D"),104,"100%: all of it explained",fontsize=7.8,color=INK2,va="bottom",ha="right")
ex_.set_xlim(X0,X1); ex_.set_ylim(0,140); ex_.set_yticks([0,25,50,75,100]); ex_.set_yticklabels(["0%","25%","50%","75%","100%"])
ex_.set_ylabel("explained ÷ earned"); ex_.set_title("(e) Share of what Bitcoin earned that each model explains",loc="left")
dx_.legend([plt.Line2D([],[],color=MUT,lw=1.4),plt.Line2D([],[],color=ORANGE,lw=2.0),plt.Line2D([],[],color=BLUE,lw=2.0)],["earned over the risk-free rate","unexplained: CAPM","MCM"],loc="upper center",bbox_to_anchor=(0.5,-0.12),ncol=3,fontsize=8.2,frameon=False,handlelength=1.8,columnspacing=1.8)
ex_.legend([plt.Line2D([],[],color=ORANGE,lw=2.0),plt.Line2D([],[],color=BLUE,lw=2.0)],["explained by the CAPM","explained by the MCM equation"],loc="upper center",bbox_to_anchor=(0.5,-0.12),ncol=2,fontsize=8.2,frameon=False,handlelength=1.8,columnspacing=1.8)
for d_ in ("2017-12-31","2020-12-31","2023-12-31","2026-04-30"): L2.append(f"trailing three-year unexplained return to {d_}: CAPM {rc[:d_].iloc[-1]:+.0f}, MCM {rm[:d_].iloc[-1]:+.0f}; share explained (0 to 100): CAPM {ec[:d_].iloc[-1]:.0f}%, MCM {em[:d_].iloc[-1]:.0f}%")
open(f"{OUT}/monthly_test.txt","a").write("\n".join(L2[-11:])+"\n"); print("\n".join(L2[-11:]))
for a_ in (ax,bx,cx,dx_,ex_): a_.grid(axis="y",alpha=1.0); a_.set_axisbelow(True)
fig.savefig(f"{FIG}/fig_gap.pdf",bbox_inches="tight"); fig.savefig(f"{FIG}/fig_gap.png",dpi=200,bbox_inches="tight"); print("saved fig_gap")
