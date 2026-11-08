"""Publication-grade restyle of all six manuscript figures.
Unified style: Carlito (Calibri-metric) labels, validated categorical palette
(dataviz reference), sequential blue ramp for ordered size groups, recessive
hairline grid, no top/right spines, direct labels over legend boxes where
feasible, thin marks."""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ---------- style ----------
INK="#0b0b0b"; INK2="#52514e"; MUT="#898781"; GRID="#e1e0d9"; BASE="#c3c2b7"
BLUE="#2a78d6"; ORANGE="#eb6834"; AQUA="#1baf7a"; RED="#e34948"; VIOLET="#6250d6"
SEQ={100:"#cde2fb",200:"#9ec5f4",250:"#86b6ef",350:"#5598e7",450:"#2a78d6",550:"#1c5cab",650:"#104281"}
plt.rcParams.update({
    "font.family":"Carlito","font.size":9.5,"axes.titlesize":11,"axes.titleweight":"bold",
    "axes.labelsize":9.5,"axes.labelcolor":INK2,"axes.edgecolor":BASE,"axes.linewidth":0.8,
    "axes.spines.top":False,"axes.spines.right":False,
    "xtick.color":MUT,"ytick.color":MUT,"xtick.labelsize":8.5,"ytick.labelsize":8.5,
    "grid.color":GRID,"grid.linewidth":0.6,"legend.frameon":False,"legend.fontsize":8.5,
    "figure.dpi":200,"savefig.facecolor":"white","axes.facecolor":"white",
    "text.color":INK,"axes.titlecolor":INK,"axes.titlelocation":"left","axes.titlepad":30})
def finish(fig,ax_list,path):
    for ax in ax_list: ax.grid(axis="y",alpha=1.0); ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f"{path}.pdf"); fig.savefig(f"{path}.png",dpi=200)
    print("saved",os.path.basename(path))

import os
GY=os.environ.get("OUT_DIR","outputs"); MD=os.environ.get("FIG_DIR","figures"); CSV=os.environ.get("CM_CSV_DIR","data/cmdata/csv"); YR=365.25
os.makedirs(MD,exist_ok=True)

# ============ FIG 1: hazard vs age ============
hb=pd.read_csv(f"{GY}/hazard_buckets_curated.csv"); hb=hb[hb["deaths"]>0]
mid=np.sqrt(hb["a"]*hb["b"]); lam=hb["lam"]; se=np.sqrt(hb["deaths"])/hb["exp"]
fig,ax=plt.subplots(figsize=(6.4,4.3))
A=np.linspace(0.32,12,200)
i2=int(np.argmin(np.abs(mid.values-2.45))); g=0.416
ax.plot(A,(lam.iloc[i2]/(mid.iloc[i2]**g))*A**g,color=BLUE,lw=1.8,zorder=3)
ax.plot(A,(lam.iloc[i2]*mid.iloc[i2])/A,color=RED,lw=1.4,ls=(0,(5,3)),zorder=2)
ax.errorbar(mid,lam,yerr=1.96*se,fmt="o",color=INK,ecolor=MUT,elinewidth=1.0,
            capsize=0,ms=4.5,zorder=4)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks([0.3,0.5,1,2,3,5,8,12]); ax.set_xticklabels(["0.3","0.5","1","2","3","5","8","12"])
ax.set_ylim(0.0045,0.52)
ax.set_yticks([0.01,0.03,0.1,0.3]); ax.set_yticklabels(["1%","3%","10%","30%"])
ax.minorticks_off()
ax.set_xlabel("asset age (years)"); ax.set_ylabel("deaths per asset-year")
ax.text(4.3,0.30,"fitted: hazard RISES with age\n(elasticity +0.42)",color=BLUE,fontsize=9,weight="bold")
ax.text(1.02,0.305,"Lindy hypothesis: λ = k/A\n(rejected)",color=RED,fontsize=9,ha="right")
ax.set_title("Cryptoasset mortality rises with age")
ax.text(0,1.018,"1,815 assets, 520 curated deaths, 2010–2026 · dots: empirical hazard ±95% CI",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
ax.grid(which="major",axis="both",alpha=0.9); ax.grid(which="minor",visible=False)
ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(f"{MD}/fig1_hazard_age.pdf"); fig.savefig(f"{MD}/fig1_hazard_age.png",dpi=200)
print("saved fig1")

# ============ FIG 2: hazard by size ============
sz=pd.read_csv(f"{GY}/hazard_by_size_curated.csv")
labels=["smallest\nquartile","Q2","Q3","largest\nquartile","ever\ntop-50","ever\ntop-20","top-20\njump only"]
vals=list(100*sz["lam"])+[5.46,3.54,0.30]
los=[np.nan]*4+[4.52,2.48,0.06]; his=[np.nan]*4+[6.54,4.90,0.86]
cols=[SEQ[200],SEQ[350],SEQ[450],SEQ[650],SEQ[550],SEQ[650],RED]
fig,ax=plt.subplots(figsize=(6.6,4.0))
x=np.arange(len(vals))
ax.bar(x,vals,width=0.62,color=cols,zorder=3)
for i,(lo,hi) in enumerate(zip(los,his)):
    if not np.isnan(lo): ax.plot([i,i],[lo,hi],color=INK,lw=1.1,zorder=4)
tops=[max(v,h) if not np.isnan(h) else v for v,h in zip(vals,his)]
for i,(v,tp) in enumerate(zip(vals,tops)):
    ax.text(i,tp+0.45,f"{v:.1f}%" if v>=1 else f"{v:.2f}%",ha="center",fontsize=9,color=INK,
            weight="bold" if i>=5 else "normal")
ax.set_xticks(x); ax.set_xticklabels(labels,fontsize=8.5,color=INK2)
ax.set_ylabel("deaths per asset-year (%)"); ax.set_ylim(0,20)
ax.set_title("Size protects; catastrophic death at the top is rare")
ax.text(0,1.018,"curated deaths · peak-volume quartiles and elite cohorts · whiskers: exact Poisson 95% CI",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
finish(fig,[ax],f"{MD}/fig2_size")

# ============ FIG 3: KM by size ============
from lifelines import KaplanMeierFitter
panel=pd.read_csv(f"{GY}/panel_v3.csv",parse_dates=["birth","last","death_cur_date"])
core=panel[~panel["stable2"]&~panel["tokstock"]&~panel["wrapped_like"]].copy()
core=core[(core["last"]-core["birth"]).dt.days>=30].set_index("asset")
dataset_end=panel["last"].max()
V=pd.read_pickle(f"{GY}/volume_monthly.pkl"); core["peak_vol"]=V.max().reindex(core.index)
T=np.where(core["dead_cur"],(pd.to_datetime(core["death_cur_date"])-core["birth"]).dt.days/YR,
           (dataset_end-core["birth"]).dt.days/YR)
core["T"]=np.clip(T,1/365.25,None); core["E"]=core["dead_cur"].astype(int)
has=core["peak_vol"].notna()
qs=pd.qcut(core.loc[has,"peak_vol"],4,labels=["smallest quartile","Q2","Q3","largest quartile"])
E20=pd.read_csv(f"{GY}/elite_top20_curated.csv"); elite=set(E20["asset"])
qcols={"smallest quartile":SEQ[200],"Q2":SEQ[350],"Q3":SEQ[450],"largest quartile":SEQ[650]}
fig,ax=plt.subplots(figsize=(6.6,4.5))
ends={}
for q in qs.cat.categories:
    sub=core.loc[has][qs==q]
    km=KaplanMeierFitter().fit(sub["T"],sub["E"])
    sf=km.survival_function_
    ax.plot(sf.index,sf.iloc[:,0],color=qcols[q],lw=1.9,drawstyle="steps-post")
    ends[q]=(min(sf.index.max(),12.9),float(sf[sf.index<=13].iloc[-1,0]),len(sub))
sub=core.loc[core.index.isin(elite)]
km=KaplanMeierFitter().fit(sub["T"],sub["E"]); sf=km.survival_function_
ax.plot(sf.index,sf.iloc[:,0],color=INK,lw=1.9,ls=(0,(4,2)),drawstyle="steps-post")
ends["ever top-20"]=(min(sf.index.max(),12.9),float(sf[sf.index<=13].iloc[-1,0]),len(sub))
# direct labels at line ends
offsets={"smallest quartile":-0.015,"Q2":0.0,"Q3":-0.01,"largest quartile":0.035,"ever top-20":-0.028}
for q,(xe,ye,n) in ends.items():
    c=qcols.get(q,INK)
    yy=ye+offsets.get(q,0)
    ax.plot([13.05,13.55],[yy,yy],color=c,lw=2.6 if q=="ever top-20" else 2.2,
            ls=(0,(3,1.5)) if q=="ever top-20" else "-",clip_on=False)
    ax.text(13.75,yy,f"{q} (n={n})",color=INK2,fontsize=8.8,va="center",
            weight="bold" if q=="ever top-20" else "normal")
ax.set_xlabel("age (years)"); ax.set_ylabel("fraction surviving")
ax.set_xlim(0,13)
ax.spines["bottom"].set_bounds(0,13); ax.set_ylim(0,1.02)
ax.set_yticks([0,0.25,0.5,0.75,1.0]); ax.set_yticklabels(["0%","25%","50%","75%","100%"])
ax.set_title("Survival curves by size")
ax.text(0,1.018,"Kaplan–Meier estimates · 1,815 cryptoassets, curated deaths, 2010–2026",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
finish(fig,[ax],f"{MD}/fig5_km_size")

# ============ FIG 4: elite death timeline ============
E=pd.read_csv(f"{GY}/elite_top20_curated.csv",parse_dates=["death_date"])
D=E[E["death"]==1].copy(); D["yr"]=D["death_date"].dt.year
cnt=D.groupby(["yr","cat"]).size().unstack(fill_value=0)
yrs=list(range(2014,2027))
fade=[int(cnt.get(0,pd.Series()).get(y,0)) for y in yrs]
cat=[int(cnt.get(1,pd.Series()).get(y,0)) for y in yrs]
fig,ax=plt.subplots(figsize=(7.0,3.8))
ax.bar(yrs,fade,width=0.68,color=SEQ[350],zorder=3,label="abandonment / delisting")
ax.bar(yrs,cat,bottom=fade,width=0.68,color=RED,zorder=3,label="jump-collapse")
for y,f,c in zip(yrs,fade,cat):
    if f+c>0: ax.text(y,f+c+0.25,str(f+c),ha="center",fontsize=8.5,color=INK2)
ax.annotate("LUNA, UST, FTT\n(Terra–FTX cascade)",xy=(2022,9.3),xytext=(2019.1,10.6),fontsize=8.5,
            color=RED,ha="center",arrowprops=dict(arrowstyle="-",lw=0.7,color=RED))
ax.annotate("2024–25\ndelisting purge",xy=(2025,12.6),xytext=(2025,13.3),fontsize=8.5,color=INK2,ha="center")
ax.set_xticks(yrs); ax.set_xticklabels([str(y) for y in yrs],fontsize=8.5)
ax.set_ylabel("elite deaths per year"); ax.set_ylim(0,15.5)
ax.set_title("When the elite died")
ax.text(0,1.018,"36 deaths among 219 ever-top-20 assets · deaths cluster in calendar time, not in age",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
ax.legend(loc="upper left")
finish(fig,[ax],f"{MD}/fig4_timeline")

# ============ FIG 5: wedge ============
btcf=pd.read_csv(f"{CSV}/btc.csv",parse_dates=["time"],usecols=["time","PriceUSD","CapMrktCurUSD","AdrBalCnt"]).set_index("time")
px=btcf["PriceUSD"].dropna().resample("ME").last(); cap=btcf["CapMrktCurUSD"].dropna().resample("ME").last()
adr=btcf["AdrBalCnt"].dropna().resample("ME").mean().reindex(px.index).interpolate()
lr=np.log(px).diff(); sig2=lr.pow(2).ewm(halflife=9).mean()*12
GEN=pd.Timestamp("2009-01-03"); age=pd.Series((px.index-GEN).days/365.25,index=px.index)
i21=px.index.get_indexer([pd.Timestamp("2021-09-30")],method="nearest")[0]
q=adr*(0.11/adr.iloc[i21])
def interp(d):
    xs=[(pd.Timestamp(f"{y}-06-30")-GEN).days/365.25 for y in sorted(d)]
    return pd.Series(np.interp(age,xs,[d[y] for y in sorted(d)]),index=px.index)
rf=interp({2012:.018,2014:.025,2016:.018,2018:.029,2020:.009,2022:.030,2024:.043,2026:.050})
Wp=cap.iloc[i21]/0.19*(q/q.iloc[i21])*(interp({2012:0.25,2021:1.0,2026:1.4}))
wbar=(cap.reindex(px.index)/Wp).clip(upper=0.9)
foc_lo=rf+0.0132+1.7*sig2*wbar+0.003
foc_hi=rf+0.042+2.8*sig2*wbar+0.03
seg=interp({2012:1.0,2020:1.0,2022:0.6,2025:0.15,2026:0.10})
req_hi=np.maximum(foc_hi,rf+seg*sig2); req_mid=0.5*(foc_lo+req_hi)
BETA=5.62; age_rule=(1+5/age)**(BETA/5)-1
fwd5=(px.shift(-60)/px)**(1/5)-1
m=age>=3.0
fig,ax=plt.subplots(figsize=(7.6,4.9))
ax.fill_between(age[m],100*foc_lo[m],100*req_hi[m],color=SEQ[100],alpha=0.65,zorder=1)
mm=m&fwd5.notna()
ax.fill_between(age[mm],100*req_mid[mm],100*fwd5[mm],where=(fwd5[mm]>req_mid[mm]),color=AQUA,alpha=0.26,zorder=2)
ax.fill_between(age[mm],100*req_mid[mm],100*fwd5[mm],where=(fwd5[mm]<=req_mid[mm]),color=RED,alpha=0.20,zorder=2)
ax.plot(age[m],100*req_mid[m],color=BLUE,lw=2.0,zorder=4)
ax.plot(age[m],100*fwd5[m],color=INK,lw=1.2,zorder=4)
ax.plot(age[m],100*age_rule[m],color=RED,lw=1.6,zorder=4)
etf_age=(pd.Timestamp("2024-01-11")-GEN).days/365.25
ax.axvline(etf_age,color=MUT,lw=0.9,ls=(0,(2,2)),zorder=1)
ax.text(etf_age+0.12,212,"spot ETFs\n(Jan 2024)",fontsize=8.3,color=INK2)
for (yr,val,lab,tx,ty) in [(2021.75,22,"holders expected 22%",11.0,-11),(2025.4,13.8,"13.8%",17.05,20)]:
    A=yr-2009.0
    ax.plot([A],[val],marker="D",color="#008300",ms=5,zorder=5)
    ax.annotate(lab,xy=(A,val),xytext=(tx,ty),fontsize=8.3,color="#008300",
                arrowprops=dict(arrowstyle="-",lw=0.6,color="#008300"))
ax.text(4.45,224,"realized forward 5-yr CAGR",color=INK,fontsize=8.8,weight="bold")
ax.text(6.05,96,"age rule forecast",color=RED,fontsize=8.8,weight="bold",rotation=-18)
ax.text(13.1,42,"required return of the\nmarginal holder (band + mid)",color=BLUE,fontsize=8.8,weight="bold")
ax.text(9.75,104,"wedge: realized − required\n(green +, red −)",color="#117a55",fontsize=8.6)
ax.axhline(0,color=BASE,lw=0.8)
ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% per year")
ax.set_xlim(3,18.5); ax.set_ylim(-15,232)
ax.set_title("The age rule tracks the decaying wedge, not a risk premium")
ax.text(0,1.018,"required-return band: holder first-order condition (γ 1.7–2.8) up to the option-implied all-in bound",
        transform=ax.transAxes,fontsize=8.5,color=INK2,va="bottom")
finish(fig,[ax],f"{MD}/fig_wedge")

# ============ FIG 6: Ether compression ============
ethf=pd.read_csv(f"{CSV}/eth.csv",parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")
epx=ethf["PriceUSD"].dropna().resample("ME").last()
esig=np.sqrt(np.log(epx).diff().pow(2).ewm(halflife=9).mean()*12)
bsig=np.sqrt(sig2)
efwd3=(epx.shift(-36)/epx)**(1/3)-1; bfwd3=(px.shift(-36)/px)**(1/3)-1
fig,axes=plt.subplots(1,2,figsize=(9.4,3.9))
ax=axes[0]
ax.plot(px.index,100*bsig,color=BLUE,lw=1.7); ax.plot(epx.index,100*esig,color=AQUA,lw=1.7)
ax.axvline(pd.Timestamp("2024-01-11"),color=MUT,ls=(0,(2,2)),lw=0.9)
ax.text(pd.Timestamp("2017-10-01"),205,"Ether",color=AQUA,fontsize=9.5,weight="bold")
ax.text(pd.Timestamp("2018-09-01"),48,"Bitcoin",color=BLUE,fontsize=9.5,weight="bold")
ax.text(pd.Timestamp("2024-03-15"),178,"spot ETFs",fontsize=8.3,color=INK2)
ax.set_ylabel("annualized volatility (%)"); ax.set_ylim(0,235)
ax.set_title("Volatility compresses…")
ax=axes[1]
ax.plot(px.index,100*bfwd3,color=BLUE,lw=1.5); ax.plot(epx.index,100*efwd3,color=AQUA,lw=1.5)
ax.axhline(0,color=BASE,lw=0.8)
ax.text(pd.Timestamp("2018-05-01"),225,"Ether",color=AQUA,fontsize=9.5,weight="bold")
ax.text(pd.Timestamp("2020-03-01"),-45,"Bitcoin",color=BLUE,fontsize=9.5,weight="bold")
ax.set_ylabel("forward 3-yr CAGR (%)"); ax.set_ylim(-80,410)
ax.set_title("…and so does the drift")
for a_ in axes: a_.set_xlim(pd.Timestamp("2016-01-01"),pd.Timestamp("2026-07-01"))
fig.suptitle("Compression is a mechanism, not a Bitcoin idiosyncrasy",x=0.013,ha="left",fontsize=11,fontweight="bold")
fig.tight_layout(rect=(0,0,1,0.94))
for a_ in axes: a_.grid(axis="y",alpha=1.0); a_.set_axisbelow(True)
fig.savefig(f"{MD}/fig6_eth.pdf"); fig.savefig(f"{MD}/fig6_eth.png",dpi=200)
print("saved fig6")
