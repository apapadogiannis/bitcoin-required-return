"""Calibrate the participation-mortality model of Bitcoin's conditional drift.

Model (survival-conditioned drift of the marginal-holder equilibrium):
  mu(t) = r_f(t) + beta*ERP + pi_M(t) + lambda*(1-delta) - y
  pi_M(t) = gamma * sigma^2(t) * kappa(t),   kappa = BTC cap / (q*phi*W)
    gamma: risk aversion (2-4), sigma: trailing 24m annualized vol,
    kappa: BTC's average portfolio weight among its holders (Merton 1987:
           lambda_i = gamma*sigma_i^2*x_i*(1-q_i)/q_i, and x/q = holders'
           average weight; phi = holders' relative wealth, phi<1 early),
    q(t): participation share (addresses shape scaled to survey anchors),
    W(t): global household wealth (UBS GWR).
Outputs: calibration table, money figure (model band vs age rule vs realized
forward 5y CAGR), component decomposition figure.
"""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":9,"axes.titlesize":10,"figure.dpi":160})
OUT=os.environ.get("OUT_DIR","outputs"); os.makedirs(OUT,exist_ok=True)
CSV=os.environ.get("CM_CSV_DIR","data/cmdata/csv")

# ---------- BTC data ----------
btc=pd.read_csv(f"{CSV}/btc.csv",parse_dates=["time"],
    usecols=["time","PriceUSD","CapMrktCurUSD","AdrBalCnt"])
btc=btc.set_index("time")
px=btc["PriceUSD"].dropna().resample("ME").last()
cap=btc["CapMrktCurUSD"].dropna().resample("ME").last()
adr=btc["AdrBalCnt"].dropna().resample("ME").mean()
lr=np.log(px).diff()
sigma=lr.rolling(24).std()*np.sqrt(12)          # trailing 24m annualized vol
GENESIS=pd.Timestamp("2009-01-03")
age=(px.index-GENESIS).days/365.25

# ---------- q(t): addresses shape scaled to survey anchors ----------
# survey anchors (US adults holding, share): Boston Fed SCPC/SDCPC, SHED, Pew
anchors={2014:0.004,2015:0.006,2018:0.012,2019:0.010,2021:0.11,2022:0.10,2023:0.115,2026:0.14}
# scale addresses so that mean log-ratio to anchors is zero
adr_m=adr.reindex(px.index).interpolate()
ratios=[]
for yr,qa in anchors.items():
    t=pd.Timestamp(f"{yr}-06-30")
    i=adr_m.index.get_indexer([t],method="nearest")[0]
    ratios.append(np.log(qa)-np.log(adr_m.iloc[i]))
scale=np.exp(np.mean(ratios))
q=(adr_m*scale).clip(upper=0.25)
# piecewise-survey alternative
yrs=sorted(anchors); qs=[anchors[y] for y in yrs]
q_srv=pd.Series(np.interp(age, [ (pd.Timestamp(f"{y}-06-30")-GENESIS).days/365.25 for y in yrs ], qs),index=px.index)
q_srv[age<yrs[0]-2009-0.5]=np.nan
# extrapolate early survey q with addresses growth rate
q_srv=q_srv.fillna(q)

# ---------- W(t), phi(t), r_f(t) ----------
Wanch={2011:220e12,2013:250e12,2015:280e12,2017:317e12,2019:360e12,2021:454e12,2023:470e12,2026:510e12}
W=pd.Series(np.interp(age,[(pd.Timestamp(f"{y}-06-30")-GENESIS).days/365.25 for y in sorted(Wanch)],
                      [Wanch[y] for y in sorted(Wanch)]),index=px.index)
# holders' relative wealth phi: 0.3 early (retail/hobbyist) -> 1.0 by 2024 (institutional era)
phi=pd.Series(np.clip(np.interp(age,[2,8,15,17.7],[0.3,0.5,0.9,1.0]),0.3,1.0),index=px.index)
rf=pd.Series(np.interp(age,[(pd.Timestamp(f"{y}-06-30")-GENESIS).days/365.25 for y in [2012,2014,2016,2018,2020,2022,2024,2026]],
                       [0.018,0.025,0.018,0.029,0.009,0.030,0.043,0.050]),index=px.index)

# ---------- model components ----------
kappa=(cap.reindex(px.index)/(q*phi*W)).clip(upper=0.6)   # holders' avg weight, capped
kappa_srv=(cap.reindex(px.index)/(q_srv*phi*W)).clip(upper=0.6)
lam_meas=0.003*0.95                                        # measured top-20 jump hazard x loss
betaERP_lo,betaERP_hi=0.013,0.042                          # beta 0.33x4% .. 1.05x4%
def model_mu(gamma,kap):
    return rf+ (betaERP_lo+betaERP_hi)/2 + gamma*(sigma**2)*kap + lam_meas
mu_mid=model_mu(3,kappa)
mu_lo =rf+betaERP_lo+2*(sigma**2)*np.minimum(kappa,kappa_srv)+lam_meas
mu_hi =rf+betaERP_hi+4*(sigma**2)*np.maximum(kappa,kappa_srv)+lam_meas

# early unmeasured existential hazard band (pre-2015): add 0..40 pts shading
early=pd.Series(np.where(age<6.0,np.clip((6.0-age)/4.0,0,1),0),index=px.index)
mu_hi_ex=mu_hi+early*0.40

# ---------- age rule and realized forward 5y ----------
BETA=5.62
age_rule=(1+5/pd.Series(age,index=px.index))**(BETA/5)-1
fwd5=(px.shift(-60)/px)**(1/5)-1

# ---------- calibration table ----------
rows=[]
for yr in [2013,2015,2017,2019,2021,2023,2026]:
    t=pd.Timestamp(f"{yr}-06-30"); i=px.index.get_indexer([t],method="nearest")[0]
    rows.append(dict(year=yr,age=round(age[i],1),sigma=round(float(sigma.iloc[i]),2),
        q=f"{q.iloc[i]:.3%}",kappa=f"{float(kappa.iloc[i]):.1%}",
        pi_M=f"{3*float(sigma.iloc[i])**2*float(kappa.iloc[i]):.1%}",
        mu_model=f"{float(mu_mid.iloc[i]):.0%}",
        age_rule=f"{float(age_rule.iloc[i]):.0%}",
        fwd5=(f"{float(fwd5.iloc[i]):.0%}" if np.isfinite(fwd5.iloc[i]) else "-")))
T=pd.DataFrame(rows)
print(T.to_string(index=False))
T.to_csv(f"{OUT}/calibration_table.csv",index=False)

# ---------- money figure ----------
m=(age>=3.0)
fig,ax=plt.subplots(figsize=(7.6,4.8))
x=pd.Series(age,index=px.index)[m]
ax.fill_between(x,100*mu_lo[m],100*mu_hi_ex[m],color="#1f4e8c",alpha=0.18,
                label="model band (γ=2–4, q variants; pre-2015 incl. existential-hazard allowance)")
ax.fill_between(x,100*mu_lo[m],100*mu_hi[m],color="#1f4e8c",alpha=0.30)
ax.plot(x,100*mu_mid[m],color="#1f4e8c",lw=1.8,label="model μ(t): r_f+βERP+γσ²κ+λ(1−δ)")
ax.plot(x,100*age_rule[m],color="#b23b3b",lw=1.6,label="age rule 5-yr forecast (β=5.62)")
ax.plot(x,100*fwd5[m],color="0.3",lw=1.0,alpha=0.9,label="realized forward 5-yr CAGR")
ax.axhline(0,color="k",lw=0.6)
ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% per year")
ax.set_ylim(-10,220); ax.set_xlim(3,18.5)
ax.set_title("Bitcoin's conditional drift: participation-mortality model vs the age rule vs realized returns")
ax.legend(fontsize=8,loc="upper right"); ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_model_vs_agerule.png")

# ---------- decomposition ----------
fig,ax=plt.subplots(figsize=(7.6,4.4))
piM=3*(sigma**2)*kappa
comps=pd.DataFrame({"r_f":rf,"β·ERP":(betaERP_lo+betaERP_hi)/2,
                    "participation γσ²κ":piM,"mortality λ(1−δ)":lam_meas},index=px.index)[m]
ax.stackplot(x,100*comps.T.values,labels=comps.columns,
             colors=["#c7d4e4","#8aa8c8","#1f4e8c","#b23b3b"],alpha=0.9)
ax.plot(x,100*age_rule[m],color="k",lw=1.3,ls="--",label="age rule forecast")
ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% per year")
ax.set_title("Decomposition of the model drift — the unexplained early gap is the selection/learning wedge")
ax.set_ylim(0,140); ax.legend(fontsize=8); ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_decomposition.png")
print("\ncurrent (Sep 2026-ish) values:")
i=-2
print(f"  sigma={float(sigma.iloc[i]):.2f}  q={float(q.iloc[i]):.3f}  kappa={float(kappa.iloc[i]):.3f}")
print(f"  pi_M(gamma=3)={3*float(sigma.iloc[i])**2*float(kappa.iloc[i]):.3f}")
print(f"  mu_model mid={float(mu_mid.iloc[i]):.3f}  lo={float(mu_lo.iloc[i]):.3f}  hi={float(mu_hi.iloc[i]):.3f}")
print(f"  age rule={float(age_rule.iloc[i]):.3f}")
