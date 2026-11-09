"""Model-side audit: recompute every quantitative claim of Sections 1-2, 5-9 and Appendices B.5, C, D
from the data and the band construction, and compare with the manuscript's numbers."""
import numpy as np, pandas as pd, re, sys
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src.split("# ============ FIG 1")[0].replace('matplotlib.use("Agg")','matplotlib.use("Agg")'))
exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
tex=open("/home/claude/model/manuscript.tex").read()
qpart=q.copy()
res=[]
def chk(label,val,claim,tol):
    ok=abs(val-claim)<=tol; res.append((ok,label,val,claim)); print(f"{'PASS' if ok else 'FAIL':5s} {label}: computed {val:.3g} vs paper {claim}")
def at(d): return px.index.get_indexer([pd.Timestamp(d)],method="nearest")[0]
sig=np.sqrt(sig2)
# --- age rule
A=17.4; chk("age rule beta/A",100*5.62/A,32,0.5); chk("age rule 5-yr form",100*((1+5/A)**(5.62/5)-1),33,0.5)
# --- trailing vol at survey dates and today
s21=sig.iloc[at("2021-09-30")]; s25=sig["2025-04":"2025-06"].mean(); snow=sig.iloc[-1]
print(f"INFO  trailing vol 2021Q3 {s21:.2f}, mid-2025 {s25:.2f}, May 2026 {snow:.2f}")
# --- Table 3 implied gamma with the note's inputs
g21=(0.22-0.035-0.003)/(0.77**2*0.19); g25=(0.138-0.072-0.003)/(0.53**2*0.19)
chk("Table 3 implied gamma 2021 (sigma .77,w .19,rf+b 3.5)",g21,1.6,0.05)
chk("Table 3 implied gamma 2025Q2 (sigma .53,w .19,rf+b 7.2)",g25,1.2,0.05)
chk("Table 3 gamma 2021 with 24m vol",(0.22-0.035-0.003)/(0.73**2*0.19),1.8,0.05); chk("Table 3 gamma 2025 with 24m vol",(0.138-0.072-0.003)/(0.48**2*0.19),1.4,0.05)
chk("trailing vol at 2021Q3",s21,0.77,0.01); chk("trailing vol at 2025Q2",s25,0.53,0.015)
chk("2025 gamma at beta .33",(0.138-0.044-0.0132-0.003)/(0.53**2*0.19),1.4,0.06); chk("2025 gamma at beta 1.05",(0.138-0.044-0.042-0.003)/(0.53**2*0.19),0.9,0.06)
# --- Section 2 worked example
we=1.5+2*0.64*0.19*100+2+0.3; chk("worked example 2021 required",we,28,0.6)
gwe=(0.22-0.015-0.02-0.003)/(0.64*0.19); chk("worked example gamma for 22%",gwe,1.5,0.06)
chk("6.7 points (gamma 2, sigma .42, w .19)",2*0.42**2*0.19*100,6.7,0.15); chk("1.8 points at w=.05",2*0.42**2*0.05*100,1.8,0.1)
# --- Section 5 envelope and Monte Carlo
lo=5+1.32+1.7*0.42**2*0.08*100+0.3; hi=5+4.2+2.8*0.42**2*0.19*100+3
chk("envelope low (analytic)",lo,9.0,0.3); chk("envelope high (analytic)",hi,21.6,0.3)
rng=np.random.default_rng(1); N=400000
beta=rng.uniform(0.33,1.05,N)*0.04; gam=rng.uniform(1.7,2.8,N); w=rng.uniform(0.08,0.19,N); mort=rng.uniform(0.003,0.03,N)
r=0.05+beta+gam*0.42**2*w+mort; q=np.percentile(r,[5,16,50,84,95])*100
gam_h=rng.uniform(1.2,1.8,N); rh=0.05+beta+gam_h*0.42**2*w+mort; qh=np.percentile(rh,[5,50,95])*100
chk("MC holders median",qh[1],13.0,0.2); chk("MC holders 90% lo",qh[0],10.6,0.2); chk("MC holders 90% hi",qh[2],15.5,0.2)
reth=0.05+beta+gam_h*0.64**2*w+mort; chk("MC Ether holders median",np.percentile(reth,50)*100,17.6,0.3)
chk("MC median",q[2],14.7,0.15); chk("MC 68% lo",q[1],12.9,0.15); chk("MC 68% hi",q[3],16.7,0.15); chk("MC 90% lo",q[0],11.8,0.15); chk("MC 90% hi",q[4],18.0,0.15)
chk("width from w",2.25*0.42**2*(0.19-0.08)*100,4,0.5); chk("width from beta",(1.05-0.33)*4,3,0.5); chk("width from mort",2.7,3,0.5); chk("width from gamma",(2.8-1.7)*0.42**2*0.135*100,3,0.5)
# --- Section 7 units
chk("vol drag sigma^2/2 at .42-.45",100*(0.42**2+0.45**2)/4,9,0.6); chk("CAGR counterpart",15-9,6,0.5); chk("diffusive noise sigma/sqrt5",100*0.42/np.sqrt(5),19,0.5)
# --- Section 6 band at Table 4 dates (paper values)
tab={"2013-06-30":(17,231),"2015-06-30":(12,135),"2017-06-30":(22,67),"2019-06-30":(37,82),"2021-06-30":(21,58),"2023-06-30":(12,24)}
for d,(l,h) in tab.items():
    i=at(d); chk(f"Table 4 band low {d[:4]}",100*foc_lo.iloc[i],l,0.6); chk(f"Table 4 band high {d[:4]}",100*req_hi.iloc[i],h,0.6)
    chk(f"Table 4 vol {d[:4]}",100*sig.iloc[i],{"2013":151,"2015":115,"2017":80,"2019":90,"2021":83,"2023":66}[d[:4]],1.0)
i=at("2026-05-31"); chk("2026 monthly band low",100*foc_lo.iloc[i],9,0.6); chk("2026 monthly band high",100*req_hi.iloc[i],23,0.6); chk("2026 vol",100*sig.iloc[i],42,1.0)
# realized
f5=lambda d: 100*((px.iloc[-1]/px.iloc[at(d)])**(1/((px.index[-1]-pd.Timestamp(d)).days/365.25))-1)
chk("BTC CAGR 2021Q3 to May 2026",f5("2021-09-30"),12.8,0.2)
for d,v in {"2013-06-30":135,"2015-06-30":103,"2017-06-30":51,"2019-06-30":42}.items():
    chk(f"Table 4 realized next-5y {d[:4]}",100*fwd5.iloc[at(d)],v,1.0)
# Figure 6 shares
beta_t=0.5*(0.0132+0.042); mort_t=0.5*(0.003+0.03)
def shares(d):
    i=at(d); tot=req_mid.iloc[i]; conc=max(tot-rf.iloc[i]-beta_t-mort_t,0); return 100*tot,100*np.array([rf.iloc[i],beta_t,conc,mort_t])/tot
t13,s13=shares("2013-06-30"); chk("Fig6 2013 total",t13,125,3); chk("Fig6 2013 conc share",s13[2],95,1.5)
t21,s21_=shares("2021-09-30"); chk("Fig6 2021 conc share (four-fifths)",s21_[2],80,3)
t26,s26=shares("2026-04-30"); chk("Fig6 2026 total",t26,16,0.6)
for k,v,lab in [(0,30,"rf"),(1,17,"beta"),(2,43,"conc"),(3,10,"mort")]: chk(f"Fig6 2026 share {lab}",s26[k],v,1.5)
# --- Section 9
chk("hurdle low rf+beta",5+1.32,6,0.5); chk("hurdle high",5+4.2,9,0.5)
chk("sizing w* gamma3 mu15",100*(15-5-2.7-0.3)/(3*0.42**2*100),13,0.6); chk("sizing age rule",100*(32-5-2.7-0.3)/(3*0.42**2*100),45,1.0)
chk("Sharpe equities 4/18",4/18,0.22,0.01); chk("Sharpe BTC",(15-5)/42,0.24,0.01); chk("Sharpe BTC ex mortality (1.65)",(15-5-1.65)/42,0.20,0.01)
chk("Sharpe units: rho SR",0.2*0.25,0.05,0.005); chk("Sharpe units: conc",2.25*0.42*0.135,0.13,0.01); chk("Sharpe units: mort",1.65/42,0.04,0.005)
chk("Sharpe units 2013 midpoint",(t13-100*rf.iloc[at('2013-06-30')])/(100*sig.iloc[at('2013-06-30')]),0.8,0.05)
chk("historical premium: equities",8/18,0.45,0.02); chk("historical premium: BTC required mid",15+0.69*4,17.8,1.5); chk("historical premium: BTC Sharpe",(18-5)/42,0.30,0.02)
# --- Ether
e=pd.read_csv("/tmp/cmdata/csv/eth.csv",parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna()
chk("ETH CAGR 2021Q3 to May 2026",100*((e.iloc[-1]/e[:"2021-09-30"].iloc[-1])**(1/((e.index[-1]-pd.Timestamp("2021-09-30")).days/365.25))-1),-7,0.5)
chk("ETH variance ratio (.64/.42)^2",(0.64/0.42)**2,2.3,0.05)
# --- Appendix D
Wp_r=cap.iloc[i21]/0.19*(qpart/qpart.iloc[i21])*interp({2012:0.25,2021:1.0,2026:1.4})
chk("D: participating wealth 2021Q3 $T",cap.iloc[i21]/0.19/1e12,4.3,0.2); chk("D: survey-holder wealth 2026 $T",Wp_r.iloc[-1]/1e12,7,0.3)
chk("D: w 2013",100*(cap.reindex(px.index)/Wp_r).iloc[at("2013-06-30")],3,0.6); chk("D: w 2017",100*(cap.reindex(px.index)/Wp_r).iloc[at("2017-06-30")],17,0.8)
chk("D: w 2021",100*(cap.reindex(px.index)/Wp_r).iloc[at("2021-06-30")],18,0.8); chk("D: w 2026 survey holders",100*(cap.reindex(px.index)/Wp_r).iloc[-1],21,0.8)
chk("D: w 2026 diluted",100*w_lo.iloc[-1],8,0.6); chk("D: inst value $B",2.5e6*px.iloc[-1]/1e9,190,8); chk("D: inst wealth at 1.5% $T",2.5e6*px.iloc[-1]/0.015/1e12,13,0.5); chk("D: inst wealth at 3% $T",2.5e6*px.iloc[-1]/0.03/1e12,6,0.5)
chk("D: address path 2018",100*q_addr.iloc[at("2018-06-30")],6.4,0.2)
chk("D: survey path 2018",100*qpart.iloc[at("2018-06-30")],1.2,0.05)
n_fail=sum(1 for ok,*_ in res if not ok); print(f"\n{len(res)-n_fail} PASS, {n_fail} FAIL")
