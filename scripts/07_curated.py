import os
"""Curated death layer:
- absolute-volume floor: truly abandoned = trailing 3m mean vol < $250k at end
  (kills mania-base false positives)
- migration list (ticker swaps / redenominations / mergers): not deaths
- manual catastrophic events with correct dates (LUNA, UST May 2022)
- drop *_eth pair artifacts
Outputs: corrected population hazard & gamma; elite (ever-top-20/50) hazards
split into abandonment vs jump-collapse; full curated elite death table.
"""
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy import stats

OUT=os.environ.get("OUT_DIR","outputs"); YR=365.25
panel=pd.read_csv(f"{OUT}/panel_v2.csv",parse_dates=["birth","last","death_broad_date","death_strict_date","econ_death_date","vol_death_date","death_any_date"])
V=pd.read_pickle(f"{OUT}/volume_monthly.pkl")
dataset_end=panel["last"].max()

# ---- migrations / redenominations / mergers (holders received successor) ----
MIGRATIONS={"matic","eos","ftm","gnt","rndr","btt","nu","strat","maid","ht",
            "rep","agix","xzc","npxs","bnx","ocean","fet_old","one","klay",
            "mith2","erd","hot_old","dgd","lend","ant","mln_old","sai",
            "ven","poly","grin_?","tomo","nxs?","xem_sym?"}
MIGRATIONS={m for m in MIGRATIONS if "?" not in m and "_old" not in m}
# note: dgd = wind-down with ETH treasury refund (value preserved) -> treated as migration-equivalent
# tomo = TomoChain->Viction rebrand

# ---- manual catastrophic jump-collapses at the top (value-destroying, sudden) ----
CATASTROPHE={"luna":"2022-05-12","ust":"2022-05-12","ftt":"2022-11-10",
             "srm":"2022-11-10","anc":"2022-05-12","mir":"2022-05-12",
             "cel":"2022-06-13","tmtg":"2022-06-28"}
# cel = Celsius token (bankruptcy freeze), tmtg already flagged

# ---- pair/duplicate artifacts ----
panel=panel[~panel["asset"].str.endswith("_eth")].copy()

# ---- absolute abandonment floor ----
final_vol={}
for a in V.columns:
    s=V[a].dropna()
    if len(s)==0: continue
    final_vol[a]=s.tail(3).mean()
panel["final_vol_3m"]=panel["asset"].map(final_vol)

# corrected vol death: original vol-collapse AND final 3m vol < $250k
panel["vol_dead_c"]=panel["vol_dead"]&(panel["final_vol_3m"].fillna(0)<2.5e5)

# curated death: (feed OR corrected-vol OR econ-price) minus migrations, plus manual catastrophes
panel["dead_cur"]=(panel["feed_dead"]|panel["vol_dead_c"]|panel["econ_dead"].fillna(False))
panel.loc[panel["asset"].isin(MIGRATIONS),"dead_cur"]=False
dc=panel[["death_strict_date","econ_death_date","vol_death_date"]].min(axis=1)
panel["death_cur_date"]=dc
for a,d in CATASTROPHE.items():
    i=panel["asset"]==a
    panel.loc[i,"dead_cur"]=True
    panel.loc[i,"death_cur_date"]=pd.Timestamp(d)
panel.loc[~panel["dead_cur"],"death_cur_date"]=pd.NaT
panel["catastrophe"]=panel["asset"].isin(CATASTROPHE)

core=panel[~panel["stable2"]&~panel["tokstock"]&~panel["wrapped_like"]].copy()
core=core[(core["last"]-core["birth"]).dt.days>=30].reset_index(drop=True)
print("core:",len(core)," dead_cur:",core["dead_cur"].sum()," (catastrophes:",core["catastrophe"].sum(),")")

def pp_for(df,dcol,ecol):
    recs=[]
    for _,r in df.iterrows():
        end=r[dcol] if r[ecol] else dataset_end
        if pd.isna(end) or end<r["birth"]: continue
        months=pd.period_range(r["birth"],end,freq="M")
        if len(months)==0: continue
        for m in months:
            age=((m.to_timestamp()+pd.Timedelta(days=14))-r["birth"]).days/YR
            if age<=0: continue
            recs.append([r["asset"],str(m),age,0])
        if r[ecol]: recs[-1][3]=1
    return pd.DataFrame(recs,columns=["asset","month","age","death"])

pp=pp_for(core,"death_cur_date","dead_cur")
pp["logage"]=np.log(pp["age"]); pp["period"]=pp["month"].str[:4].astype(int).clip(lower=2016).astype(str)
pp["off"]=np.log(1/12)
m=smf.glm("death ~ logage + C(period)",data=pp,family=sm.families.Poisson(),
          offset=pp["off"]).fit(cov_type="cluster",cov_kwds={"groups":pp["asset"]})
print(f"[curated population] deaths={pp['death'].sum()}  gamma(FE)={m.params['logage']:.3f} ({m.bse['logage']:.3f})")

print("\nage-bucket hazards (curated):")
edges=np.array([0.1,0.5,1,1.5,2,3,4,5,7,9,12,17]); buck=[]
for a,b in zip(edges[:-1],edges[1:]):
    msk=(pp["age"]>=a)&(pp["age"]<b); e=msk.sum()/12; d=pp.loc[msk,"death"].sum()
    if e>0:
        buck.append(dict(a=a,b=b,deaths=int(d),exp=e,lam=d/e))
        print(f"  {a:>4}-{b:<4}: d={d:3d} exp={e:6.0f}  lambda={d/e:.4f}")
pd.DataFrame(buck).to_csv(f"{OUT}/hazard_buckets_curated.csv",index=False)

core2=core.set_index("asset"); core2["peak_vol"]=V.max().reindex(core2.index)
has=core2["peak_vol"].notna()
qs=pd.qcut(core2.loc[has,"peak_vol"],4,labels=["Q1","Q2","Q3","Q4"])
print("\nhazard by peak-volume quartile (curated):")
sz=[]
for q in qs.cat.categories:
    sub=core2.loc[has][qs==q].reset_index()
    p2=pp_for(sub,"death_cur_date","dead_cur")
    lam=p2["death"].sum()/(len(p2)/12)
    sz.append(dict(q=q,n=len(sub),deaths=int(p2["death"].sum()),lam=lam))
    print(f"  {q}: n={len(sub)} deaths={p2['death'].sum()} lambda={lam:.4f}")
pd.DataFrame(sz).to_csv(f"{OUT}/hazard_by_size_curated.csv",index=False)

ranks=V.rank(axis=1,ascending=False)
elite_tables={}
for TOPN in (20,50):
    ever={}
    for a in V.columns:
        hit=ranks.index[(ranks[a]<=TOPN).fillna(False)]
        if len(hit): ever[a]=hit[0]
    rows=[]
    for a,t0 in ever.items():
        if a not in core2.index: continue
        r=core2.loc[a]
        dead=bool(r["dead_cur"]); dd=r["death_cur_date"]
        end=dd if dead else dataset_end
        if dead and pd.notna(dd) and dd<=t0: continue
        expo=(end-t0).days/YR
        if expo<=0: continue
        rows.append(dict(asset=a,first_top=t0,exp_yr=expo,death=int(dead),
                         cat=int(bool(r["catastrophe"])),death_date=dd))
    E=pd.DataFrame(rows); X=E["exp_yr"].sum()
    for lab,dn in [("all deaths","death"),("jump-collapse only","cat")]:
        d=int(E[dn].sum())
        lo=stats.chi2.ppf(0.025,2*d)/2/X if d>0 else 0
        hi=stats.chi2.ppf(0.975,2*(d+1))/2/X
        print(f"\n[ever top-{TOPN}] {lab}: n={len(E)} exp={X:.0f} d={d} lambda={d/X:.4f} (CI {lo:.4f}-{hi:.4f})")
    if TOPN==20:
        print("\ncurated top-20 death table:")
        print(E[E["death"]==1].sort_values("death_date")[["asset","death_date","cat"]].to_string(index=False))
    elite_tables[TOPN]=E
    E.to_csv(f"{OUT}/elite_top{TOPN}_curated.csv",index=False)

# time profile of elite hazard: split exposure pre/post 2023
E=elite_tables[20].copy()
for cut in [pd.Timestamp("2023-01-01")]:
    d_pre=((E["death"]==1)&(E["death_date"]<cut)).sum()
    d_post=((E["death"]==1)&(E["death_date"]>=cut)).sum()
    # exposure split
    def split(r):
        a=r["first_top"]; b=r["death_date"] if r["death"] else dataset_end
        pre=max(0,(min(b,cut)-a).days)/YR
        post=max(0,(b-max(a,cut)).days)/YR
        return pre,post
    sp=E.apply(split,axis=1,result_type="expand")
    print(f"\n[top-20 era split at {cut.date()}] pre: d={d_pre}, exp={sp[0].sum():.0f}, lam={d_pre/sp[0].sum():.4f} | post: d={d_post}, exp={sp[1].sum():.0f}, lam={d_post/sp[1].sum():.4f}")
    dc_pre=((E["cat"]==1)&(E["death_date"]<cut)).sum(); dc_post=((E["cat"]==1)&(E["death_date"]>=cut)).sum()
    print(f"  jump-collapses: pre={dc_pre} (lam={dc_pre/sp[0].sum():.4f})  post={dc_post} (lam={dc_post/sp[1].sum():.4f})")
panel.to_csv(f"{OUT}/panel_v3.csv",index=False)
