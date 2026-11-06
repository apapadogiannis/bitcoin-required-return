import os
"""Add volume-collapse death; rebuild unified 'abandonment' definition; rerun
gamma regression and elite hazards."""
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy import stats

OUT=os.environ.get("OUT_DIR","outputs"); YR=365.25
panel=pd.read_csv(f"{OUT}/panel_full.csv",parse_dates=["birth","last","death_broad_date","death_strict_date","econ_death_date"])
V=pd.read_pickle(f"{OUT}/volume_monthly.pkl")
dataset_end=panel["last"].max()

print("n_px>=90:", (panel["n_px"]>=90).sum(), "of", len(panel))

# ---- volume-collapse death ----
vrows={}
for a in V.columns:
    s=V[a].dropna()
    if len(s)<6: continue
    peak=s.rolling(12,min_periods=3).mean().max()
    trail=s.rolling(3,min_periods=1).mean()
    if peak is np.nan or peak<=0: continue
    below=trail<0.01*peak
    if len(below)==0: continue
    if below.iloc[-1]:
        idx=np.where(~below.values)[0]
        start=(idx[-1]+1) if len(idx) else 0
        vrows[a]=s.index[start]
panel["vol_dead"]=panel["asset"].map(lambda a: a in vrows)
panel["vol_death_date"]=panel["asset"].map(vrows)

# ---- robust stablecoin flag (median near 1 and P5-P95 inside 0.8-1.2) ----
# approximate from monthly prices where available
PM=pd.read_pickle(f"{OUT}/prices_monthly.pkl")
stab={}
for a in PM.columns:
    s=PM[a].dropna()
    if len(s)<6: continue
    med=s.median()
    if 0.9<=med<=1.1 and s.quantile(0.05)>0.8 and s.quantile(0.95)<1.2:
        stab[a]=True
panel["stable2"]=panel["stable"]|panel["asset"].map(lambda a: stab.get(a,False))

# ---- unified abandonment death ----
panel["dead_any"]=panel["feed_dead"]|panel["econ_dead"].fillna(False)|panel["vol_dead"]
dcols=panel[["death_strict_date","econ_death_date","vol_death_date"]].apply(pd.to_datetime)
panel["death_any_date"]=dcols.min(axis=1)
panel.loc[~panel["dead_any"],"death_any_date"]=pd.NaT
# guard: death date must be after birth+30d
bad=(panel["dead_any"])&((panel["death_any_date"]-panel["birth"]).dt.days<30)
panel.loc[bad,"death_any_date"]=panel.loc[bad,"birth"]+pd.Timedelta(days=30)

core=panel[~panel["stable2"]&~panel["tokstock"]&~panel["wrapped_like"]].copy()
core=core[(core["last"]-core["birth"]).dt.days>=30].reset_index(drop=True)
print("core:",len(core)," dead_any:",core["dead_any"].sum(),
      "(feed",core["feed_dead"].sum(),"| econ",core["econ_dead"].fillna(False).sum(),"| vol",core["vol_dead"].sum(),")")
for a in ["luna","ust","ftt","srm","btc","eth"]:
    r=core[core["asset"]==a]
    if len(r): r=r.iloc[0]; print(f"  {a}: dead_any={r['dead_any']} date={str(r['death_any_date'])[:10]}")

# ---- person-period + gamma regression ----
def pp_for(df,dcol,ecol):
    recs=[]
    for _,r in df.iterrows():
        end=r[dcol] if r[ecol] else dataset_end
        months=pd.period_range(r["birth"],end,freq="M")
        if len(months)==0: continue
        for m in months:
            age=((m.to_timestamp()+pd.Timedelta(days=14))-r["birth"]).days/YR
            if age<=0: continue
            recs.append([r["asset"],str(m),age,0])
        if r[ecol]: recs[-1][3]=1
    return pd.DataFrame(recs,columns=["asset","month","age","death"])

pp=pp_for(core,"death_any_date","dead_any")
pp["logage"]=np.log(pp["age"]); pp["period"]=pp["month"].str[:4].astype(int).clip(lower=2016).astype(str)
pp["off"]=np.log(1/12)
m=smf.glm("death ~ logage + C(period)",data=pp,family=sm.families.Poisson(),
          offset=pp["off"]).fit(cov_type="cluster",cov_kwds={"groups":pp["asset"]})
print(f"\n[abandonment def] person-months={len(pp)}, deaths={pp['death'].sum()}")
print(f"gamma (period FE) = {m.params['logage']:.3f} ({m.bse['logage']:.3f})")

# bucketed hazard
edges=np.array([0.1,0.5,1,1.5,2,3,4,5,7,9,12,17])
print("\nage-bucket hazards (deaths/asset-yr):")
buck=[]
for a,b in zip(edges[:-1],edges[1:]):
    msk=(pp["age"]>=a)&(pp["age"]<b)
    e=msk.sum()/12; d=pp.loc[msk,"death"].sum()
    if e>0:
        buck.append((a,b,int(d),e,d/e))
        print(f"  {a:>4}-{b:<4}: d={d:3d} exp={e:6.0f}  lambda={d/e:.4f}")
pd.DataFrame(buck,columns=["a","b","deaths","exp","lam"]).to_csv(f"{OUT}/hazard_buckets_any.csv",index=False)

# size quartiles
core2=core.set_index("asset")
core2["peak_vol"]=V.max().reindex(core2.index)
has=core2["peak_vol"].notna()
qs=pd.qcut(core2.loc[has,"peak_vol"],4,labels=["Q1","Q2","Q3","Q4"])
print("\nhazard by peak-volume quartile (abandonment def):")
for q in qs.cat.categories:
    sub=core2.loc[has][qs==q].reset_index()
    p2=pp_for(sub,"death_any_date","dead_any")
    print(f"  {q}: n={len(sub)} deaths={p2['death'].sum()} lambda={p2['death'].sum()/(len(p2)/12):.4f}")

# ---- elite top-20 / top-50 ----
ranks=V.rank(axis=1,ascending=False)
for TOPN in (20,50):
    ever={}
    for a in V.columns:
        hit=ranks.index[(ranks[a]<=TOPN).fillna(False)]
        if len(hit): ever[a]=hit[0]
    E=[]
    for a,t0 in ever.items():
        if a not in core2.index: continue
        r=core2.loc[a]
        end=r["death_any_date"] if r["dead_any"] else dataset_end
        if r["dead_any"] and pd.notna(end) and end<=t0: continue
        if pd.isna(end): end=dataset_end
        expo=(end-t0).days/YR
        if expo<=0: continue
        E.append((a,t0,expo,int(r["dead_any"]),r["death_any_date"]))
    E=pd.DataFrame(E,columns=["asset","first_top","exp_yr","death","death_date"])
    d=int(E["death"].sum()); X=E["exp_yr"].sum()
    lo=stats.chi2.ppf(0.025,2*d)/2/X if d>0 else 0
    hi=stats.chi2.ppf(0.975,2*(d+1))/2/X
    print(f"\n[ever top-{TOPN}] n={len(E)} exposure={X:.0f} deaths={d} lambda={d/X:.4f} (CI {lo:.4f}-{hi:.4f})")
    if TOPN==20:
        print(E.loc[E['death']==1].sort_values("death_date")[['asset','death_date']].to_string(index=False))
        E.to_csv(f"{OUT}/elite_top20.csv",index=False)
panel.to_csv(f"{OUT}/panel_v2.csv",index=False)
pp.to_pickle(f"{OUT}/pp_any.pkl")
