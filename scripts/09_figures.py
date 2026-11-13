"""Draft figures of the census of deaths. The paper's versions are drawn by 22_pretty_figs.py."""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":9,"axes.titlesize":10,"figure.dpi":160})
OUT=os.environ.get("OUT_DIR","outputs")

# ---- Fig 1: hazard vs age, curated, log-log, with fits ----
b=pd.read_csv(f"{OUT}/hazard_buckets_curated.csv")
b=b[b["deaths"]>0]
mid=np.sqrt(b["a"]*b["b"]); lam=b["lam"]
se=np.sqrt(b["deaths"])/b["exp"]
fig,ax=plt.subplots(figsize=(6.2,4.4))
ax.errorbar(mid,lam,yerr=1.96*se,fmt="o",color="#1f4e8c",capsize=3,ms=5,
            label="empirical hazard (95% CI)")
A=np.linspace(0.3,12,200)
i2=np.argmin(np.abs(mid.values-2.45))
g=0.416; scale=lam.iloc[i2]/(mid.iloc[i2]**g)
ax.plot(A,scale*A**g,color="#1f4e8c",lw=1.4,
        label=r"fitted: $\lambda\propto A^{+0.42}$ (period FE)")
kL=lam.iloc[i2]*mid.iloc[i2]
ax.plot(A,kL/A,"--",color="#b23b3b",lw=1.4,label=r"Lindy: $\lambda=k/A$ (rejected)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("asset age (years)"); ax.set_ylabel("deaths per asset-year")
ax.set_title("Cryptoasset mortality hazard vs age\n1,815 assets, 520 curated deaths, 2010–2026 (Coin Metrics universe)")
ax.legend(fontsize=8,loc="lower right"); ax.grid(alpha=0.25,which="both")
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_hazard_age.png")

# ---- Fig 2: hazard by size + elite ----
sz=pd.read_csv(f"{OUT}/hazard_by_size_curated.csv")
fig,ax=plt.subplots(figsize=(6.2,4.0))
labels=list(sz["q"])+["ever top-50","ever top-20","top-20\njump-collapse"]
vals=list(sz["lam"])+[0.0546,0.0354,0.0030]
los =[np.nan]*4+[0.0452,0.0248,0.0006]
his =[np.nan]*4+[0.0654,0.0490,0.0086]
cols=["#8aa8c8"]*4+["#1f4e8c","#1f4e8c","#b23b3b"]
bars=ax.bar(range(len(vals)),vals,color=cols)
for i,(lo,hi) in enumerate(zip(los,his)):
    if not np.isnan(lo): ax.plot([i,i],[lo,hi],color="k",lw=1.2)
ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels,fontsize=8)
ax.set_ylabel("deaths per asset-year")
for i,v in enumerate(vals):
    ax.text(i,v+0.004,f"{v:.1%}",ha="center",fontsize=8)
ax.set_title("Mortality falls steeply with size; catastrophic death at the top is rare\npeak-volume quartiles vs elite cohorts, curated deaths")
ax.set_ylim(0,0.21)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_size.png")

# ---- Fig 3: cohort return curves (median & mean), price-complete subset ----
res=np.load(f"{OUT}/cohort_res.npy",allow_pickle=True).item()
fig,axes=plt.subplots(1,2,figsize=(9.6,4.2),sharex=True)
colors={"2010-14":"#1f4e8c","2015-17":"#2e7d57","2018-20":"#b2762b","2021-23":"#b23b3b"}
for cname,r in res.items():
    ages=r["ages"]; m=ages>=1
    cagr_mean=r["mean"][m]**(1/ages[m])-1
    cagr_med=r["med"][m]**(1/ages[m])-1
    axes[0].plot(ages[m],100*cagr_mean,color=colors[cname],label=f"{cname} (n={r['n']})")
    axes[1].plot(ages[m],100*cagr_med,color=colors[cname],label=f"{cname} (n={r['n']})")
axes[0].set_title("mean (equal-weight) cohort CAGR"); axes[1].set_title("median asset CAGR")
for ax in axes:
    ax.axhline(0,color="k",lw=0.7); ax.set_xlabel("age (years)"); ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
axes[0].set_ylabel("compound annual return to age A (%)")
axes[0].set_ylim(-100,600); axes[1].set_ylim(-100,200)
fig.suptitle("Buy-at-birth, hold-to-age-A returns by birth cohort — significant-asset subset (n=86), deaths included",fontsize=10)
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_cohorts.png")

# ---- Fig 4: elite death timeline ----
E=pd.read_csv(f"{OUT}/elite_top20_curated.csv",parse_dates=["first_top","death_date"])
D=E[E["death"]==1].copy(); D["yr"]=D["death_date"].dt.year
fig,ax=plt.subplots(figsize=(7.2,3.8))
cnt=D.groupby(["yr","cat"]).size().unstack(fill_value=0)
yrs=range(2014,2027)
fade=[cnt.get(0,pd.Series()).get(y,0) for y in yrs]
cat=[cnt.get(1,pd.Series()).get(y,0) for y in yrs]
ax.bar(yrs,fade,color="#8aa8c8",label="abandonment / delisting")
ax.bar(yrs,cat,bottom=fade,color="#b23b3b",label="jump-collapse (LUNA, UST, FTT)")
ax.set_xticks(list(yrs)); ax.set_xticklabels([str(y) for y in yrs],fontsize=8)
ax.set_ylabel("deaths among ever-top-20 assets")
ax.set_title("When the elite died — 36 deaths among 219 ever-top-20 assets")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_timeline.png")
print("figures saved")
