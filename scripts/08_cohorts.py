import os
"""Cohort unconditional return curves on the price-complete subset.
Buy $1 of each asset at first month-end price; hold; dead/faded assets carry
last price (collapse ~ 0). Equal-weight cohort value by age in months.
Report mean & median CAGR by age, BTC's own curve, and the survivorship wedge.
Also: gamma and cumulative k for the elite subsample.
"""
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf

OUT=os.environ.get("OUT_DIR","outputs"); YR=365.25
PM=pd.read_pickle(f"{OUT}/prices_monthly.pkl")
panel=pd.read_csv(f"{OUT}/panel_v3.csv",parse_dates=["birth","last","death_cur_date"])
V=pd.read_pickle(f"{OUT}/volume_monthly.pkl")

npx=PM.notna().sum()
full=[a for a in PM.columns if npx[a]>=12]
meta=panel.set_index("asset")
full=[a for a in full if a in meta.index and not meta.loc[a,["stable2","tokstock","wrapped_like"]].any()]
print("price-complete assets (>=12 monthly obs, core):",len(full))
print(sorted(full))

# growth path per asset: cumulative multiple vs age (months since first obs)
paths={}
for a in full:
    s=PM[a].dropna()
    g=(s/s.iloc[0]).values
    # carry last value to dataset end (dead or faded assets freeze at last price)
    n_total=(PM.index[-1].to_period("M")-s.index[0].to_period("M")).n+1
    if len(g)<n_total:
        g=np.concatenate([g,np.full(n_total-len(g),g[-1])])
    paths[a]=g

birthyr={a:meta.loc[a,"birth"].year for a in full}
cohdef={"2010-14":range(2010,2015),"2015-17":range(2015,2018),
        "2018-20":range(2018,2021),"2021-23":range(2021,2024)}
print("\ncohort composition:")
res={}
for cname,yrs in cohdef.items():
    members=[a for a in full if birthyr[a] in yrs]
    if len(members)<3: continue
    print(f"  {cname}: n={len(members)}", sorted(members)[:18], "..." if len(members)>18 else "")
    L=min(len(paths[a]) for a in members)
    M=np.vstack([paths[a][:L] for a in members])
    ages=np.arange(L)/12
    mean_mult=M.mean(axis=0); med_mult=np.median(M,axis=0)
    res[cname]=dict(ages=ages,mean=mean_mult,med=med_mult,n=len(members),members=members)
    for A in [1,3,5,7,10]:
        i=int(A*12)
        if i<L:
            cagr_mean=mean_mult[i]**(1/A)-1; cagr_med=med_mult[i]**(1/A)-1
            print(f"     age {A}y: mean CAGR={cagr_mean:+.1%}  median CAGR={cagr_med:+.1%}")

np.save(f"{OUT}/cohort_res.npy",res,allow_pickle=True)

# BTC curve for reference
btc=paths["btc"]; print("\nBTC multiples: 3y",f"{btc[36]:.1f}x","5y",f"{btc[60]:.1f}x","10y",f"{btc[120]:.0f}x")

# wedge at 5y: BTC's realized 5y CAGR from each start vs cohort
print("\n[survivorship wedge] cohort mean-CAGR at 5y vs BTC same-window CAGR:")
btc_s=PM["btc"].dropna()
for cname,r in res.items():
    if len(r["ages"])<61: continue
    members=r["members"]
    # average window: use each member's own 5y window for btc comparison
    btc_cagrs=[]
    for a in members:
        s=PM[a].dropna(); t0=s.index[0]
        t1=t0+pd.DateOffset(years=5)
        b=btc_s[(btc_s.index>=t0)]
        if len(b)<61: continue
        btc_cagrs.append((b.iloc[60]/b.iloc[0])**(1/5)-1)
    coh=r["mean"][60]**(1/5)-1
    if btc_cagrs:
        print(f"  {cname}: cohort {coh:+.1%} vs BTC {np.mean(btc_cagrs):+.1%}  wedge={np.mean(btc_cagrs)-coh:+.1%}")

# ---- elite-subsample gamma & cumulative k ----
E=pd.read_csv(f"{OUT}/elite_top20_curated.csv",parse_dates=["first_top","death_date"])
dataset_end=panel["last"].max()
recs=[]
for _,r in E.iterrows():
    a=r["asset"]
    if a not in meta.index: continue
    b=meta.loc[a,"birth"]
    end=r["death_date"] if r["death"]==1 else dataset_end
    months=pd.period_range(b,end,freq="M")
    for m in months:
        age=((m.to_timestamp()+pd.Timedelta(days=14))-b).days/YR
        if age<=0: continue
        recs.append([a,str(m),age,0])
    if r["death"]==1: recs[-1][3]=1
ppE=pd.DataFrame(recs,columns=["asset","month","age","death"])
ppE["logage"]=np.log(ppE["age"]); ppE["period"]=ppE["month"].str[:4].astype(int).clip(lower=2016).astype(str)
ppE["off"]=np.log(1/12)
mE=smf.glm("death ~ logage + C(period)",data=ppE,family=sm.families.Poisson(),
           offset=ppE["off"]).fit(cov_type="cluster",cov_kwds={"groups":ppE["asset"]})
print(f"\n[elite top-20 subsample] deaths={ppE['death'].sum()}  gamma(FE)={mE.params['logage']:.3f} ({mE.bse['logage']:.3f})")
# cumulative survival over BTC-like life at measured elite hazard
lam=0.0354
import math
print(f"implied 14-yr survival at elite all-cause hazard {lam:.3f}: {math.exp(-lam*14):.2f}")
print(f"implied 14-yr survival at jump hazard 0.0030: {math.exp(-0.0030*14):.3f}")
print(f"survival needed for k=5.6 Lindy over age 3->17.7: {(3/17.7)**5.6:.1e}")
