"""The equity premium held at 4% against a premium that moves (robustness to Section 4's convention).
The band and the month-by-month test of Section 5 are recomputed with the premium implied by the level of the
S&P 500 at each month-end (Damodaran, monthly, trailing twelve-month cash flows) and with fixed values of 3% to 6%.
Nothing else changes. Writes outputs/equity_premium.txt.

data/implied_equity_premium_monthly.csv holds one column of Damodaran's file "Implied ERP by month"
(https://pages.stern.nyu.edu/~adamodar/), in percent. A value dated at the start of a month is what was known at the
month-end before, and is used there."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import statsmodels.api as sm
exec(open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read().split("# ============ FIG 1")[0])
src=open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
assert ERP==0.04
_base=req_mid.copy()

_f=pd.read_csv(os.path.join(DATA,"implied_equity_premium_monthly.csv"))
implied=pd.Series(_f.implied_premium.values/100,index=pd.to_datetime(_f.start_of_month+"-01")-pd.offsets.MonthEnd(1)).reindex(px.index)

r=px.shift(-1)/px-1                                   # next-month simple return
mo=lambda mu: np.exp(mu/12)-1                         # expected one-month simple return at drift mu
_voo=pd.read_csv(os.path.join(DATA,"voo_monthly.csv"),parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; _voo.index=_voo.index+pd.offsets.MonthEnd(0)
s_next=_voo.pct_change().shift(-1)

def band(erp):
    """The band of Section 5 with another equity premium: a number, or a series by month-end."""
    bt=beta_roll*erp
    lo=rf+0.85*bt+G_LO*sig2*w_lo+0.003
    hi=np.maximum(rf+1.15*bt+G_HI*sig2*w_hi+0.035,rf+seg*sig2)
    return bt,lo,hi,0.5*(lo+hi)

def test(erp,a,b):
    bt,lo,hi,mid=band(erp)
    # the gap: every month that has a following month, as in 27_monthly_test.py
    D=pd.DataFrame({"r":r,"mid":mo(mid),"prem":erp if isinstance(erp,pd.Series) else pd.Series(erp,index=px.index)}).dropna(); D=D[D.index>="2012-01-01"][a:b]
    gap=D.r-D.mid
    # the regression and the unexplained return: the months that also have an S&P 500 return
    RG=pd.DataFrame({"r":r,"s":s_next,"rf":mo(rf),"extra":mo(mid-bt),"bt":beta_roll}).dropna(); RG=RG[RG.index>="2012-01-01"][a:b]
    capm_u=RG.r-RG.rf-RG.bt*(RG.s-RG.rf); mcm_u=RG.r-RG.extra-RG.bt*(RG.s-RG.rf)  # unexplained, with the beta known at that month-end
    f=sm.OLS(RG.r-RG.extra,sm.add_constant(RG.s-RG.rf)).fit()
    ex=(RG.r-RG.rf).mean()
    return dict(n=len(D),prem=100*D.prem.mean(),req=1200*D.mid.mean(),gap=1200*gap.mean(),se=1200*gap.std(ddof=1)/np.sqrt(len(D)),
                unexpl=1200*mcm_u.mean(),share=100*(1-mcm_u.mean()/ex),alpha=1200*f.params.iloc[0],alpha_se=1200*f.bse.iloc[0])

assert np.allclose(band(ERP)[3].dropna(),_base.dropna())
last=req_mid.dropna().index[-1]
CASES=[("4%, as in the paper",0.04),("implied, month by month",implied),("3%",0.03),("5%",0.05),("6%",0.06)]
i_=implied[implied.index>="2012-01-01"].dropna()
L=[f"implied equity premium (Damodaran, trailing twelve-month cash flows), month-ends {i_.index[0].date()} to {i_.index[-1].date()}: "
   f"mean {100*i_.mean():.2f}%, low {100*i_.min():.2f}% ({i_.idxmin():%b %Y}), high {100*i_.max():.2f}% ({i_.idxmax():%b %Y}), last {100*i_.iloc[-1]:.2f}%; "
   f"mean since 2018 {100*i_['2018':].mean():.2f}%",
   f"required return at {last.date()} (midpoint; band) and the month-by-month test, percent a year",
   "premium                    at the last month-end      | sample   n  avg premium  required  gap (se)      unexplained  explained by MCM  regression alpha (se)"]
for name,e in CASES:
    bt,lo,hi,mid=band(e)
    now=f"{100*mid[last]:5.1f} ({100*lo[last]:4.1f} to {100*hi[last]:4.1f})"
    for a,b,lab in (("2012","2026","2012-26"),("2018","2026","2018-26")):
        o=test(e,a,b)
        L.append(f"{name:26s} {now:24s} | {lab}  {o['n']:3d}  {o['prem']:5.2f}       {o['req']:6.1f}   {o['gap']:+6.1f} ({o['se']:3.0f})   {o['unexpl']:+6.1f}       {o['share']:5.1f}%            {o['alpha']:+6.1f} ({o['alpha_se']:3.0f})")
_,_,_,m2=band(implied); d=100*(m2-_base)[lambda x: x.index>="2012-01-01"].dropna()
L.append(f"change in the midpoint, implied premium less 4%, points: mean {d.mean():+.1f}, largest {d.max():+.1f} ({d.idxmax():%b %Y}), smallest {d.min():+.1f} ({d.idxmin():%b %Y})")
L.append("the unexplained return and the regression alpha use the S&P 500's realized return, not the premium assumed; the premium enters them only through "
         "the months in which the early holder sets the upper edge of the band, where the midpoint carries less than the full market term")
open(f"{OUT}/equity_premium.txt","w").write("\n".join(L)+"\n"); print("\n".join(L))
