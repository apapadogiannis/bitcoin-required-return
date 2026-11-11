"""Section 7: the equation for Ether and the other cryptoassets, with measured inputs.
Builds (i) the cap-weighted crypto market return, (ii) each priced asset's volatility, equity beta and
'effective weight' factor kappa = Cov(r_i, r_cm)/Var(r_i), (iii) a survivorship-free equal-weighted altcoin basket."""
import numpy as np, pandas as pd, glob, os, sys
CSV="/tmp/cmdata/csv"; GY="/home/claude/graveyard"; MD="/home/claude/model"
pan=pd.read_csv(f"{GY}/panel_v3.csv",parse_dates=["birth","last","death_cur_date"]).set_index("asset")
core=pan[~pan.stable&~pan.stable2&~pan.tokstock&~pan.wrapped_like]
PX={}; CAP={}
for a in core.index:
    f=f"{CSV}/{a}.csv"
    if not os.path.exists(f): continue
    cols=pd.read_csv(f,nrows=0).columns
    if "PriceUSD" not in cols: continue
    d=pd.read_csv(f,usecols=[c for c in ("time","PriceUSD","CapMrktCurUSD") if c in cols],parse_dates=["time"]).set_index("time")
    p=d["PriceUSD"].dropna()
    if len(p)<400: continue
    PX[a]=p.resample("ME").last()
    if "CapMrktCurUSD" in d: CAP[a]=d["CapMrktCurUSD"].dropna().resample("ME").last()
P=pd.DataFrame(PX); C=pd.DataFrame(CAP).reindex(columns=P.columns)
R=P.pct_change(fill_method=None)
print("priced assets:",P.shape[1],"| with cap:",C.notna().any().sum(),"| dead (curated):",int(core.loc[P.columns,"dead_cur"].sum()))
# peak-volume quartile of the priced assets
try:
    V=pd.read_pickle(f"{GY}/volume_monthly.pkl"); pk=V.max(); qs=pd.qcut(pk.reindex(core.index).dropna(),4,labels=["Q1","Q2","Q3","Q4"])
    print("priced assets by size quartile:",qs.reindex(P.columns).value_counts().to_dict())
except Exception as e: print("no quartiles",e)
# cap-weighted crypto market return (lagged cap weights, assets with price and cap)
W=C.shift(1); W=W.where(R.notna()); W=W.div(W.sum(axis=1),axis=0)
rcm=(W*R).sum(axis=1,min_count=1)
print("BTC weight in the index, 2018/2021/2026:",[round(float(W["btc"].loc[d]),2) for d in ("2018-06-30","2021-09-30","2026-04-30")], "| ETH:",[round(float(W["eth"].loc[d]),2) for d in ("2018-06-30","2021-09-30","2026-04-30")])
v=pd.read_csv(f"{MD}/extdata/voo_monthly.csv",parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; v.index=v.index+pd.offsets.MonthEnd(0)
rs=v.pct_change()
END="2026-04-30"
def stats(a,win=48):
    x=pd.DataFrame({"i":np.log1p(R[a]),"m":np.log1p(rcm),"s":np.log1p(rs),"b":np.log1p(R["btc"])})[:END].dropna().iloc[-win:]
    if len(x)<36: return None
    ew=np.sqrt(np.log1p(R[a][:END]).pow(2).ewm(halflife=9).mean().iloc[-1]*12)
    return dict(n=len(x),vol=x.i.std()*12**.5,vol_ewma=ew,beta_eq=x.cov().loc["i","s"]/x.s.var(),kappa=x.cov().loc["i","m"]/x.i.var(),beta_btc=x.cov().loc["i","b"]/x.b.var(),corr_m=x.corr().loc["i","m"])
print("crypto market vol (4y): %.0f%%"%(100*np.log1p(rcm[:END]).iloc[-48:].std()*12**.5))
for a in ("btc","eth"):
    for w in (48,100):
        s=stats(a,w); print(a,w,{k:round(float(x),2) for k,x in s.items()})
alive=[a for a in P.columns if a not in("btc","eth") and not core.loc[a,"dead_cur"] and P[a][:END].notna().iloc[-1]]
S=pd.DataFrame({a:stats(a) for a in alive if stats(a)}).T.astype(float)
print("alive altcoins with 4y of prices:",len(S)); print(S.describe().loc[["25%","50%","75%"]].round(2).to_string())
S.round(4).to_csv(f"{MD}/cross_section_assets.csv")
# ---------- survivorship-free basket ----------
alt=[a for a in P.columns if a not in("btc","eth")]
Ra=R[alt].copy()
dead=[a for a in alt if core.loc[a,"dead_cur"]]
# a dead asset whose price feed stops is given a final return of -100% in the following month (worst case) or dropped (best case)
Rw=Ra.copy()
for a in dead:
    last=P[a].last_valid_index()
    nxt=last+pd.offsets.MonthEnd(1)
    if nxt in Rw.index and nxt<=pd.Timestamp(END): Rw.loc[nxt,a]=-1.0
Rn=R.shift(-1); Rna=Ra.shift(-1); Rnw=Rw.shift(-1)       # return over the month after each month-end, as in the monthly test
def test(Rx,a0,b0,lab):
    bk=Rx[a0:b0].mean(axis=1).dropna() if isinstance(Rx,pd.DataFrame) else Rx[a0:b0].dropna()
    m=12*bk.mean(); se=12*bk.std()/np.sqrt(len(bk)); cg=np.exp(12*np.log1p(bk).mean())-1
    n=Rx[a0:b0].notna().sum(axis=1) if isinstance(Rx,pd.DataFrame) else pd.Series([1])
    print(f"{lab:44s} {a0} to {b0}: months {len(bk)}, assets {n.min()}-{n.max()}, average {100*m:5.1f}% (se {100*se:4.1f}), compound {100*cg:5.1f}%")
    return m,se,cg
for a0,b0 in (("2018-01","2026-04"),("2021-09","2026-04")):
    test(Rn["btc"],a0,b0,"Bitcoin"); test(Rn["eth"],a0,b0,"Ether")
    test(Rna,a0,b0,"altcoin basket, feed deaths dropped"); test(Rnw,a0,b0,"altcoin basket, feed deaths at -100%")
out=[]
for a in alt:
    p=P[a]["2018-01":"2026-05"].dropna()
    if len(p)<24: continue
    yrs=(p.index[-1]-p.index[0]).days/365.25; out.append((a,(p.iloc[-1]/p.iloc[0])**(1/yrs)-1,bool(core.loc[a,"dead_cur"])))
O=pd.DataFrame(out,columns=["asset","cagr","dead"])
print("per-asset compound return, January 2018 (or listing) to May 2026: assets",len(O),"| median %.0f%% a year"%(100*O.cagr.median()),"| share negative %.0f%%"%(100*(O.cagr<0).mean()),"| share above Bitcoin's %.0f%%"%(100*(O.cagr>((P['btc']['2026-05'].iloc[-1]/P['btc']['2018-01'].iloc[0])**(1/8.33)-1)).mean()),"| dead",int(O.dead.sum()))
O.round(4).to_csv(f"{MD}/cross_section_cagr.csv",index=False)
