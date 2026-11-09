"""Figure: the three risk terms of equation (1) plus the risk-free rate, over Bitcoin's life.
Mid-band decomposition: rf(t); beta term at the midpoint of 1.3-4.2 points; mortality at the
midpoint of 0.3-3 points; concentration = required (mid) minus the other three, which absorbs
the gamma*sigma^2*w term and the all-in option bound of the band's upper edge."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])  # style block only
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
beta_t=pd.Series(0.5*(0.0132+0.042),index=px.index); mort_t=pd.Series(0.5*(0.003+0.03),index=px.index)
conc_t=(req_mid-rf-beta_t-mort_t).clip(lower=0)
m=(age>=3.0)&(age<=17.45)
A=age[m].values; parts=[100*rf[m].values,100*beta_t[m].values,100*conc_t[m].values,100*mort_t[m].values]
labels=["risk-free rate","market risk  β·ERP","concentration  γσ²w","mortality  λ(1−δ)"]
cols=[BASE,BLUE,ORANGE,AQUA]
tot=sum(parts); shares=[p/tot for p in parts]

plt.rcParams["axes.titlepad"]=8
fig,axes=plt.subplots(1,2,figsize=(8.6,5.0),gridspec_kw={"width_ratios":[1,1.12]})
ax=axes[0]
ax.stackplot(A,*parts,colors=cols,alpha=0.92,lw=0)
ax.set_ylabel("% per year"); ax.set_xlabel("Bitcoin age (years)")
ax.set_xlim(3,17.5); ax.set_ylim(0,215)
ax.set_title("Levels: the required return and its parts")
ax=axes[1]
ax.stackplot(A,*[100*s for s in shares],colors=cols,alpha=0.92,lw=0)
ax.set_ylabel("share of required return (%)"); ax.set_xlabel("Bitcoin age (years)")
ax.set_xlim(3,17.5); ax.set_ylim(0,100)
ax.set_title("Weights: who gets paid for what")
def share_at(y):
    return int(np.argmin(np.abs(A-(y-2009.0))))
i26=share_at(2026.3); i13=share_at(2013.5)
cum=np.zeros_like(A)
for s,lab,c in zip(shares,labels,cols):
    mid=cum+50*s
    ax.text(17.7,mid[i26],f"{lab}\n{100*s[i26]:.0f}% in 2026",fontsize=8.3,va="center",ha="left",color=c if c!=BASE else INK2,weight="bold")
    cum=cum+100*s
ax.spines["right"].set_visible(False)
axes[0].text(6.3,150,"2013: concentration is\n%d%% of a %d%% requirement"%(round(100*shares[2][i13]),round(tot[i13])),fontsize=8.3,color=INK2)
axes[0].annotate("2026: %.0f%% (band midpoint)"%tot[i26],xy=(A[i26],tot[i26]),xytext=(12.2,62),fontsize=8.3,color=INK2,
                 arrowprops=dict(arrowstyle="-",lw=0.6,color=MUT))
for a in axes:
    sec=a.secondary_xaxis("top",functions=(lambda x:x+2009.0,lambda y:y-2009.0))
    sec.set_xticks([2013,2016,2019,2022,2025]); sec.tick_params(labelsize=8,colors=MUT,length=2)
    sec.spines["top"].set_visible(False)
fig.suptitle("Equation (1), term by term: concentration carried the early requirement; the floor terms carry today's",
             x=0.013,y=0.985,ha="left",fontsize=11,fontweight="bold")
fig.text(0.013,0.925,"mid-band decomposition of the monthly required return; beta and mortality at the midpoints of their stated ranges, concentration as the remainder",
         fontsize=8.5,color=INK2)
fig.tight_layout(rect=(0,0,0.97,0.925))
fig.savefig(f"{MD}/fig_terms.pdf"); fig.savefig(f"{MD}/fig_terms.png",dpi=200)
for y in [2013.5,2015.5,2017.5,2019.5,2021.75,2023.5,2026.3]:
    i=share_at(y); print(y, "total %.0f%%"%tot[i], " ".join(f"{l.split()[0]} {100*s[i]:.0f}%" for l,s in zip(labels,shares)))
