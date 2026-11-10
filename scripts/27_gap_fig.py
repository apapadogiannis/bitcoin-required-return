"""Figure: realized average return minus required return (midpoint), by five-year window,
against the sampling error of a five-year average; and the average miss by period."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
lrm=np.log(px).diff()
d=pd.DataFrame({"real":fwd_mu,"mid":req_mid}).dropna(); d=d[d.index>="2012-01-01"]
d["gap"]=100*(d.real-d.mid)
d["se"]=100*(lrm.rolling(60).std().shift(-60)*np.sqrt(12)).reindex(d.index)/np.sqrt(5)
per=[("2012","2014","2012–14"),("2015","2017","2015–17"),("2018","2021","2018–21")]
rows=[(lab,d[a:b].gap.abs().mean(),d[a:b].se.mean(),100*(d[a:b].gap.abs()<2*d[a:b].se).mean()) for a,b,lab in per]
with open(f"{MD}/gap_summary.txt","w") as f:
    f.write(f"windows {len(d)}; mean gap {d.gap.mean():.1f}; MAE {d.gap.abs().mean():.1f}; mean s.e. {d.se.mean():.1f}; within 1 s.e. {100*(d.gap.abs()<d.se).mean():.0f}%; within 2 s.e. {100*(d.gap.abs()<2*d.se).mean():.0f}%\n")
    for r in rows: f.write("%s: mean absolute gap %.0f, sampling s.e. %.0f, within 2 s.e. %.0f%%\n"%r)
print(open(f"{MD}/gap_summary.txt").read())
fig,(ax,bx)=plt.subplots(1,2,figsize=(9.4,4.9),gridspec_kw=dict(width_ratios=[1.75,1]))
t=d.index
ax.fill_between(t,-2*d.se,2*d.se,color=SEQ[100],alpha=0.55,lw=0,zorder=1)
ax.fill_between(t,-d.se,d.se,color=SEQ[200],alpha=0.75,lw=0,zorder=2)
ax.axhline(0,color=BLUE,lw=1.6,zorder=3)
l,=ax.plot(t,d.gap.clip(lower=-210),color=INK,lw=1.6,zorder=5)
mn=d.gap.min(); ax.annotate(f"off scale: {mn:.0f}",xy=(d.gap.idxmin(),-210),xytext=(pd.Timestamp("2014-06-30"),-195),fontsize=8.3,color=INK2,arrowprops=dict(arrowstyle="-",lw=0.6,color=INK2))
ax.set_ylim(-220,160); ax.set_ylabel("percentage points per year")
ax.set_xlabel("start of the five-year window")
ax.set_title("Realized average return minus required return",loc="left")
ax.legend([l,plt.Line2D([],[],color=BLUE,lw=1.6),Patch(facecolor=SEQ[200],alpha=0.9),Patch(facecolor=SEQ[100],alpha=0.8)],
          ["realized minus required (midpoint of the band)","zero: Bitcoin delivered exactly what was required",
           "±1 standard error of a five-year average return","±2 standard errors"],
          loc="upper center",bbox_to_anchor=(0.5,-0.17),ncol=1,fontsize=8.0,frameon=True,framealpha=1.0,edgecolor=GRID,borderpad=0.8)
x=np.arange(3); wd=0.36
b1=bx.bar(x-wd/2-0.01,[r[1] for r in rows],wd,color=INK,zorder=3)
b2=bx.bar(x+wd/2+0.01,[r[2] for r in rows],wd,color=SEQ[250],zorder=3)
for b in list(b1)+list(b2):
    bx.text(b.get_x()+b.get_width()/2,b.get_height()+1.5,f"{b.get_height():.0f}",ha="center",va="bottom",fontsize=8.5,color=INK)
bx.set_xticks(x); bx.set_xticklabels([r[0] for r in rows]); bx.set_ylim(0,90)
bx.set_xlabel("window start"); bx.set_ylabel("percentage points per year")
bx.set_title("Average size of the gap",loc="left")
bx.legend([b1,b2],["mean absolute gap, realized vs required","1 standard error of a five-year average\n(the typical gap from noise alone)"],
          loc="upper center",bbox_to_anchor=(0.5,-0.17),ncol=1,fontsize=8.0,frameon=True,framealpha=1.0,edgecolor=GRID,borderpad=0.8)
finish(fig,[ax,bx],f"{MD}/fig_gap")
