"""Size-conditional and elite hazards.
(1) hazard by peak-volume quartile (volume available for ~all assets)
(2) 'ever top-N by monthly volume' cohort: hazard after first entering top-N,
    with named deaths — the lambda relevant for a dominant asset.
"""
import os, numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf

CSV_DIR=os.environ.get("CM_CSV_DIR","data/cmdata/csv"); OUT=os.environ.get("OUT_DIR","outputs"); YR=365.25
panel=pd.read_csv(f"{OUT}/panel_full.csv",parse_dates=["birth","last","death_broad_date"])
core=panel[~panel["stable"]&~panel["tokstock"]&~panel["wrapped_like"]].copy()
core=core[(core["last"]-core["birth"]).dt.days>=30].reset_index(drop=True)
dataset_end=panel["last"].max()

# ---- monthly volume matrix for core assets ----
vol={}
for a in core["asset"]:
    f=os.path.join(CSV_DIR,a+".csv")
    try:
        df=pd.read_csv(f,usecols=lambda c:c in("time","volume_reported_spot_usd_1d"),parse_dates=["time"])
    except Exception: continue
    if "volume_reported_spot_usd_1d" not in df.columns: continue
    v=pd.to_numeric(df["volume_reported_spot_usd_1d"],errors="coerce")
    s=pd.Series(v.values,index=df["time"]).dropna()
    s=s[(s>0)&(s<1e12)]   # a reported volume above $1 trillion a day is a feed error
    if len(s)<10: continue
    vol[a]=s.resample("ME").mean()
V=pd.DataFrame(vol)
print("volume matrix:",V.shape)
V.to_pickle(f"{OUT}/volume_monthly.pkl")

core=core.set_index("asset")
core["peak_vol"]=V.max().reindex(core.index)
has=core["peak_vol"].notna()
print("assets with volume:",has.sum())

# ---- hazard by peak-volume quartile (person-period) ----
def pp_for(df):
    recs=[]
    for a,r in df.iterrows():
        end=r["death_broad_date"] if r["dead_broad"] else dataset_end
        months=pd.period_range(r["birth"],end,freq="M")
        if len(months)==0: continue
        for j,m in enumerate(months):
            age=((m.to_timestamp()+pd.Timedelta(days=14))-r["birth"]).days/YR
            if age<=0: continue
            recs.append((a,str(m),age,0))
        if r["dead_broad"]: recs[-1]=recs[-1][:3]+(1,)
    return pd.DataFrame(recs,columns=["asset","month","age","death"])

qs=pd.qcut(core.loc[has,"peak_vol"],4,labels=["Q1 small","Q2","Q3","Q4 large"])
print("\nhazard by peak-volume quartile (deaths/asset-yr, broad):")
rows=[]
for q in qs.cat.categories:
    sub=core.loc[has][qs==q]
    pp=pp_for(sub)
    lam=pp["death"].sum()/(len(pp)/12)
    rows.append((q,len(sub),int(pp['death'].sum()),round(len(pp)/12),round(lam,4)))
    print(f"  {q}: n={len(sub)}, deaths={pp['death'].sum()}, exposure={len(pp)/12:.0f} yr, hazard={lam:.4f}")
pd.DataFrame(rows,columns=["quartile","n","deaths","exp_yr","hazard"]).to_csv(f"{OUT}/hazard_by_size.csv",index=False)

# gamma within large half
subL=core.loc[has][qs.isin(["Q3","Q4 large"])]
ppL=pp_for(subL); ppL["logage"]=np.log(ppL["age"])
ppL["period"]=ppL["month"].str[:4].astype(int).clip(lower=2016).astype(str)
ppL["off"]=np.log(1/12)
mL=smf.glm("death ~ logage + C(period)",data=ppL,family=sm.families.Poisson(),
           offset=ppL["off"]).fit(cov_type="cluster",cov_kwds={"groups":ppL["asset"]})
print(f"\n[upper-half size] gamma (FE) = {mL.params['logage']:.3f} ({mL.bse['logage']:.3f}), deaths={ppL['death'].sum()}")

# ---- elite: ever top-N by monthly volume ----
for TOPN in (20,50):
    ranks=V.rank(axis=1,ascending=False)
    ever=pd.Series(pd.NaT,index=V.columns)
    for a in V.columns:
        hit=ranks.index[(ranks[a]<=TOPN).fillna(False)]
        if len(hit): ever[a]=hit[0]
    elite=ever.dropna()
    elite=elite[elite.index.isin(core.index)]
    rows=[]
    for a,t0 in elite.items():
        r=core.loc[a]
        end=r["death_broad_date"] if r["dead_broad"] else dataset_end
        if pd.isna(end) or end<=t0:
            if r["dead_broad"] and end<=t0: continue
            end=dataset_end
        expo=(end-t0).days/YR
        if expo<=0: continue
        rows.append((a,t0,expo,int(r["dead_broad"]),r["death_broad_date"]))
    E=pd.DataFrame(rows,columns=["asset","first_top","exp_yr","death","death_date"])
    lam=E["death"].sum()/E["exp_yr"].sum()
    import math
    d=E["death"].sum(); lo=0.5*math.nan if d==0 else None
    # exact Poisson CI
    from scipy import stats
    lo=stats.chi2.ppf(0.025,2*d)/2/E["exp_yr"].sum() if d>0 else 0.0
    hi=stats.chi2.ppf(0.975,2*(d+1))/2/E["exp_yr"].sum()
    print(f"\n[ever top-{TOPN} by monthly volume] n={len(E)}, exposure={E['exp_yr'].sum():.0f} asset-yr, deaths={d}")
    print(f"  hazard = {lam:.4f}/yr  (95% CI {lo:.4f}–{hi:.4f})")
    print("  deaths:",E.loc[E['death']==1,['asset','death_date']].to_string(index=False))
    if TOPN==50: E.to_csv(f"{OUT}/elite_top50.csv",index=False)
