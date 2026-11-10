"""Model-side audit: recompute the quantitative claims of Sections 1-2, 5-9 and Appendices A, B, D, E
from the data and the shared band construction, and compare with the manuscript's numbers."""
import numpy as np, pandas as pd, importlib.util, sys
src=open("/home/claude/model/22_pretty_figs.py").read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
res=[]
def chk(label,val,claim,tol):
    ok=abs(val-claim)<=tol; res.append(ok); print(f"{'PASS' if ok else 'FAIL':5s} {label}: computed {val:.3g} vs paper {claim}")
def at(d): return px.index.get_indexer([pd.Timestamp(d)],method="nearest")[0]
sig=np.sqrt(sig2); qpart=q.copy()
# age rule
chk("age rule 5-yr form, Sept 2026 (A=17.7)",100*((1+5/17.7)**(5.62/5)-1),32,0.5); chk("age Sept 2026",(pd.Timestamp("2026-09-15")-pd.Timestamp("2009-01-03")).days/365.25,17.7,0.05); chk("age rule beta/A",100*5.62/17.4,32,0.5); chk("age rule 5-yr form",100*((1+5/17.4)**(5.62/5)-1),33,0.5)
# Appendix A betas
def B(x): return np.cov(x.b,x.s)[0,1]/x.s.var()
chk("beta last 4y",B(_d.iloc[-48:]),1.75,0.03); chk("beta since 2016",B(_d["2016":]),1.5,0.03); chk("beta since 2012",B(_d["2012":]),1.8,0.04)
chk("corr last 4y",_d.iloc[-48:].corr().iloc[0,1],0.50,0.02); chk("corr since 2016",_d["2016":].corr().iloc[0,1],0.32,0.02); chk("corr since 2012",_d["2012":].corr().iloc[0,1],0.29,0.02)
chk("rolling beta 2019",beta_roll.iloc[at("2019-06-30")],0.7,0.05); chk("rolling beta 2021Q3",beta_roll.iloc[at("2021-09-30")],1.3,0.05); chk("rolling beta 2025Q2",beta_roll["2025-04":"2025-06"].mean(),2.0,0.08)
chk("rolling beta min since mid-2022",beta_roll["2022-06":].min(),1.6,0.06); chk("rolling beta max since mid-2022",beta_roll["2022-06":].max(),2.2,0.06)
chk("CAPM low",5+1.5*4,11,0.1); chk("CAPM high",5+1.8*6,16,0.3)
chk("gamma*sigma_m^2 low",170*0.16**2,4.4,0.1); chk("gamma*sigma_m^2 high",280*0.16**2,7.2,0.1)
# Section 2 worked example
chk("worked example 2021",1.5+1.3*4+2*0.64*0.19*100+0.3,31,0.6); chk("worked example gamma",(0.22-0.015-0.052-0.003)/(0.64*0.19),1.3,0.07)
chk("6.7 points",2*0.42**2*0.19*100,6.7,0.15)
# Table 3
s21=sig.iloc[at("2021-09-30")]; s25=sig["2025-04":"2025-06"].mean(); chk("vol 2021Q3",s21,0.77,0.01); chk("vol 2025Q2",s25,0.53,0.015)
chk("T3 2021 req low",100*(0.015+0.052+1.7*0.77**2*0.19+0.003),26,0.6); chk("T3 2021 req high",100*(0.015+0.052+2.8*0.77**2*0.19+0.003),38,0.7)
chk("T3 2025 req low",100*(0.044+0.078+1.7*0.53**2*0.19+0.003),22,0.6); chk("T3 2025 req high",100*(0.044+0.078+2.8*0.53**2*0.19+0.003),27,0.7)
chk("T3 gamma 2021",(0.22-0.015-0.052-0.003)/(0.77**2*0.19),1.3,0.06); chk("T3 gamma 2025",(0.138-0.044-0.078-0.003)/(0.53**2*0.19),0.2,0.06)
# Section 5 Monte Carlo (same script the paper cites)
spec=importlib.util.spec_from_file_location("u","/home/claude/model/23_uncertainty.py"); u=importlib.util.module_from_spec(spec); spec.loader.exec_module(u)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    qb=u.run("b",0.42,1.5,2.0,0.08,0.19,0.003,0.03)*100; qe=u.run("e",0.64,2.0,2.7,0.08,0.19,0.003,0.03)*100; ql=u.run("l",0.80,2.0,2.7,0.10,0.30,0.01,0.03)*100
    qs=u.run("s",(1.0,1.3),2.0,2.7,0.10,0.30,0.157,0.174)*100; qg=u.run("g",(0.13,0.20),-0.1,0.1,0.02,0.10,0.0,0.003)*100; qd=u.run("d",0.15,1.5,2.0,0.02,0.10,0.003,0.03)*100
chk("MC median",qb[2],18.9,0.2); chk("MC 68 lo",qb[1],17.2,0.2); chk("MC 68 hi",qb[3],20.9,0.2); chk("MC 90 lo",qb[0],16.2,0.2); chk("MC 90 hi",qb[4],22.1,0.2)
chk("envelope lo",5+6+1.7*0.42**2*8+0.3,13.7,0.1); chk("envelope hi",5+8+2.8*0.42**2*19+3,25.4,0.1)
chk("Ether median",qe[2],28,0.6); chk("Ether 90 lo",qe[0],23,0.6); chk("Ether 90 hi",qe[4],35,0.6)
chk("Large alt median",ql[2],45,0.8); chk("Large alt 90 lo",ql[0],31,0.8); chk("Large alt 90 hi",ql[4],62,0.8)
chk("Small median",qs[2],88,1.5); chk("Small 90 lo",qs[0],60,1.5); chk("Small 90 hi",qs[4],131,2)
chk("Gold median",qg[2],5.5,0.1); chk("Digital gold median",qd[2],14.0,0.2); chk("Digital gold 90 lo",qd[0],12.3,0.2); chk("Digital gold 90 hi",qd[4],15.6,0.2)
chk("vol drag",100*(0.42**2+0.45**2)/4,9,0.6); chk("CAGR counterpart",18.9-9.2,10,0.5); chk("diffusive noise",100*0.42/np.sqrt(5),19,0.5)
# Section 6 table
T={"2013-06-30":(151,3.0,26,231,128,144,135,132),"2015-06-30":(115,2.9,21,135,78,99,103,90),"2017-06-30":(80,2.2,28,67,47,76,51,68),"2019-06-30":(90,0.7,38,82,60,58,42,55)}
for d,(v,b,lo,hi,mid,dr,cg,ar) in T.items():
    i=at(d); y=d[:4]
    chk(f"T4 {y} vol",100*sig.iloc[i],v,1); chk(f"T4 {y} beta",beta_roll.iloc[i],b,0.06); chk(f"T4 {y} band lo",100*foc_lo.iloc[i],lo,0.7); chk(f"T4 {y} band hi",100*req_hi.iloc[i],hi,0.7)
    chk(f"T4 {y} mid",100*req_mid.iloc[i],mid,0.7); chk(f"T4 {y} realized drift",100*fwd_mu.iloc[i],dr,1); chk(f"T4 {y} CAGR",100*fwd5.iloc[i],cg,1); chk(f"T4 {y} age rule",100*age_rule.iloc[i],ar,1)
i=at("2021-09-30"); chk("T4 2021Q3 band lo",100*foc_lo.iloc[i],23,0.7); chk("T4 2021Q3 band hi",100*req_hi.iloc[i],47,0.7); chk("T4 2021Q3 mid",100*req_mid.iloc[i],35,0.7); chk("T4 2021Q3 age rule",100*age_rule.iloc[i],45,1)
l=np.log(px).diff()["2021-10":]; g=12*l.mean(); v=12*l.var(); chk("2021Q3-> drift",100*(g+v/2),27,0.6); chk("2021Q3-> CAGR",100*(np.exp(g)-1),13,0.5)
i=at("2023-06-30"); chk("T4 2023 band lo",100*foc_lo.iloc[i],18,0.7); chk("T4 2023 band hi",100*req_hi.iloc[i],29,0.7); chk("T4 2023 mid",100*req_mid.iloc[i],23,0.7)
i=at("2026-05-31"); chk("T4 2026 band lo",100*foc_lo.iloc[i],14,0.7); chk("T4 2026 band hi",100*req_hi.iloc[i],27,0.7); chk("T4 2026 mid",100*req_mid.iloc[i],20,0.7); chk("2026 vol",100*sig.iloc[i],42,1)
mm=(age>=3.0)&fwd_mu.notna()
chk("windows",mm.sum(),113,0); chk("gap vs mid",100*(fwd_mu-req_mid)[mm].mean(),5,0.6); chk("gap vs lower",100*(fwd_mu-foc_lo)[mm].mean(),60,1); chk("gap vs upper",100*(fwd_mu-req_hi)[mm].mean(),-49,1); chk("median gap vs mid",100*(fwd_mu-req_mid)[mm].median(),21,1)
chk("inside band share",100*((fwd_mu>=foc_lo)&(fwd_mu<=req_hi))[mm].mean(),48,1); chk("MAE mid",100*np.abs(fwd_mu-req_mid)[mm].mean(),51,1); chk("MAE age rule",100*np.abs(fwd_mu-age_rule)[mm].mean(),21,1)
# monthly test (Table: monthly; Figure 6; D.3)
_r=px.shift(-1)/px-1; _mo=lambda mu: np.exp(mu/12)-1
_D=pd.DataFrame({"r":_r,"lo":_mo(foc_lo),"mid":_mo(req_mid),"hi":_mo(req_hi),"age":((age+1/12)/age)**5.62-1}).dropna(); _D=_D[_D.index>="2012-01-01"]
def _nw(e,Lg=6):
    e=np.asarray(e)-np.mean(e); n=len(e); v=(e**2).sum()/n
    for l in range(1,Lg+1): v+=2*(1-l/(Lg+1))*(e[l:]*e[:-l]).sum()/n
    return np.sqrt(v/n)
_TAB={"all":("2012","2026",172,118,30,116,72,88,47,39,2,48),"2012-14":("2012","2014",36,278,47,298,167,231,111,170,-21,143),
 "2015-17":("2015","2017",36,160,29,105,67,130,93,46,55,82),"2018-20":("2018","2020",36,69,34,81,57,35,12,48,-12,15),
 "2021-23":("2021","2023",36,30,21,42,32,9,-2,39,-12,-12),"2024-26":("2024","2026",28,36,17,37,27,20,10,33,0,1),
 "2012-17":("2012","2017",72,219,38,202,117,180,102,87,17,112),"2018-26":("2018","2026",100,46,25,55,40,21,6,24,-9,1)}
_dt=0
for _k,(_a,_b,_n,_re,_lo,_hi,_mi,_gl,_gm,_sm,_gh,_ga) in _TAB.items():
    _s=_D[_a:_b]; _e=_s.r-_s.mid; _se=1200*_e.std(ddof=1)/np.sqrt(len(_e))
    chk(f"monthly {_k}: n",len(_s),_n,0); chk(f"monthly {_k}: delivered",1200*_s.r.mean(),_re,0.6); chk(f"monthly {_k}: band lo",1200*_s.lo.mean(),_lo,0.6); chk(f"monthly {_k}: band hi",1200*_s.hi.mean(),_hi,0.6)
    chk(f"monthly {_k}: mid",1200*_s.mid.mean(),_mi,0.6); chk(f"monthly {_k}: gap lo",1200*(_s.r-_s.lo).mean(),_gl,0.6); chk(f"monthly {_k}: gap mid",1200*_e.mean(),_gm,0.6); chk(f"monthly {_k}: se mid",_se,_sm,0.6)
    chk(f"monthly {_k}: gap hi",1200*(_s.r-_s.hi).mean(),_gh,0.6); chk(f"monthly {_k}: gap age",1200*(_s.r-_s.age).mean(),_ga,0.6)
    for _c in ["lo","mid","hi","age"]:
        _x=(_s.r-_s[_c]); _dt=max(_dt,abs(_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x)))-_x.mean()/_nw(_x)))
chk("monthly: max |t - HAC t| in table",_dt,0.15,0.15)
_x=_D.r-_D.lo; chk("monthly: t lower edge",_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x))),2.2,0.06)
_x=_D["2015":"2017"]; _x=_x.r-_x.mid; chk("monthly: t mid 2015-17",_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x))),2.0,0.06)
chk("monthly: delivered s.e. all",1200*_D.r.std(ddof=1)/np.sqrt(len(_D)),39,1)
chk("monthly: largest month %",100*_D.r.max(),451,1); chk("monthly: largest month is Nov 2013",float(_D.r.idxmax()==pd.Timestamp("2013-10-31")),1,0); chk("monthly: its contribution",1200*_D.r.max()/len(_D),31,0.6)
_x=_D[_D.index.year!=2013]; chk("ex-2013 delivered",1200*_x.r.mean(),69,0.6); chk("ex-2013 mid",1200*_x.mid.mean(),65,0.6); chk("ex-2013 gap mid",1200*(_x.r-_x.mid).mean(),4,0.6); chk("ex-2013 se mid",1200*(_x.r-_x.mid).std(ddof=1)/np.sqrt(len(_x)),21,0.6)
chk("ex-2013 gap lo",1200*(_x.r-_x.lo).mean(),41,0.6); chk("ex-2013 gap hi",1200*(_x.r-_x.hi).mean(),-35,0.6); _y=_x.r-_x.lo; chk("ex-2013 t lo",_y.mean()/(_y.std(ddof=1)/np.sqrt(len(_y))),2.0,0.06)
chk("monthly corr with mid",np.corrcoef(_D.r,_D.mid)[0,1],-0.02,0.01); chk("monthly corr with age rule",np.corrcoef(_D.r,_D.age)[0,1],0.17,0.01)
_x=_D[:"2021-05"]; chk("monthly gap mid over the 5y-window months",1200*(_x.r-_x.mid).mean(),69,0.6); chk("n those months",len(_x),113,0)
chk("band width 2012-14",298-47,250,2); chk("band width 2024-26",37-17,20,0.5)
_pv=np.sqrt((0.95*0.165)**2+(0.05*0.42)**2+2*0.95*0.05*0.5*0.165*0.42)
chk("rebalanced 5%: added return",0.05*(19-9),0.5,0.01); chk("rebalanced 5%: portfolio vol",100*_pv,16.8,0.06); chk("rebalanced 5%: extra drag",100*(_pv**2-0.165**2)/2,0.05,0.01)
chk("equity compound",9-100*0.165**2/2,8,0.5); chk("BTC compound",19-100*0.42**2/2,10,0.3); chk("vol ratio",42/16.5,2.5,0.06)
chk("drift example: +100%,-50% average",(100-50)/2,25,0)
chk("age rule closer share",100*(np.abs(fwd_mu-age_rule)<np.abs(fwd_mu-req_mid))[mm].mean(),91,1); chk("corr realized, mid",np.corrcoef(fwd_mu[mm],req_mid[mm])[0,1],0.14,0.02); chk("corr realized, age rule",np.corrcoef(fwd_mu[mm],age_rule[mm])[0,1],0.83,0.02)
# Figure 6 shares
mort_t=0.5*(0.003+0.03)
def shares(d):
    i=at(d); tot=req_mid.iloc[i]; conc=max(tot-rf.iloc[i]-beta_term.iloc[i]-mort_t,0); return 100*tot,100*np.array([rf.iloc[i],beta_term.iloc[i],conc,mort_t])/tot
t13,s13=shares("2013-06-30"); chk("Fig6 2013 total",t13,128,1); chk("Fig6 2013 conc share",s13[2],88,1.5)
t21,s21_=shares("2021-09-30"); chk("Fig6 2021 conc share",s21_[2],75,3)
t26,s26=shares("2026-04-30"); chk("Fig6 2026 total",t26,21,0.7)
for k,vv,lab in [(0,24,"rf"),(1,35,"market"),(2,33,"conc"),(3,8,"mort")]: chk(f"Fig6 2026 share {lab}",s26[k],vv,1.5)
# Section 8/9
e=pd.read_csv("/tmp/cmdata/csv/eth.csv",parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna().resample("ME").last()
le=np.log(e).diff()["2021-10":]; chk("ETH drift 2021Q3->",100*(12*le.mean()+6*le.var()),19,1); chk("ETH CAGR 2021Q3->",100*(np.exp(12*le.mean())-1),-7,0.6)
de=pd.DataFrame({"b":np.log(e).diff(),"s":_d.s}).dropna(); chk("ETH beta 4y",B(de.iloc[-48:]),2.7,0.05); chk("ETH beta since 2016",B(de["2016":]),2.0,0.05)
chk("altcoin drift from -7% CAGR at 80% vol",-7+32,25,1)
chk("hurdle lo",5+6,11,0.1); chk("hurdle hi",5+8,13,0.1); chk("sizing",100*(19-5-7-0.3)/(3*0.42**2*100),12,0.8); chk("sizing age rule",100*(32-5-7-0.3)/(3*0.42**2*100),36,1.5)
chk("Sharpe BTC",(19-5)/42,0.33,0.01); chk("Sharpe BTC ex mort",(19-5-1.65)/42,0.29,0.01); chk("Sharpe market term",7/42,0.15,0.02); chk("Sharpe conc",2.25*0.42*0.135,0.13,0.01); chk("Sharpe mort",1.65/42,0.04,0.005)
chk("Sharpe units 2013",(t13-100*rf.iloc[at('2013-06-30')])/(100*sig.iloc[at('2013-06-30')]),0.8,0.05); chk("hist premium BTC required",19+7,26,0.5); chk("hist premium BTC Sharpe",(26-5)/42,0.50,0.01); chk("diluted Sharpe",0.15+0.04,0.19,0.01)
# Appendix B
Wp_r=cap.iloc[i21]/0.19*(qpart/qpart.iloc[i21])*interp({2012:0.25,2021:1.0,2026:1.4}); wr=cap.reindex(px.index)/Wp_r
chk("B: wealth 2021Q3 $T",cap.iloc[i21]/0.19/1e12,4.3,0.2); chk("B: survey-holder wealth 2026 $T",Wp_r.iloc[-1]/1e12,7,0.3); chk("B: w 2013",100*wr.iloc[at("2013-06-30")],3,0.6); chk("B: w 2017",100*wr.iloc[at("2017-06-30")],17,0.8)
chk("B: w 2021",100*wr.iloc[at("2021-06-30")],18,0.8); chk("B: w 2026",100*wr.iloc[-1],21,0.8); chk("B: w 2026 diluted",100*w_lo.iloc[-1],8,0.6); chk("B: inst value $B",2.5e6*px.iloc[-1]/1e9,190,8)
chk("B: address path 2018",100*q_addr.iloc[at("2018-06-30")],6.4,0.2); chk("B: survey path 2018",100*qpart.iloc[at("2018-06-30")],1.2,0.05)
print(f"\n{sum(res)} PASS, {len(res)-sum(res)} FAIL")
