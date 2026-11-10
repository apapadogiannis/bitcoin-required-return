"""Robustness (Appendix D.6): the holder-weight back-cast on total cryptoasset capitalization instead of Bitcoin's alone.
The surveys measure the share of crypto as a whole in owners' financial assets; this version clears the whole asset class
(panel assets with a reported capitalization, excluding stablecoins and wrapped or tokenized claims) against participating wealth.
Writes cryptowide_backcast.txt."""
import sys, io
_buf=io.StringIO(); _out=sys.stdout; sys.stdout=_buf
import numpy as np, pandas as pd, glob, os, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
exec(open("/home/claude/model/22_pretty_figs.py").read().split("# ============ FIG 1")[0])
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
caps={}
for f in glob.glob("/tmp/cmdata/csv/*.csv"):
    if "CapMrktCurUSD" in pd.read_csv(f,nrows=0).columns:
        c=pd.read_csv(f,usecols=["time","CapMrktCurUSD"],parse_dates=["time"]).set_index("time")["CapMrktCurUSD"].dropna()
        if len(c): caps[os.path.basename(f)[:-4]]=c.resample("ME").last()
C=pd.DataFrame(caps).reindex(px.index)
stable=[c for c in C.columns if any(c.startswith(p) for p in ["usdt","usdc","dai","busd","tusd","pax","usdp","gusd","husd","susd","fdusd","pyusd","usdd","eurs","eurt","usdk","lusd","frax","ust","xaut","paxg","wbtc","renbtc","steth","wsteth","weth"])]
print("excluded:",sorted(stable))
tot=C.drop(columns=stable).sum(axis=1); dom=cap.reindex(px.index)/tot
print("dominance:",{d:round(float(dom.loc[d]),2) for d in ["2013-06-30","2015-06-30","2017-06-30","2018-01-31","2019-06-30","2021-09-30","2023-06-30","2026-05-31"]})
Wp2=tot.iloc[i21]/0.19*(q/q.iloc[i21])*(interp({2012:0.25,2021:1.0,2026:1.4}))
w_hi2=(tot/Wp2).clip(upper=0.9); w_lo2=(tot/(Wp2+inst_val/0.015)).clip(upper=0.9)
for d in ["2013-06-30","2015-06-30","2017-06-30","2019-06-30","2021-06-30","2021-09-30","2023-06-30","2026-05-31"]:
    print(d,"base w_hi %.3f w_lo %.3f | total-cap w_hi %.3f w_lo %.3f"%(w_hi.loc[d],w_lo.loc[d],w_hi2.loc[d],w_lo2.loc[d]))
foc_lo2=rf+0.85*beta_term+1.7*sig2*w_lo2+0.003; foc_hi2=rf+1.15*beta_term+2.8*sig2*w_hi2+0.03
req_hi2=np.maximum(foc_hi2,rf+seg*sig2); req_mid2=0.5*(foc_lo2+req_hi2)
r=px.shift(-1)/px-1; mo=lambda mu: np.exp(mu/12)-1
for lab,(lo,mi,hi) in {"base":(foc_lo,req_mid,req_hi),"total cap":(foc_lo2,req_mid2,req_hi2)}.items():
    D=pd.DataFrame({"r":r,"lo":mo(lo),"mid":mo(mi),"hi":mo(hi)}).dropna(); D=D[D.index>="2012-01-01"]
    for a,b in [("2012","2026"),("2012","2017"),("2018","2026")]:
        s=D[a:b]; e=s.r-s.mid; print(f"{lab:10s} {a}-{b}: delivered {1200*s.r.mean():.0f} band {1200*s.lo.mean():.0f}-{1200*s.hi.mean():.0f} mid {1200*s.mid.mean():.0f} gap lo {1200*(s.r-s.lo).mean():+.0f} mid {1200*e.mean():+.0f} (se {1200*e.std(ddof=1)/np.sqrt(len(e)):.0f}) hi {1200*(s.r-s.hi).mean():+.0f}")
    print("   2026 band %.1f-%.1f mid %.1f"%(100*lo.iloc[-1],100*hi.iloc[-1],100*mi.iloc[-1]))
exec(open("/home/claude/model/23_uncertainty.py").read().split('if __name__')[0])
run("Bitcoin base w 0.08-0.19",0.42,1.5,2.0,0.08,0.19,0.003,0.03)
run("Bitcoin w %.3f-%.3f"%(w_lo2.iloc[-1],w_hi2.iloc[-1]),0.42,1.5,2.0,float(w_lo2.iloc[-1]),float(w_hi2.iloc[-1]),0.003,0.03)
run("Bitcoin w %.3f-0.19"%(w_lo2.iloc[-1]),0.42,1.5,2.0,float(w_lo2.iloc[-1]),0.19,0.003,0.03)

sys.stdout=_out; open("/home/claude/model/cryptowide_backcast.txt","w").write(_buf.getvalue()); print(_buf.getvalue())
