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

fig,(ax,bx)=plt.subplots(1,2,figsize=(9.4,5.0))
x=np.arange(len(PER)); labs=[p[2] for p in PER]; O=[T[l] for l in labs]
ax.set_yscale("log")
for i,o in enumerate(O):
    ax.fill_between([i-0.27,i+0.27],[o["lo"]]*2,[o["hi"]]*2,color=SEQ[200],alpha=0.85,lw=0,zorder=2)
    ax.plot([i-0.27,i+0.27],[o["mid"]]*2,color=BLUE,lw=2.2,zorder=3)
    ax.plot([i],[o["real"]],marker="o",ms=7.5,color=INK,mec="white",mew=1.2,ls="none",zorder=5)
    ax.text(i+0.33,o["real"],f"{o['real']:.0f}%",fontsize=8.5,color=INK,va="center")
ticks=[10,20,50,100,200,400]; ax.set_yticks(ticks); ax.set_yticklabels([f"{t}%" for t in ticks]); ax.minorticks_off()
ax.set_ylim(10,480); ax.set_xlim(-0.6,len(PER)-0.3); ax.set_xticks(x); ax.set_xticklabels(labs)
ax.set_ylabel("% per year (log scale)"); ax.set_title("Delivered against required",loc="left")
ax.legend([plt.Line2D([],[],marker="o",ms=7,color=INK,ls="none"),Patch(facecolor=SEQ[200],alpha=0.9),plt.Line2D([],[],color=BLUE,lw=2.2)],
          ["realized average return (12 × mean monthly return)","required-return band, average over the period","midpoint of the band"],
          loc="upper center",bbox_to_anchor=(0.5,-0.12),ncol=1,fontsize=8.0,frameon=True,framealpha=1.0,edgecolor=GRID,borderpad=0.8)
YL=(-130,300)
bx.axhline(0,color=BLUE,lw=1.6,zorder=2)
for i,o in enumerate(O):
    g,s=o["g_mid"],o["se_mid"]
    bx.plot([i,i],[max(g-2*s,YL[0]),min(g+2*s,YL[1])],color=MUT,lw=1.2,zorder=3)
    bx.plot([i,i],[max(g-s,YL[0]),min(g+s,YL[1])],color=INK,lw=3.2,zorder=4,solid_capstyle="butt")
    bx.plot([i],[g],marker="o",ms=7.5,color=INK,mec="white",mew=1.2,ls="none",zorder=5)
    bx.text(i+0.16,g+13,f"{g:+.0f}".replace("-","−"),fontsize=8.5,color=INK,va="center")
bx.set_ylim(*YL); bx.set_xlim(-0.6,len(PER)-0.3); bx.set_xticks(x); bx.set_xticklabels(labs)
bx.set_ylabel("percentage points per year"); bx.set_title("The gap: realized minus required (midpoint)",loc="left")
bx.legend([plt.Line2D([],[],marker="o",ms=7,color=INK,ls="none"),plt.Line2D([],[],color=INK,lw=3.2),plt.Line2D([],[],color=MUT,lw=1.2),plt.Line2D([],[],color=BLUE,lw=1.6)],
          ["gap, average over the period","±1 standard error","±2 standard errors (2012–14 extends off the panel)","zero: delivered exactly what was required"],
          loc="upper center",bbox_to_anchor=(0.5,-0.12),ncol=1,fontsize=8.0,frameon=True,framealpha=1.0,edgecolor=GRID,borderpad=0.8)
finish(fig,[ax,bx],f"{FIG}/fig_gap")
