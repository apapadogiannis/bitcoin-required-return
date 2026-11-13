"""Figure: Ether's volatility and realized average return alongside Bitcoin's, in the measures used for Bitcoin elsewhere."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
exec(open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read().split("# ============ FIG 1")[0])
src=open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
epx=pd.read_csv(f"{CSV}/eth.csv",parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna().resample("ME").last()
esig=np.sqrt(np.log(epx).diff().pow(2).ewm(halflife=9).mean()*12); bsig=np.sqrt(sig2)
def cma(p):
    r=12*p.pct_change().shift(-1); r=r[:"2026-04-30"].dropna(); return r.rolling(36,center=True,min_periods=18).mean()
bc=cma(px)["2016":]; ec=cma(epx)["2016":]
print("min centered averages: BTC %.2f ETH %.2f"%(bc.min(),ec.min()))
ETF_B=pd.Timestamp("2024-01-11"); ETF_E=pd.Timestamp("2024-07-23")
plt.rcParams["axes.titlepad"]=10
fig,axes=plt.subplots(1,2,figsize=(9.4,3.7))
ax=axes[0]
ax.plot(bsig.index,100*bsig,color=BLUE,lw=1.7); ax.plot(esig.index,100*esig,color=AQUA,lw=1.7)
ax.text(pd.Timestamp("2017-10-01"),205,"Ether",color=AQUA,fontsize=9.5,weight="bold"); ax.text(pd.Timestamp("2018-09-01"),48,"Bitcoin",color=BLUE,fontsize=9.5,weight="bold")
ax.set_ylabel("% per year"); ax.set_ylim(0,235); ax.set_title("(a) Volatility")
ax=axes[1]; ax.set_yscale("log")
ax.plot(bc.index,np.maximum(bc,0.03),color=BLUE,lw=1.7); ax.plot(ec.index,np.maximum(ec,0.03),color=AQUA,lw=1.7)
tk=[0.05,0.10,0.20,0.50,1.0,2.0,5.0,10.0]
ax.yaxis.set_major_locator(FixedLocator(tk)); ax.yaxis.set_major_formatter(FixedFormatter([f"{int(round(100*t))}%" for t in tk])); ax.yaxis.set_minor_locator(NullLocator())
ax.set_ylim(0.04,14); ax.set_ylabel("% per year (log scale)"); ax.set_title("(b) Realized average return, centered three-year average")
ax.text(pd.Timestamp("2016-08-01"),7.0,"Ether",color=AQUA,fontsize=9.5,weight="bold"); ax.text(pd.Timestamp("2018-03-01"),0.12,"Bitcoin",color=BLUE,fontsize=9.5,weight="bold")
for a_ in axes:
    a_.set_xlim(pd.Timestamp("2016-01-01"),pd.Timestamp("2026-07-01")); a_.grid(axis="y",alpha=1.0); a_.set_axisbelow(True)
    a_.axvline(ETF_B,color=MUT,ls=(0,(2,2)),lw=0.9); a_.axvline(ETF_E,color=MUT,ls=(0,(2,2)),lw=0.9)
axes[0].text(pd.Timestamp("2021-07-01"),215,"spot ETFs: Bitcoin (Jan 2024),\nEther (Jul 2024)",fontsize=8.0,color=INK2,va="top")
fig.tight_layout()
fig.savefig(f"{FIG}/fig6_eth.pdf"); fig.savefig(f"{FIG}/fig6_eth.png",dpi=140)
