"""Model-side audit: recompute the quantitative claims of Sections 1 to 8 and Appendices A to E
from the data and the shared band construction, and compare with the manuscript's numbers."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, importlib.util, sys
src=open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])
res=[]; records=[]     # records: every check, for outputs/results.json
def chk(label,val,claim,tol):
    records.append({"claim":label,"computed":float(val),"paper":claim,"tolerance":tol})
    ok=abs(val-claim)<=tol; res.append(ok); print(f"{'PASS' if ok else 'FAIL':5s} {label}: computed {val:.3g} vs paper {claim}")
def at(d): return px.index.get_indexer([pd.Timestamp(d)],method="nearest")[0]
sig=np.sqrt(sig2); qpart=q.copy()
# age rule
chk("age rule beta/A",100*5.62/17.4,32,0.5); chk("age rule 5-yr form",100*((1+5/17.4)**(5.62/5)-1),33,0.5)
# Appendix A betas
def B(x): return np.cov(x.b,x.s)[0,1]/x.s.var()
chk("beta last 4y",B(_d.iloc[-48:]),1.75,0.03); chk("beta since 2016",B(_d["2016":]),1.5,0.03); chk("beta since 2012",B(_d["2012":]),1.8,0.04)
chk("rolling corr median 2014-19",corr_roll["2014":"2019"].median(),0.2,0.03); chk("rolling corr mean since 2022",corr_roll["2022":].mean(),0.5,0.03); chk("corr last 4y",_d.iloc[-48:].corr().iloc[0,1],0.50,0.02); chk("corr since 2016",_d["2016":].corr().iloc[0,1],0.32,0.02); chk("corr since 2012",_d["2012":].corr().iloc[0,1],0.29,0.02)
chk("rolling beta 2019",beta_roll.iloc[at("2019-06-30")],0.7,0.05); chk("rolling beta 2021Q3",beta_roll.iloc[at("2021-09-30")],1.3,0.05); chk("T2 beta, May 2025",beta_roll.iloc[at("2025-05-31")],1.98,0.005)
chk("rolling beta min since mid-2022",beta_roll["2022-06":].min(),1.6,0.06); chk("rolling beta max since mid-2022",beta_roll["2022-06":].max(),2.2,0.06)
chk("CAPM low",5+1.5*4,11,0.1); chk("CAPM high",5+1.8*6,16,0.3)
chk("gamma*sigma_m^2 low",100*0.16**2,2.6,0.1); chk("gamma*sigma_m^2 high",280*0.16**2,7.2,0.1)
# Section 2 worked example
chk("worked example 2021",1.5+1.3*4+2*0.64*0.19*100+0.3,31,0.6); chk("worked example gamma",(0.22-0.015-0.052-0.003)/(0.64*0.19),1.3,0.07)
chk("6.7 points",2*0.42**2*0.19*100,6.7,0.15)
# Table 3
s21=sig.iloc[at("2021-09-30")]; s25=sig.iloc[at("2025-05-31")]; chk("vol 2021Q3",s21,0.77,0.01); chk("T2 volatility, May 2025",s25,0.53,0.005); chk("T2 risk-free rate, May 2025",100*rf.iloc[at("2025-05-31")],4.4,0.05); chk("T2 risk-free rate, September 2021",100*rf.iloc[at("2021-09-30")],1.5,0.05); chk("T2 market term 2025",1.98*4,7.9,0.05); chk("T2 risk-free plus market term 2025",4.4+7.9,12.3,0.001)
chk("T3 2021 req low",100*(0.015+0.052+1.0*0.77**2*0.19+0.003),18,0.6); chk("T3 2021 req high",100*(0.015+0.052+2.8*0.77**2*0.19+0.003),39,0.5)
chk("T3 2025 req low",100*(0.044+0.079+1.0*0.53**2*0.19+0.003),18,0.5); chk("T3 2025 req high",100*(rf.iloc[at("2025-05-31")]+beta_roll.iloc[at("2025-05-31")]*0.04+2.8*sig2.iloc[at("2025-05-31")]*0.19+0.003),27,0.5)
chk("T3 gamma 2021",(0.22-0.015-0.052-0.003)/(0.77**2*0.19),1.3,0.06); chk("T3 gamma 2025",(0.138-0.044-0.079-0.003)/(0.53**2*0.19),0.2,0.05)
# Section 5 Monte Carlo (same script the paper cites)
spec=importlib.util.spec_from_file_location("u",os.path.join(SCRIPTS,"23_uncertainty.py")); u=importlib.util.module_from_spec(spec); spec.loader.exec_module(u)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    qb=u.run("b",0.42,1.5,2.0,0.07,0.19,0.003,0.035)*100; qe=u.run("e",0.64,2.0,2.7,0.07,0.19,0.003,0.035)*100; ql=u.run("l",0.80,2.0,2.7,0.10,0.30,0.01,0.03)*100
    qs=u.run("s",(1.0,1.3),2.0,2.7,0.10,0.30,0.067,0.162)*100; qg=u.run("g",(0.13,0.20),-0.1,0.1,0.02,0.10,0.0,0.003)*100; qd=u.run("d",0.15,1.5,2.0,0.02,0.10,0.003,0.035)*100
chk("MC median",qb[2],18.1,0.05); chk("MC 68 lo",qb[1],16.2,0.05); chk("MC 68 hi",qb[3],20.3,0.05); chk("MC 90 lo",qb[0],15.2,0.05); chk("MC 90 hi",qb[4],21.8,0.05)
chk("envelope lo",5+6+1.0*0.42**2*7+0.3,13,0.5); chk("envelope hi",5+8+2.8*0.42**2*19+3.5,26,0.5)
chk("Gold median",qg[2],5.5,0.1); chk("Digital gold: beta at 15% volatility and correlation 0.5",0.5*15/14.1,0.5,0.04); chk("Digital gold: required return",5+0.5*15/14.1*4+1.9,9,0.1); chk("Digital gold lo",5+0.5*15/14.1*4+0.3,7,0.5); chk("Digital gold hi",5+0.5*15/14.1*4+3.5,11,0.5)
chk("vol drag",100*(0.42**2+0.45**2)/4,9,0.6); chk("CAGR counterpart",18.0-9.2,9,0.5); chk("diffusive noise",100*0.42/np.sqrt(5),19,0.5)
# Section 5 table
T={"2013-06-30":(151,3.0,56,231,144,174,135,132),"2015-06-30":(115,2.9,35,135,85,103,103,90),"2017-06-30":(80,2.2,21,67,44,78,51,68),"2019-06-30":(90,0.7,18,51,35,58,42,55)}
for d,(v,b,lo,hi,mid,dr,cg,ar) in T.items():
    i=at(d); y=d[:4]
    chk(f"T4 {y} vol",100*sig.iloc[i],v,1); chk(f"T4 {y} beta",beta_roll.iloc[i],b,0.06); chk(f"T4 {y} band lo",100*foc_lo.iloc[i],lo,0.7); chk(f"T4 {y} band hi",100*req_hi.iloc[i],hi,0.7)
    chk(f"T4 {y} mid",100*req_mid.iloc[i],mid,0.7); chk(f"T4 {y} realized drift",100*fwd_mu.iloc[i],dr,1); chk(f"T4 {y} CAGR",100*fwd5.iloc[i],cg,1); chk(f"T4 {y} age rule",100*age_rule.iloc[i],ar,1)
i=at("2021-09-30"); chk("T4 2021Q3 band lo",100*foc_lo.iloc[i],14,0.7); chk("T4 2021Q3 band hi",100*req_hi.iloc[i],43,0.7); chk("T4 2021Q3 mid",100*req_mid.iloc[i],28,0.7); chk("T4 2021Q3 age rule",100*age_rule.iloc[i],45,1)
l=np.log(px).diff()["2021-10":]; g=12*l.mean(); v=12*l.var(); chk("2021Q3-> drift",100*(g+v/2),27,0.6); chk("2021Q3-> CAGR",100*(np.exp(g)-1),13,0.5)
i=at("2023-06-30"); chk("T4 2023 band lo",100*foc_lo.iloc[i],16,0.7); chk("T4 2023 band hi",100*req_hi.iloc[i],40,0.7); chk("T4 2023 mid",100*req_mid.iloc[i],28,0.7)
i=at("2026-05-31"); chk("T4 2026 band lo",100*foc_lo.iloc[i],12,0.7); chk("T4 2026 band hi",100*req_hi.iloc[i],25,0.7); chk("T4 2026 mid",100*req_mid.iloc[i],19,0.7); chk("2026 vol",100*sig.iloc[i],42,1)
mm=(age>=3.0)&fwd_mu.notna()
chk("windows",mm.sum(),113,0); 
chk("MAE mid",100*np.abs(fwd_mu-req_mid)[mm].mean(),51,0.5); chk("MAE age rule",100*np.abs(fwd_mu-age_rule)[mm].mean(),27,0.5)
# monthly test (Table 5; Figure 3; Appendix D.2)
_r=px.shift(-1)/px-1; _mo=lambda mu: np.exp(mu/12)-1
_D=pd.DataFrame({"r":_r,"lo":_mo(foc_lo),"mid":_mo(req_mid),"hi":_mo(req_hi),"age":((age+1/12)/age)**5.62-1}).dropna(); _D=_D[_D.index>="2012-01-01"]
def _nw(e,Lg=6):
    e=np.asarray(e)-np.mean(e); n=len(e); v=(e**2).sum()/n
    for l in range(1,Lg+1): v+=2*(1-l/(Lg+1))*(e[l:]*e[:-l]).sum()/n
    return np.sqrt(v/n)
_TAB={"all":("2012","2026",172,118,27,109,67,91,51,39,9,48),
 "2012-14":("2012","2014",36,278,60,298,174,218,104,169,-21,143),
 "2015-17":("2015","2017",36,160,27,98,62,132,98,46,62,82),
 "2018-20":("2018","2020",36,69,17,57,37,52,32,47,12,15),
 "2021-23":("2021","2023",36,30,15,44,29,15,1,38,-14,-12),
 "2024-26":("2024","2026",28,36,14,33,23,22,13,33,4,1),
 "2012-17":("2012","2017",72,219,44,198,118,175,101,87,21,112),
 "2018-26":("2018","2026",100,46,16,45,30,30,15,23,1,1)}
_dt=0
for _k,(_a,_b,_n,_re,_lo,_hi,_mi,_gl,_gm,_sm,_gh,_ga) in _TAB.items():
    _s=_D[_a:_b]; _e=_s.r-_s.mid; _se=1200*_e.std(ddof=1)/np.sqrt(len(_e))
    chk(f"monthly {_k}: n",len(_s),_n,0); chk(f"monthly {_k}: delivered",1200*_s.r.mean(),_re,0.6); chk(f"monthly {_k}: band lo",1200*_s.lo.mean(),_lo,0.6); chk(f"monthly {_k}: band hi",1200*_s.hi.mean(),_hi,0.6)
    chk(f"monthly {_k}: mid",1200*_s.mid.mean(),_mi,0.6); chk(f"monthly {_k}: gap lo",1200*(_s.r-_s.lo).mean(),_gl,0.6); chk(f"monthly {_k}: gap mid",1200*_e.mean(),_gm,0.6); chk(f"monthly {_k}: se mid",_se,_sm,0.6)
    chk(f"monthly {_k}: gap hi",1200*(_s.r-_s.hi).mean(),_gh,0.6); chk(f"monthly {_k}: gap age",1200*(_s.r-_s.age).mean(),_ga,0.6)
    for _c in ["lo","mid","hi","age"]:
        _x=(_s.r-_s[_c]); _dt=max(_dt,abs(_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x)))-_x.mean()/_nw(_x)))
chk("D.2 robust errors (six lags): largest change in a t-statistic of Table 5",_dt,0.4,0.05)
_x=_D.r-_D.lo; chk("monthly: t lower edge",_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x))),2.3,0.06)
_x=_D["2015":"2017"]; _x=_x.r-_x.mid; chk("monthly: t mid 2015-17",_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x))),2.1,0.06)
chk("monthly: delivered s.e. all",1200*_D.r.std(ddof=1)/np.sqrt(len(_D)),39,1)
chk("monthly: largest month %",100*_D.r.max(),451,1); chk("monthly: largest month is Nov 2013",float(_D.r.idxmax()==pd.Timestamp("2013-10-31")),1,0); chk("monthly: its contribution",1200*_D.r.max()/len(_D),31,0.6)
_x=_D[_D.index.year!=2013]; chk("ex-2013 delivered",1200*_x.r.mean(),69,0.6); chk("ex-2013 mid",1200*_x.mid.mean(),60,0.6); chk("ex-2013 gap mid",1200*(_x.r-_x.mid).mean(),9,0.6); chk("ex-2013 se mid",1200*(_x.r-_x.mid).std(ddof=1)/np.sqrt(len(_x)),21,0.6)
chk("ex-2013 gap lo",1200*(_x.r-_x.lo).mean(),44,0.6); chk("ex-2013 gap hi",1200*(_x.r-_x.hi).mean(),-28,0.6); _y=_x.r-_x.lo; chk("ex-2013 t lo",_y.mean()/(_y.std(ddof=1)/np.sqrt(len(_y))),2.2,0.06)
chk("monthly corr with mid",np.corrcoef(_D.r,_D.mid)[0,1],0.03,0.005); chk("monthly corr with age rule",np.corrcoef(_D.r,_D.age)[0,1],0.17,0.01)
_x=_D[:"2021-05"]; chk("n those months",len(_x),113,0)
chk("band width, average band 2012-14: over 200 points",float(1200*(_D.hi-_D.lo)["2012":"2014"].mean()>200),1,0); chk("band width at the end of May 2026, points",100*(req_hi-foc_lo).iloc[at("2026-05-31")],13,0.5)
_pv=np.sqrt((0.95*0.141)**2+(0.05*0.42)**2+2*0.95*0.05*0.5*0.141*0.42)

chk("equity compound",9-100*0.141**2/2,8,0.05); chk("BTC compound",18-100*0.42**2/2,9,0.3); chk("vol ratio",42/14.1,3,0.06)
_lb=np.log(px).diff()
for _c in ["eth","xrp","bnb","ada","doge","ltc"]:
    _p=pd.read_csv(f"{CSV}/{_c}.csv",parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna().resample("ME").last()
    _x=pd.DataFrame({"b":_lb,"a":np.log(_p).diff()}).dropna()["2018":]; chk(f"beta to BTC since 2018: {_c}",_x.cov().iloc[0,1]/_x.b.var(),1.0,0.155)
chk("fn: all-in at 120% vol",100*1.2**2,144,0.1); chk("fn: conc term lo",100*1.0*0.42**2*0.07,1,0.5); chk("fn: conc term hi",100*2.8*0.42**2*0.19,9,0.5)
_rr=px.pct_change(); chk("delivered 2017-07..2022-12 within the option bound 66-84 (+rf)",1200*_rr["2017-07":"2022-12"].mean(),75,12)
chk("S&P hurdle",5+4,9,0); _dh=[float(x_.split("%")[0]) for x_ in open(os.path.join(OUT,"uncertainty_propagation.txt")).read().split("Bitcoin, diversified holder (w=0)")[1].split("90% ")[1].split("|")[0].split("-")]
chk("diversified hurdle lo (90% range)",_dh[0],12,0.5); chk("diversified hurdle hi (90% range)",_dh[1],16,0.5); chk("rent lo",18.1-_dh[1],2,0.5); chk("rent hi",18.1-_dh[0],6,0.5); chk("overstatement more than two-fifths",(32-18)/32,0.44,0.01)
chk("required return rises per 1% of wealth at gamma 3",3*0.42**2,0.5,0.04)
chk("required at gamma=1",5+7+1.9+100*1*0.42**2*0.13,16,0.3); chk("required at central gamma 1.9",5+7+1.9+100*1.9*0.42**2*0.13,18.3,0.05); chk("required at gamma=0 (central)",5+7+1.9,13.9,0.01)
_rg=np.random.default_rng(1); _Ng=400000
_xg=0.05+_rg.uniform(1.5,2.0,_Ng)*0.04+_rg.uniform(1.0,2.8,_Ng)*0.42**2*_rg.uniform(0.07,0.19,_Ng)+_rg.uniform(0.003,0.035,_Ng); _qg=np.percentile(_xg,[5,50,95])
chk("gamma 1-2.8: median",100*_qg[1],18.1,0.05); chk("gamma 1-2.8: 5%",100*_qg[0],15.2,0.05); chk("gamma 1-2.8: 95%",100*_qg[2],21.8,0.05)
with contextlib.redirect_stdout(io.StringIO()):
    _qh=u.run("h",0.42,1.5,2.0,0.07,0.19,0.003,0.035,glo=1.7)*100; _qm=u.run("m",0.42,1.5,2.0,0.07,0.19,0.003,0.015)*100; _qw=u.run("w",0.42,1.5,2.0,0.11,0.19,0.003,0.035)*100
chk("household gamma: median",_qh[2],19.0,0.05); chk("household gamma: 5%",_qh[0],16.0,0.05); chk("household gamma: 95%",_qh[4],22.3,0.05)
chk("D.1 mortality 0.3-1.5: median",_qm[2],17.0,0.05); chk("D.1 mortality: 5%",_qm[0],14.6,0.05); chk("D.1 mortality: 95%",_qm[4],20.6,0.05)
chk("D.1 w 0.11-0.19: median",_qw[2],18.8,0.05); chk("D.1 w 0.11-0.19: 5%",_qw[0],15.9,0.05); chk("D.1 w 0.11-0.19: 95%",_qw[4],22.3,0.06)
import io as _io, contextlib as _cl
with _cl.redirect_stdout(_io.StringIO()): _qv=u.run("v",0.42,1.5,2.0,0.06,0.12,0.003,0.035)*100; _qv8=u.run("v8",0.42,1.5,2.0,0.05,0.08,0.003,0.035)*100
_zz_r=np.random.default_rng(11); _zz_n=400000; _zz_u=_zz_r.uniform(0,1,_zz_n); _zz_ub=_zz_r.uniform(0,1,_zz_n); _zz_um=_zz_r.uniform(0,1,_zz_n)
_zz_dep=lambda ug,uw,ub,um: 100*np.percentile(0.05+(1.5+0.5*ub)*0.04+(1+1.8*ug)*0.42**2*(0.07+0.12*uw)+0.003+0.032*um,[5,50,95])
_zz_d1=_zz_dep(_zz_u,_zz_u,_zz_ub,_zz_um); _zz_d2=_zz_dep(_zz_u,1-_zz_u,_zz_ub,_zz_um); _zz_e=np.linspace(0,1,len(_zz_u)); _zz_d3=_zz_dep(_zz_e,_zz_e,_zz_e,_zz_e)
chk("D.1 gamma,w together: median",_zz_d1[1],18.3,0.1); chk("D.1 gamma,w together: 5%",_zz_d1[0],14.7,0.1); chk("D.1 gamma,w together: 95%",_zz_d1[2],23.1,0.1)
chk("D.1 gamma,w opposite: median",_zz_d2[1],17.9,0.1); chk("D.1 gamma,w opposite: 5%",_zz_d2[0],16.1,0.1); chk("D.1 gamma,w opposite: 95%",_zz_d2[2],19.8,0.1)
chk("D.1 all together: 5%",_zz_d3[0],13.0,0.1); chk("D.1 all together: 95%",_zz_d3[2],25.0,0.1); chk("D.1 all together: median",_zz_d3[1],18.3,0.05)
# The age rule with its exponent re-estimated in real time (Introduction, Appendix D.2 and D.3; as in 37_age_rule_exponent.py)
_ad=pd.read_csv(os.path.join(CSV,"btc.csv"),parse_dates=["time"]).set_index("time")["PriceUSD"].dropna()
if _ad.index.tz is not None: _ad.index=_ad.index.tz_localize(None)
_afit=lambda x: np.polyfit(np.log((x.index-GEN).days/365.25),np.log(x.values),1)[0]
_abt=pd.Series({t:_afit(_ad[:t]) for t in px.index if t>=pd.Timestamp("2011-12-31")}).reindex(px.index)
chk("exponent real-time: min 2012-14",_abt["2012":"2014"].min(),5.5,0.05); chk("exponent real-time: max 2012-14",_abt["2012":"2014"].max(),8.2,0.05); chk("exponent real-time: min 2015",_abt["2015"].min(),6.0,0.05); chk("exponent real-time: max 2015",_abt["2015"].max(),6.8,0.05); chk("exponent real-time: min since 2016",_abt["2016":].min(),5.6,0.05); chk("exponent real-time: max since 2016",_abt["2016":].max(),6.0,0.05)
_aD=pd.DataFrame({"r":px.shift(-1)/px-1,"fix":((age+1/12)/age)**5.62-1,"rt":((age+1/12)/age)**_abt-1}).dropna(); _aD=_aD[_aD.index>="2012-01-01"]
_ag=lambda a,b,k: 1200*(_aD[a:b].r-_aD[a:b][k]).mean()
chk("age gap real-time, full",_ag("2012","2026","rt"),41,0.6); chk("age gap fixed, full",_ag("2012","2026","fix"),48,0.6); chk("age gap real-time 2012-14",_ag("2012","2014","rt"),121,0.6); chk("age gap real-time 2015-17",_ag("2015","2017","rt"),77,0.6)
chk("age gap change since 2018, max over periods",max(abs(_ag(a,b,"rt")-_ag(a,b,"fix")) for a,b in (("2018","2020"),("2021","2023"),("2024","2026"),("2018","2026"))),2,0.5)
_aW=pd.DataFrame({"f":fwd_mu,"mid":req_mid,"rt":(1+5/age)**(_abt/5)-1}).dropna()["2012":]
chk("D.3 real-time age rule: MAE",100*(_aW.f-_aW.rt).abs().mean(),32,0.6); chk("D.3 real-time age rule: corr",_aW.f.corr(_aW.rt),0.72,0.006); chk("D.3 real-time age rule: closer %",100*((_aW.f-_aW.rt).abs()<(_aW.f-_aW.mid).abs()).mean(),73,0.6)
# Equity premium: Damodaran's implied premium at year-ends 2020-2025 (histimpl table, retrieved 12 Nov 2026)
_erp={2020:4.72,2021:4.24,2022:5.94,2023:4.60,2024:4.33,2025:4.23}
chk("implied ERP start of 2026",_erp[2025],4.2,0.05); chk("implied ERP min 2020-25",min(_erp.values()),4.2,0.05); chk("implied ERP max 2020-25",max(_erp.values()),5.9,0.05); chk("implied ERP max is end-2022",float(max(_erp,key=_erp.get)),2022,0.1)
# Worked example of the monthly test (Section 5, Step 3): December 2023
_wi=at("2023-12-31"); _wm=req_mid.iloc[_wi]; _wr=px.iloc[_wi+1]/px.iloc[_wi]-1
chk("example: midpoint Dec 2023, % a year",100*_wm,25.0,0.05); chk("example: required for the month, %",100*(np.exp(_wm/12)-1),2.1,0.05); chk("example: Bitcoin's return Jan 2024, %",100*_wr,0.9,0.05); chk("example: gap, points",100*(_wr-(np.exp(_wm/12)-1)),-1.2,0.05)
# Other groupings of the monthly test (Appendix D.2; as in 38_grouping_robustness.py)
_gD=pd.DataFrame({"r":px.shift(-1)/px-1,"lo":np.exp(foc_lo/12)-1,"mid":np.exp(req_mid/12)-1,"hi":np.exp(req_hi/12)-1}).dropna(); _gD=_gD[_gD.index>="2012-01-01"]
def _grow(a,b):
    _s=_gD.loc[a:b]; _e=_s.r-_s.mid; _d=1200*_s.r.mean(); return (0 if 1200*_s.lo.mean()<=_d<=1200*_s.hi.mean() else (1 if _d>1200*_s.hi.mean() else -1)), 1200*_e.mean(), 1200*_e.std(ddof=1)/np.sqrt(len(_e))
_gy=[_grow(str(y),str(y)) for y in range(2012,2027)]
chk("grouping: years inside band",sum(r[0]==0 for r in _gy),3,0.1); chk("grouping: years above",sum(r[0]==1 for r in _gy),7,0.1); chk("grouping: years below",sum(r[0]==-1 for r in _gy),5,0.1)
chk("grouping: yearly gap min",min(r[1] for r in _gy),-292,0.6); chk("grouping: yearly gap max",max(r[1] for r in _gy),613,0.6); chk("grouping: yearly se min",min(r[2] for r in _gy),36,0.6); chk("grouping: yearly se max",max(r[2] for r in _gy),474,1)
for _gq_a,_gq_g,_gq_t in (("2014",-158,-3.1),("2016",159,2.6),("2018",-18,None),("2020",75,None),("2022",-7,None),("2024",19,None)):
    _gq_r=_grow(_gq_a,str(int(_gq_a)+1)); chk(f"grouping: two-year gap from {_gq_a}",_gq_r[1],_gq_g,0.6)
    if _gq_t is not None: chk(f"grouping: two-year t from {_gq_a}",_gq_r[1]/_gq_r[2],_gq_t,0.06)
    else: chk(f"grouping: two-year |t| below 2 from {_gq_a}",float(abs(_gq_r[1]/_gq_r[2])<2),1,0)
for (_gq_a,_gq_b),_gq_g in zip((("2012","2015"),("2016","2019"),("2020","2023"),("2024","2026")),(72,70,34,13)):
    _gq_r=_grow(_gq_a,_gq_b); chk(f"grouping: four-year gap {_gq_a}-{_gq_b}",_gq_r[1],_gq_g,0.6); chk(f"grouping: four-year |t| below 2 {_gq_a}-{_gq_b}",float(abs(_gq_r[1]/_gq_r[2])<2),1,0)
# Section 2 example: the cost of a position and of the next dollar (gamma 2, sigma 0.42)
_s2=0.42**2; chk("example: sigma squared",_s2,0.176,0.0005); chk("example: at 19%",100*2*_s2*0.19,6.7,0.05); chk("example: at 5%",100*2*_s2*0.05,1.8,0.05)
# Appendix B.2: the fund-investor weight at 3% instead of 1.5%
_c26=cap.reindex(px.index).iloc[-1]
chk("B.2 w lower bound at 3%",100*_c26/(Wp.iloc[-1]+inst_val.iloc[-1]/0.03),11,0.5); chk("B.2 fund-investor wealth at 1.5% ($tn)",inst_val.iloc[-1]/0.015/1e12,13,0.6); chk("B.2 fund-investor wealth at 3% ($tn)",inst_val.iloc[-1]/0.03/1e12,6,0.5); chk("B.2 survey-type wealth ($tn)",Wp.iloc[-1]/1e12,8,0.5)
# Option-implied cap on a collapse to zero (Appendix C.5); quotes of 12 Nov 2026 as in 35_option_bound.py
_ox=0.0035*73477.85; chk("option cap: put price $",_ox,257,1); chk("option cap: % of strike",100*_ox/30000,0.86,0.005); chk("option cap: before expiry %",100*_ox/30000*76081.74/73477.85,0.9,0.05); chk("option cap: % a year",100*_ox/30000*76081.74/73477.85/(225/365),1.4,0.05)
# Ownership at the 2021Q3 anchor (Appendix D.4): 3% in 2021Q3 and 11% by mid-2022, everything else as in the baseline
_oA='pd.Timestamp("2021-09-30"):0.11,'; assert src.count(_oA)==1
_os=src.replace(_oA,'pd.Timestamp("2021-09-30"):0.03,pd.Timestamp("2022-06-30"):0.11,'); _on={"__file__":__file__}
exec(_os.split("# ============ FIG 1")[0],_on); exec(_os[_os.index("# ============ FIG 5"):_os.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")],_on)
_oat=lambda d: _on["px"].index.get_indexer([pd.Timestamp(d)],method="nearest")[0]
chk("D.4 ownership alt: early holder mid-2019",_on["seg"].iloc[_oat("2019-06-30")],0.75,0.005); chk("D.4 ownership alt: early holder mid-2019, baseline",seg.iloc[at("2019-06-30")],0.51,0.005); chk("D.4 ownership alt: upper edge mid-2019",100*_on["req_hi"].iloc[_oat("2019-06-30")],63,0.5); chk("D.4 ownership alt: upper edge mid-2019, baseline",100*req_hi.iloc[at("2019-06-30")],51,0.5); chk("D.4 ownership alt: w 2026 with funds",100*_on["w_lo"].iloc[-1],7,0.5)
chk("D.4 ownership alt: anchor weight unchanged",100*_on["w_hi"].iloc[_oat("2021-09-30")],100*w_hi.iloc[at("2021-09-30")],0.01)
chk("D.4 ownership alt: band 2013 lo",100*_on["foc_lo"].iloc[_oat("2013-06-30")],56,0.5); chk("D.4 ownership alt: band 2013 hi",100*_on["req_hi"].iloc[_oat("2013-06-30")],231,0.5); chk("D.4 ownership alt: band 2026 lo",100*_on["foc_lo"].iloc[-1],12,0.5); chk("D.4 ownership alt: band 2026 hi",100*_on["req_hi"].iloc[-1],25,0.5)
_oD=pd.DataFrame({"r":_on["px"].shift(-1)/_on["px"]-1,"mid":np.exp(_on["req_mid"]/12)-1}).dropna(); _oD=_oD[_oD.index>="2012-01-01"]; _oe=_oD.r-_oD.mid
chk("D.4 ownership alt: gap 2012-17",1200*_oe["2012":"2017"].mean(),101,0.5); chk("D.4 ownership alt: gap since 2018",1200*_oe["2018":].mean(),15,0.5); chk("D.4 ownership alt: no gap moves by more than a point",float(abs(1200*_oe["2018":].mean()-1200*(_D.r-_D.mid)["2018":].mean())<=1 and abs(1200*_oe["2012":"2017"].mean()-1200*(_D.r-_D.mid)["2012":"2017"].mean())<=1 and abs(1200*_oe.mean()-1200*(_D.r-_D.mid).mean())<=1),1,0)
# Beta by window (Table in Appendix A.2) and the two beta sensitivities of D.1
def _seB(x):
    b=B(x); a_=x.b.mean()-b*x.s.mean(); e_=x.b-a_-b*x.s; return np.sqrt(e_.var(ddof=2)/((x.s-x.s.mean())**2).sum())
for _lab,_x,_cb,_cs,_cc in (("2y",_d.iloc[-24:],1.26,0.64,0.39),("3y",_d.iloc[-36:],1.38,0.54,0.40),("4y",_d.iloc[-48:],1.75,0.43,0.52),("5y",_d.iloc[-60:],1.81,0.38,0.53),("since 2020",_d["2020":],1.93,0.35,0.54),("since 2016",_d["2016":],1.51,0.38,0.34),("since 2012",_d["2012":],1.77,0.45,0.29)):
    chk(f"beta table {_lab}: beta",B(_x),_cb,0.006); chk(f"beta table {_lab}: se",_seB(_x),_cs,0.006); chk(f"beta table {_lab}: corr",_x.b.corr(_x.s),_cc,0.006)
chk("beta table months since 2020",len(_d["2020":]),77,0.5); chk("beta table months since 2016",len(_d["2016":]),125,0.5); chk("beta table months since 2012",len(_d["2012":]),173,0.5)
import io as _io2, contextlib as _cl2
with _cl2.redirect_stdout(_io2.StringIO()): _qb=u.run("b",0.42,1.3,2.2,0.07,0.19,0.003,0.035)*100
chk("D.1 beta 1.3-2.2: median",_qb[2],18.1,0.1); chk("D.1 beta 1.3-2.2: 5%",_qb[0],14.8,0.1); chk("D.1 beta 1.3-2.2: 95%",_qb[4],22.1,0.1)
_zr=np.random.default_rng(5); _zn=400000; _zx=100*np.percentile(0.05+_zr.normal(1.75,0.45,_zn)*0.04+_zr.uniform(1,2.8,_zn)*0.42**2*_zr.uniform(0.07,0.19,_zn)+_zr.uniform(0.003,0.035,_zn),[5,50,95])
chk("D.1 beta normal: median",_zx[1],18.2,0.1); chk("D.1 beta normal: 5%",_zx[0],14.0,0.1); chk("D.1 beta normal: 95%",_zx[2],22.7,0.1)
chk("rolling corr min since mid-2022",corr_roll["2022-06":].min(),0.4,0.03); chk("rolling corr max since mid-2022",corr_roll["2022-06":].max(),0.6,0.06); chk("S8 rolling correlation, highest since 2012",corr_roll["2012":].max(),0.57,0.005); chk("S8 rolling correlation, lowest since 2012 is about zero",corr_roll["2012":].min(),0.0,0.05)
chk("D.1 w 0.06-0.12: median",_qv[2],16.9,0.05); chk("D.1 w 0.06-0.12: 5%",_qv[0],14.5,0.05); chk("D.1 w 0.06-0.12: 95%",_qv[4],19.5,0.06); chk("D.1 w 0.05-0.08: median",_qv8[2],16.1,0.05); chk("D.1 w 0.05-0.08: 5%",_qv8[0],14.0,0.05); chk("D.1 w 0.05-0.08: 95%",_qv8[4],18.2,0.05)
chk("compound range lo",15.2-8.8,7,0.61); chk("compound range hi",21.8-8.8,13,0.5); chk("compound envelope lo",12.5-8.8,4,0.5); chk("compound envelope hi",25.9-8.8,17,0.5); chk("excess return",18-5,13,0); chk("compound central",18.1-8.8,9.3,0.05)
chk("gold conc max",100*2.8*0.2**2*0.1,1.1,0.05); chk("gold envelope lo",5-0.4+100*1.0*0.13**2*0.02,4.6,0.05)
chk("BTC share of global household wealth (about $510T) is well under 1%",float(100*cap.iloc[-1]/510e12<0.6),1,0); chk("conc term at a 0.5% weight is under 0.2 points",float(100*1.9*0.42**2*0.005<0.2),1,0); chk("mortality example: 3% x 95%",3*0.95,2.9,0.06)
chk("all-in bound nominal lo",5+100*0.40**2,21,0.1); chk("all-in bound nominal hi",5+100*0.55**2,35,0.3)
def _seB(x):
    b=B(x); a_=x.b.mean()-b*x.s.mean(); e_=x.b-a_-b*x.s; return np.sqrt(e_.var(ddof=2)/((x.s-x.s.mean())**2).sum())
chk("beta 5y",B(_d.iloc[-60:]),1.8,0.05); chk("beta 5y se",_seB(_d.iloc[-60:]),0.4,0.05); chk("beta 3y",B(_d.iloc[-36:]),1.4,0.05); chk("beta 3y se",_seB(_d.iloc[-36:]),0.5,0.05); chk("beta 2y",B(_d.iloc[-24:]),1.3,0.05); chk("beta 2y se",_seB(_d.iloc[-24:]),0.6,0.05); chk("JPM US large cap premium over 5%",7.9-5,3,0.15)
for _y,_v in [(2012,1.7),(2020,0.7),(2023,3.8)]: chk(f"rf path {_y}",100*rf.iloc[at(f"{_y}-06-30")],_v,0.05)
_tn=pd.read_csv(os.path.join(DATA,"tnx_monthly.csv"),parse_dates=["Date"]).set_index("Date")["Close"]
for _mth,_v in [("2026-09-01",5.3),("2026-10-01",4.9),("2026-11-01",5.0)]: chk(f"TNX {_mth}",_tn.loc[_mth],_v,0.05)
chk("rf May 2026",100*rf.iloc[-1],4.5,0.05)
chk("participation 2025 anchor",100*qpart.iloc[at("2025-06-30")],12,0.05); chk("participation 2021Q3 anchor",100*qpart.iloc[at("2021-09-30")],11,0.05); chk("back-cast w 2026 implied by flat participation",18.6*(cap.iloc[-1]/cap.iloc[i21])/1.4*11/12,23,1)
for _n,_mu,_sg,_dr,_cp,_sh in [("global",8.8,13.8,1.0,7.8,0.28),("sp500",9.0,14.1,1.0,8.0,0.28),("gold",5.5,15.5,1.2,4.3,0.03),("btc",18.1,42,8.8,9.3,0.31),("eth",23.0,64,20.5,2.5,0.28)]:
    chk(f"compound table {_n}: drag",_sg**2/200,_dr,0.05); chk(f"compound table {_n}: compound",_mu-_sg**2/200,_cp,0.05); chk(f"compound table {_n}: Sharpe",(_mu-5)/_sg,_sh,0.006)
for _n,_mu,_sg,_cs in [("global",8.8,13.83,0.21),("sp500",9.0,14.06,0.21),("nasdaq",9.48,17.226,0.17),("russell",9.7,19.138,0.15),("gold",5.5,15.5,-0.05),("btc",18.1,42,0.10),("eth",23.0,64,-0.04)]:
    chk(f"compound table {_n}: Sharpe on the compound return",(_mu-_sg**2/200-5)/_sg,_cs,0.0051)
chk("compound Sharpe: BTC below every equity index",float(0.10<min([0.21,0.21,0.17,0.15])),1,0)
chk("drag share BTC about half",8.8/18.1,0.5,0.03); chk("drag share ETH nearly nine-tenths",20.5/23.0,0.89,0.01)
chk("drift example: +100%,-50% average",(100-50)/2,25,0)
chk("age rule closer share",100*(np.abs(fwd_mu-age_rule)<np.abs(fwd_mu-req_mid))[mm].mean(),81,0.6); chk("corr realized, mid",np.corrcoef(fwd_mu[mm],req_mid[mm])[0,1],0.43,0.006); chk("corr realized, age rule",np.corrcoef(fwd_mu[mm],age_rule[mm])[0,1],0.86,0.02)
# Figure 2, panel (c): shares
mort_t=0.5*(0.003+0.035)
def shares(d):
    i=at(d); tot=req_mid.iloc[i]; conc=max(tot-rf.iloc[i]-beta_term.iloc[i]-mort_t,0); return 100*tot,100*np.array([rf.iloc[i],beta_term.iloc[i],conc,mort_t])/tot
t13,s13=shares("2013-06-30"); chk("Fig6 2013 total",t13,144,0.5); chk("Fig6 2013 conc share",s13[2],89,0.6)
t21,s21_=shares("2021-09-30"); chk("Fig6 2021 conc share (text: about 70%)",s21_[2],70,1.0)
t26,s26=shares("2026-04-30"); chk("Fig6 2026 total",t26,19.2,0.05)
for k,vv,lab in [(0,23,"rf"),(1,38,"market"),(2,30,"conc"),(3,10,"mort")]: chk(f"Fig6 2026 share {lab}",s26[k],vv,0.51)
# Section 7/8
e=pd.read_csv(os.path.join(CSV,"eth.csv"),parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna().resample("ME").last()
le=np.log(e).diff()["2021-10":]; chk("ETH drift 2021Q3->",100*(12*le.mean()+6*le.var()),19,1); chk("ETH CAGR 2021Q3->",100*(np.exp(12*le.mean())-1),-7,0.6)
de=pd.DataFrame({"b":np.log(e).diff(),"s":_d.s}).dropna(); chk("ETH beta 4y",B(de.iloc[-48:]),2.7,0.05); chk("ETH beta since 2016",B(de["2016":]),2.0,0.05)
chk("altcoin drift from -7% CAGR at 80% vol",-7+32,25,1); chk("altcoin shortfall",39-25,15,1.5); chk("market share of required",7/18,0.4,0.02)
chk("hurdle lo",5+6,11,0.1); chk("hurdle hi",5+8,13,0.1); chk("sizing",100*(18.1-5-7-1.9)/(3*0.42**2*100),8,0.5); chk("sizing age rule",100*(32-5-7-1.9)/(3*0.42**2*100),34,0.5); chk("sizing across the hurdle range, low",100*(18.1-_dh[1])/(3*0.42**2*100),5,0.5); chk("sizing across the hurdle range, high",100*(18.1-_dh[0])/(3*0.42**2*100),11,0.5)
chk("Sharpe BTC",(18.1-5)/42,0.31,0.006); chk("Sharpe BTC ex mort",(18.1-5-1.9)/42,0.27,0.01); chk("Sharpe conc",1.9*0.42*0.13,0.10,0.005); chk("Sharpe mort",1.9/42,0.05,0.005); 
# Appendix B
Wp_r=cap.iloc[i21]/0.19*(qpart/qpart.iloc[i21])*interp({2012:0.25,2021:1.0,2026:1.4}); wr=cap.reindex(px.index)/Wp_r
chk("B: wealth 2021Q3 $T",cap.iloc[i21]/0.19/1e12,4.3,0.2); chk("B: surveyed owners' wealth May 2026 $T",Wp.iloc[-1]/1e12,8,0.5); chk("D.4 market-value path: w mid-2012",100*wr.iloc[at("2012-06-30")],0.7,0.05); chk("D.4 market-value path: w December 2017",100*wr.iloc[at("2017-12-31")],80,0.5); chk("D.4 market-value path: w December 2022",100*wr.iloc[at("2022-12-31")],6,0.5); chk("D.4 market-value path: w mid-2025",100*wr.iloc[at("2025-06-30")],34,0.5)
chk("D.4 market-value path: w May 2026",100*wr.iloc[-1],23,0.5); chk("B: w 2026 with fund and treasury investors",100*w_lo.iloc[-1],7.4,0.05); chk("B.3 the same without 3.5 million lost coins",100*(_c26:=cap.reindex(px.index).iloc[-1])*(1-3.5e6*px.iloc[-1]/_c26)/(_c26*(1-3.5e6*px.iloc[-1]/_c26)/0.19+inst_val.iloc[-1]/0.015),6.6,0.05); chk("B: inst value $B",2.5e6*px.iloc[-1]/1e9,190,8)
chk("B: address path 2018",100*q_addr.iloc[at("2018-06-30")],6.4,0.2); chk("B: survey path 2018",100*qpart.iloc[at("2018-06-30")],1.2,0.05)
print(f"\n{sum(res)} PASS, {len(res)-sum(res)} FAIL")

# ETF-measured volatilities for the compound table (monthly log total returns, Jan 2012 to Apr 2026)
def _lr(f):
    _x=pd.read_csv(f,parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; return np.log(_x).diff().dropna()
_E=pd.DataFrame({"VT":_lr(os.path.join(DATA,"vt_monthly.csv")),"VOO":_lr(os.path.join(DATA,"voo_monthly.csv")),"GLD":_lr(os.path.join(DATA,"gld_monthly.csv"))}).dropna()["2012-01":"2026-04"]
chk("ETF vol sample months",len(_E),172,0.5); chk("vol VT",100*_E.VT.std()*12**.5,14.0,0.05); chk("vol VOO",100*_E.VOO.std()*12**.5,14.1,0.05); chk("vol GLD",100*_E.GLD.std()*12**.5,15.5,0.05); chk("corr VT VOO",_E.corr().loc["VT","VOO"],0.96,0.005)
chk("equity Sharpe range lo",4/20,0.20,0.005); chk("equity Sharpe range hi",4/14.1,0.28,0.005); chk("equity Sharpe high case lo",6/20,0.30,0.005); chk("equity Sharpe high case hi",6/14,0.43,0.005)
chk("CAGR VOO 2012-26",100*(np.exp(12*_E.VOO.mean())-1),15,0.5); chk("CAGR VT 2012-26",100*(np.exp(12*_E.VT.mean())-1),12,0.5)
_A=pd.DataFrame({"ACWI":_lr(os.path.join(DATA,"acwi_monthly.csv")),"VOO":_lr(os.path.join(DATA,"voo_monthly.csv"))}).dropna()["2012-01":"2026-04"]
_fx=np.log(pd.read_csv(os.path.join(DATA,"eurusd_monthly.csv"),parse_dates=["Date"]).sort_values("Date").set_index("Date")["Close"]).diff().reindex(_A.index)
_bA=_A.cov().loc["ACWI","VOO"]/_A.VOO.var()
chk("ACWI months",len(_A),172,0.5); chk("vol ACWI",100*_A.ACWI.std()*12**.5,13.8,0.05); chk("beta ACWI on VOO",_bA,0.95,0.005); chk("corr ACWI VOO",_A.corr().loc["ACWI","VOO"],0.97,0.005); chk("ACWI premium",4*_bA,3.8,0.05)
chk("CAGR ACWI 2012-26",100*(np.exp(12*_A.ACWI.mean())-1),11.5,0.1); chk("EUR vol ACWI",100*(_A.ACWI-_fx).std()*12**.5,12.6,0.05); chk("EUR vol VOO",100*(_A.VOO-_fx).std()*12**.5,13.8,0.05)
_Q=pd.DataFrame({"QQQ":_lr(os.path.join(DATA,"qqq_monthly.csv")),"IWM":_lr(os.path.join(DATA,"iwm_monthly.csv")),"VOO":_lr(os.path.join(DATA,"voo_monthly.csv"))}).dropna()["2012-01":"2026-04"]
for _k,_v,_be,_cg in (("QQQ",17.2,1.12,20),("IWM",19.1,1.18,11)):
    _bq=_Q.cov().loc[_k,"VOO"]/_Q.VOO.var(); _vq=100*_Q[_k].std()*12**.5; _av=5+round(4*_bq,1)
    chk(f"{_k} months",len(_Q),172,0.5); chk(f"vol {_k}",_vq,_v,0.06); chk(f"beta {_k} on VOO",_bq,_be,0.006); chk(f"CAGR {_k} 2012-26",100*(np.exp(12*_Q[_k].mean())-1),_cg,0.5)
    chk(f"{_k} average",_av,{"QQQ":9.5,"IWM":9.7}[_k],0.01); chk(f"{_k} drag",_vq**2/200,{"QQQ":1.5,"IWM":1.8}[_k],0.05); chk(f"{_k} compound",_av-_vq**2/200,{"QQQ":8.0,"IWM":7.9}[_k],0.05); chk(f"{_k} Sharpe",(_av-5)/_vq,{"QQQ":0.26,"IWM":0.25}[_k],0.005)
chk("gold CAGR end-2023 to Nov 2026",100*((4040/2060)**(1/2.87)-1),26,0.6); chk("gold stock value $tn",224000*32150.7*4040/1e12,29,0.5)
# Appendix E.2: the equity beta does not run through on-chain activity (independent of 33_activity_beta.py)
import statsmodels.api as _sm
def _etf(_f):
    _x=pd.read_csv(f"{DATA}/{_f}_monthly.csv",parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; _y=np.log(_x).diff(); _y.index=_y.index.to_period("M"); return _y
_cm=pd.read_csv(os.path.join(CSV,"btc.csv"),parse_dates=["time"]).set_index("time")
_mm=pd.DataFrame({"btc":_cm.PriceUSD.resample("ME").last(),"act":_cm.AdrActCnt.resample("ME").mean()}); _mm.index=_mm.index.to_period("M")
_gg=np.log(_mm).diff(); _gg["spx"]=_etf("voo"); _gg["gold"]=_etf("gld"); _gg=_gg["2012-01":"2026-04"].dropna(); _g20=_gg["2020-01":]
_hac=lambda _y,_X: _sm.OLS(_y,_sm.add_constant(_X)).fit(cov_type="HAC",cov_kwds={"maxlags":3})
chk("E.2 months since 2020",len(_g20),76,0.5); chk("E.2 corr activity growth, equity",_g20.act.corr(_g20.spx),0.18,0.005)
chk("E.2 equity coef with gold",_hac(_g20.btc,_g20[["spx","gold"]]).params["spx"],2.0,0.05); chk("E.2 equity coef with gold and activity",_hac(_g20.btc,_g20[["spx","gold","act"]]).params["spx"],1.9,0.05)
_ll=_gg.assign(btc1=_gg.btc.shift(1),act1=_gg.act.shift(1)).dropna()
chk("E.2 lagged price -> activity, t",_hac(_ll.act,_ll[["btc1","act1"]]).tvalues["btc1"],2.8,0.05); chk("E.2 lagged activity -> price, t",_hac(_ll.btc,_ll[["act1","btc1"]]).tvalues["act1"],0.7,0.05)
_yy=_cm.assign(fee=_cm.FeeTotNtv*_cm.PriceUSD).resample("YE").agg({"AdrActCnt":"mean","CapMrktCurUSD":"mean","fee":"sum"}); _yy.index=_yy.index.year
chk("E.2 active addresses 2017 (thousand)",_yy.AdrActCnt[2017]/1e3,760,5); chk("E.2 active addresses 2025 (thousand)",_yy.AdrActCnt[2025]/1e3,720,5); chk("E.2 cap 2025/2017",_yy.CapMrktCurUSD[2025]/_yy.CapMrktCurUSD[2017],30,1)
chk("E.2 fees % cap 2017",100*_yy.fee[2017]/_yy.CapMrktCurUSD[2017],0.8,0.05); chk("E.2 fees % cap 2025",100*_yy.fee[2025]/_yy.CapMrktCurUSD[2025],0.01,0.005)
_b=pd.read_csv(os.path.join(CSV,"btc.csv"),parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna().resample("ME").last()
chk("sigma EWMA hl9 May 2026",100*np.sqrt(np.log(_b).diff().pow(2).ewm(halflife=9).mean().iloc[-1]*12),42,0.5)
chk("beta x ERP lo",1.5*4,6,0.01); chk("beta x ERP hi",2.0*4,8,0.01); chk("conc lo",1.0*0.42**2*7,1,0.5); chk("conc hi",2.8*0.42**2*19,9,0.5)
_opt=(rf+seg*sig2>foc_hi)[m]
chk("early holder sets the upper edge, share of months",100*_opt.mean(),49,1.0); chk("early holder last sets it 2019-01",float(_opt[_opt].index[-1].year*100+_opt[_opt].index[-1].month),201901,0.1); chk("early holder sets the upper edge in every month of 2012-18",float(_opt["2012":"2018"].all()),1,0); chk("early weight mid-2018",seg.iloc[at("2018-06-30")],1.0,0.001); chk("early weight mid-2019",seg.iloc[at("2019-06-30")],0.5,0.02); chk("early weight 2021Q3",seg.iloc[at("2021-09-30")],0.1,0.012); chk("owners implied 2013 (thousand)",q.iloc[at("2013-06-30")]*258e6/1e3,600,15); chk("wealth each if all-in 2013",cap.iloc[at("2013-06-30")]/(q.iloc[at("2013-06-30")]*258e6),1700,150); chk("months in band path",float(m.sum()),172,2)
for _dt,_wl,_wh in [("2013-06-30",19,19),("2017-06-30",17,19),("2021-09-30",12,19),("2026-05-31",7,19)]:
    chk(f"band table w_lo {_dt}",100*w_lo.iloc[at(_dt)],_wl,0.6); chk(f"band table w_hi {_dt}",100*w_hi.iloc[at(_dt)],_wh,0.6)
chk("the two weights coincide until the Grayscale trust begins (September 2013)",float((w_lo[:"2013-09-30"]-w_hi[:"2013-09-30"]).abs().max()),0,1e-9); chk("market term edges 2026",0.85*1.75*4,6,0.06); chk("market term hi 2026",1.15*1.75*4,8,0.06); chk("beta range in proportion lo",1.5/1.75,0.85,0.01); chk("beta range in proportion hi",2.0/1.75,1.15,0.01)
chk("monthly return min annualized",1200*_D.r.min(),-470,6); chk("monthly return max annualized",1200*_D.r.max(),5400,10)
# Table 5 recomputed independently from the published monthly series, and checked against the figure markers
_m=pd.read_csv(os.path.join(OUT,"required_band_monthly.csv"),parse_dates=["month_end"]).set_index("month_end")
_rr=px.pct_change().shift(-1).reindex(_m.index)
_Q=pd.DataFrame({"r":_rr,"lo":np.exp(_m.required_lower/12)-1,"mid":np.exp(_m.required_midpoint/12)-1,"hi":np.exp(_m.required_upper/12)-1,"ar":(1+1/12/_m.age_years)**5.62-1}); _Q=_Q[(_Q.index>="2012-01-01")&(_Q.index<="2026-04-30")].dropna()
_T5={("2012","2026"):(118,27,109,67,91,51,39,9,48),("2012","2014"):(278,60,298,174,218,104,169,-21,143),("2015","2017"):(160,27,98,62,132,98,46,62,82),("2018","2020"):(69,17,57,37,52,32,47,12,15),("2021","2023"):(30,15,44,29,15,1,38,-14,-12),("2024","2026"):(36,14,33,23,22,13,33,4,1),("2012","2017"):(219,44,198,118,175,101,87,21,112),("2018","2026"):(46,16,45,30,30,15,23,1,1)}
for (_a,_b),_v in _T5.items():
    _x=_Q[_a:_b]; _g=_x.r-_x.mid
    _c=[1200*_x.r.mean(),1200*_x.lo.mean(),1200*_x.hi.mean(),1200*_x.mid.mean(),1200*(_x.r-_x.lo).mean(),1200*_g.mean(),1200*_g.std()/np.sqrt(len(_x)),1200*(_x.r-_x.hi).mean(),1200*(_x.r-_x.ar).mean()]
    for _n,_cc,_vv in zip(["delivered","band lo","band hi","mid","gap lo","gap mid","se mid","gap hi","gap age"],_c,_v): chk(f"T5 {_a}-{_b} {_n}",_cc,_vv,0.6)
chk("T5 months",len(_Q),172,0)
chk("T5 note: plain average midpoint 2012-14",100*_m.required_midpoint["2012":"2014"].mean(),161,0.6); chk("T5 note: plain average within half a point after 2020",float(max(abs(1200*_Q[_a:_b].mid.mean()-100*_m.required_midpoint[_a:_b][:"2026-04-30"].mean()) for _a,_b in (("2021","2023"),("2024","2026")))<0.5),1,0)
_x=_m[(_m.index>="2012-01-01")&(_m.index<="2017-12-31")]; _rs=px.pct_change().shift(-1).reindex(_x.index)
_oth=(_x.risk_free+_x.beta_4y*0.04+0.019).mean(); _s2=(_x.volatility**2).mean()
chk("implied gamma*w 2012-17",(12*_rs.mean()-_oth)/_s2,1.2,0.06); chk("its standard error",12*_rs.std()/np.sqrt(len(_rs))/_s2,0.5,0.03)

def _pxm(f):
    _z=pd.read_csv(f,parse_dates=["Date"]).sort_values("Date").set_index("Date")["AdjClose"]; _z.index=_z.index+pd.offsets.MonthEnd(0); return np.log(_z).diff()
_G=pd.DataFrame({"b":np.log(px).diff(),"s":_pxm(os.path.join(DATA,"voo_monthly.csv")),"g":_pxm(os.path.join(DATA,"gld_monthly.csv"))}).dropna()[:"2026-04"]
_g1=_G["2020":]; _g0=_G["2012":"2019"]
chk("corr BTC S&P since 2020",_g1.corr().loc["b","s"],0.54,0.006); chk("corr BTC gold since 2020",_g1.corr().loc["b","g"],0.04,0.006); chk("corr BTC S&P before 2020",_g0.corr().loc["b","s"],0.16,0.006); chk("corr BTC gold before 2020",_g0.corr().loc["b","g"],-0.02,0.006)
_X=np.column_stack([np.ones(len(_g1)),_g1.s,_g1.g]); _bb=np.linalg.lstsq(_X,_g1.b,rcond=None)[0]; _rs_=_g1.b-_X@_bb; _se=np.sqrt(np.diag(_rs_.var(ddof=3)*np.linalg.inv(_X.T@_X)))
chk("joint regression: equity coefficient",_bb[1],2.0,0.05); chk("its t",_bb[1]/_se[1],5.6,0.1); chk("gold coefficient |t| below 1",float(abs(_bb[2]/_se[2])<1),1,0)
_rg=np.random.default_rng(1); _N=400000; _sg=_rg.uniform(0.13,0.20,_N)
chk("gold: concentration term, middle",100*np.median(_rg.uniform(1,2.8,_N)*_sg**2*_rg.uniform(0.02,0.10,_N)),0.3,0.05); chk("gold: mortality middle",0.15,0.15,0.001); chk("gold: premium",0+0.3+0.15,0.5,0.06)
# Section 6 (31_cross_section.py and the appended runs of 23_uncertainty.py)
import runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()): _cs=runpy.run_path(os.path.join(SCRIPTS,"31_cross_section.py"))
_st=_cs["stats"]; _S=_cs["S"]; _O=_cs["O"]; _Rn=_cs["Rn"]; _Rna=_cs["Rna"]; _Rnw=_cs["Rnw"]
chk("kappa BTC 4y",_st("btc")["kappa"],1.04,0.006); chk("kappa BTC since 2018",_st("btc",100)["kappa"],0.99,0.006); chk("kappa ETH 4y",_st("eth")["kappa"],0.7,0.006); chk("kappa ETH since 2018",_st("eth",100)["kappa"],0.68,0.03)
chk("alive altcoins with 4y prices",len(_S),51,0); chk("alt median vol (EWMA)",100*_S.vol_ewma.median(),76,0.6); chk("alt vol q1",100*_S.vol_ewma.quantile(.25),68,0.6); chk("alt vol q3",100*_S.vol_ewma.quantile(.75),88,0.6)
chk("alt beta q1",_S.beta_eq.quantile(.25),1.6,0.06); chk("alt beta q3",_S.beta_eq.quantile(.75),2.7,0.06); chk("alt kappa median",_S.kappa.median(),0.47,0.006); chk("alt kappa q1",_S.kappa.quantile(.25),0.41,0.006); chk("alt kappa q3",_S.kappa.quantile(.75),0.56,0.006)
def _dl(x,a0="2018-01",b0="2026-04"):
    bk=x[a0:b0].mean(axis=1).dropna() if isinstance(x,pd.DataFrame) else x[a0:b0].dropna()
    return 1200*bk.mean(),1200*bk.std()/np.sqrt(len(bk)),100*(np.exp(12*np.log1p(bk).mean())-1),len(bk)
for _n,_x,_v in [("BTC",_Rn["btc"],(46,23,28)),("ETH",_Rn["eth"],(48,32,8)),("alt basket",_Rna,(37,33,-3))]:
    _r=_dl(_x); chk(f"S6 delivered {_n} average",_r[0],_v[0],0.6); chk(f"S6 delivered {_n} se",_r[1],_v[1],0.6); chk(f"S6 delivered {_n} compound",_r[2],_v[2],0.6); chk(f"S6 {_n} months",_r[3],100,0)
chk("S6 basket compound, feed deaths at -100%",_dl(_Rnw)[2],-4,0.6); chk("S6 ETH since 2021Q3 average",_dl(_Rn["eth"],"2021-09")[0],19,0.6); chk("S6 ETH since 2021Q3 se",_dl(_Rn["eth"],"2021-09")[1],35,0.6)
chk("S6 altcoins in basket",len(_O),77,0); chk("S6 dead in basket",int(_O.dead.sum()),24,0); chk("S6 median altcoin compound",100*_O.cagr.median(),-28,0.6); chk("S6 share losing money",100*(_O.cagr<0).mean(),83,0.6)
chk("S6 basket max assets",int(_Rna["2018-01":"2026-04"].notna().sum(axis=1).max()),77,0)
_u=dict(l.split(" median ") for l in open(os.path.join(OUT,"uncertainty_propagation.txt")).read().strip().split("\n"))
def _med(k): return float(_u[[x for x in _u if x.strip()==k][0]].split("%")[0])
def _q90(k): 
    t=_u[[x for x in _u if x.strip()==k][0]].split("90% ")[1].split(" |")[0].replace("%","").split("-"); return float(t[0]),float(t[1])
for _k,_m,_lo,_hi in [("Bitcoin, diversified holder (w=0)",14,12,16),("Ether, average crypto owner (kappa 0.7)",23,19,29),("Ether, diversified holder (w=0)",16,14,18),("Large altcoin, average crypto owner",22,18,29),("Large altcoin, diversified holder (w=0)",16,13,18),("Small coin, diversified holder (w=0)",25,20,30)]:
    chk(f"S6 required {_k}",_med(_k),_m,0.6); chk(f"S6 required {_k} 5%",_q90(_k)[0],_lo,0.6); chk(f"S6 required {_k} 95%",_q90(_k)[1],_hi,0.6)
# Section 6: the holder weight w = crypto share x kappa, and the term-by-term sums of Table 6 (cross_section_terms.txt)
_k6_W=_cs["W"].loc["2026-04-30"]; chk("S6 index April 2026: Bitcoin",100*_k6_W["btc"],73,0.5); chk("S6 index April 2026: Ether",100*_k6_W["eth"],14,0.5); chk("S6 index April 2026: other coins",100*(1-_k6_W["btc"]-_k6_W["eth"]),13,0.5)
_k6_b=_st("btc"); _k6_e=_st("eth"); _k6_vm=float(np.log1p(_cs["rcm"][:"2026-04-30"]).iloc[-48:].std()*12**.5)
chk("S6 crypto market volatility, four years",100*_k6_vm,57,0.5); chk("S6 Ether volatility, four years",100*_k6_e["vol"],74,0.5); chk("S6 Ether correlation with the market",_k6_e["corr_m"],0.91,0.005)
chk("S6 kappa = correlation x market volatility / asset volatility, Ether",_k6_e["corr_m"]*_k6_vm/_k6_e["vol"],_k6_e["kappa"],0.005); chk("S6 kappa identity, Bitcoin",_k6_b["corr_m"]*_k6_vm/_k6_b["vol"],_k6_b["kappa"],0.005)
chk("S6 market moves 7% when Ether moves 10%",10*_k6_e["kappa"],7,0.05); chk("S6 altcoin median correlation",_S.corr_m.median(),0.74,0.005); chk("S6 altcoin median volatility, four years",100*_S.vol.median(),86,0.5)
for _k6_n,_k6_k,_k6_lo,_k6_hi in (("Ether",0.7,5,13),("large altcoin",0.47,3,9)): chk(f"S6 weight {_k6_n}: low",7*_k6_k,_k6_lo,0.5); chk(f"S6 weight {_k6_n}: high",19*_k6_k,_k6_hi,0.5)
chk("S6 Ether weight at the midpoint",13*0.7,9.1,0.001); chk("S6 Ether concentration term as printed",100*1.9*0.64**2*0.091,7.1,0.05)
for _k6_n,_k6_s,_k6_be,_k6_k,_k6_m,_k6_t in (("Bitcoin",0.42,1.75,1.0,1.9,(7.0,1.9,14,4.4,18.3)),("Ether",0.64,2.35,0.7,1.9,(9.4,1.9,16,7.1,23.4)),("large altcoin",0.76,2.15,0.47,2.0,(8.6,2.0,16,6.7,22.3)),("small coin",None,2.15,None,11.45,(8.6,11.45,25,None,None))):
    _k6_fl=5.0+4*_k6_be+_k6_m; chk(f"Table 6 {_k6_n}: market term",4*_k6_be,_k6_t[0],0.001); chk(f"Table 6 {_k6_n}: mortality term",_k6_m,_k6_t[1],0.051); chk(f"Table 6 {_k6_n}: floor",_k6_fl,_k6_t[2],0.5)
    if _k6_k is not None: _k6_c=100*1.9*_k6_s**2*0.13*_k6_k; chk(f"Table 6 {_k6_n}: concentration term",_k6_c,_k6_t[3],0.05); chk(f"Table 6 {_k6_n}: sum of the terms",_k6_fl+_k6_c,_k6_t[4],0.05)
chk("Table 6 mortality midpoints: top-twenty",(0.3+3.5)/2,1.9,0.001); chk("Table 6 mortality midpoints: small coin",(6.7+16.2)/2,11.5,0.051)
for _k6_n,_k6_key,_k6_sum in (("Bitcoin","Bitcoin",18.3),("Ether","Ether, average crypto owner (kappa 0.7)",23.4),("large altcoin","Large altcoin, average crypto owner",22.3)): chk(f"Table 6 {_k6_n}: median within 0.4 of the sum of the terms",float(abs(_k6_sum-_med(_k6_key))<=0.4001),1,0)
_k6_o=open(os.path.join(OUT,"cross_section_terms.txt")).read().splitlines()
for _k6_n,_k6_v in (("Bitcoin",18.3),("Ether",23.4),("Large altcoin",22.3)): chk(f"Table 6 against the script output: {_k6_n} sum",float([l for l in _k6_o if l.startswith(_k6_n)][0].split()[-1]),_k6_v,0.001)
_k6_ep=pd.read_csv(os.path.join(CSV,"eth.csv"),parse_dates=["time"],usecols=["time","PriceUSD"]).set_index("time")["PriceUSD"].dropna().resample("ME").last(); _k6_es=np.sqrt(np.log(_k6_ep).diff().pow(2).ewm(halflife=9).mean()*12); _k6_bs=np.sqrt(sig2)
for _k6_d,_k6_ve,_k6_vb in (("2017-12-31",172,98),("2021-09-30",99,77),("2026-05-31",64,42)): chk(f"S6 Ether volatility {_k6_d[:7]}",100*_k6_es[:_k6_d].iloc[-1],_k6_ve,0.5); chk(f"S6 Bitcoin volatility {_k6_d[:7]}",100*_k6_bs[:_k6_d].iloc[-1],_k6_vb,0.5)
chk("S6 priced cryptoassets with a capitalization",int(_cs["C"].notna().any().sum()),77,0); chk("S6 Bitcoin: w_i = kappa x w leaves the weight unchanged",round(float(_st("btc")["kappa"]),1),1.0,0.001); chk("S6 Ether months since 2018",_dl(_Rn["eth"])[3],100,0)
_fg_l=[l for l in open(os.path.join(OUT,"monthly_test.txt")).read().splitlines() if l.startswith("2012–14")][0].split("|")[1].split(); _fg_g=float(_fg_l[2]); _fg_s=float(_fg_l[3].strip("(;"))
chk("Figure 3: 2012-14 two-standard-error interval, lower end as annotated",_fg_g-2*_fg_s,-234,1.5); chk("Figure 3: 2012-14 two-standard-error interval, upper end as annotated",_fg_g+2*_fg_s,442,1.5)
chk("S7 hurdle at the central mortality term, about 14%",5+7+1.9,14,0.15); chk("S7 rent at the middle, about 4 points",18.1-13.9,4,0.25); chk("S7 Black-Litterman: full confidence",100*(18.1-13.9)/(3*0.42**2*100),8,0.5); chk("S7 Black-Litterman: half confidence, about 4%",0.5*100*(18.1-13.9)/(3*0.42**2*100),4,0.5)
for _sp_d,_sp_v,_sp_g in (("2013-06-30",6.5,137),("2021-09-30",5.5,23),("2026-05-31",8.5,10)): chk(f"S5 S&P 500 required return {_sp_d[:7]}",100*float((rf+0.04)[:_sp_d].iloc[-1]),_sp_v,0.06); chk(f"S5 gap of the Bitcoin midpoint to the S&P 500 required return {_sp_d[:7]}",100*float((req_mid-rf-0.04)[:_sp_d].iloc[-1]),_sp_g,0.6)
_al={l.split()[1].rstrip(","):l for l in open(os.path.join(OUT,"monthly_test.txt")).read().splitlines() if l.startswith("alpha ")}
def _alp(k):
    c,m_=_al[k].split("|"); f=lambda z: (float(z.split("(")[0].split()[-1]),float(z.split(";")[1]))
    return f(c),f(m_)
for _ak,_av in (("2012–26",((90,2.3),(34,0.9))),("2018–26",((24,1.1),(2,0.1))),("2012–14",((185,None),(24,None))),("2015–17",((141,3.0),(91,None))),("2018–20",((53,None),(23,None))),("2021–23",((10,None),(-10,None))),("2024–26",((-1,None),(-12,None)))):
    for _an,_ao,_ap in zip(("CAPM","MCM"),_alp(_ak),_av):
        chk(f"S5 {_an} alpha {_ak}",_ao[0],_ap[0],0.5)
        if _ap[1] is not None: chk(f"S5 {_an} alpha {_ak}, t",_ao[1],_ap[1],0.05)
_cu={l.split(",")[0].split()[-1]:l for l in open(os.path.join(OUT,"monthly_test.txt")).read().splitlines() if l.startswith("cumulative unexplained return")}
for _ck,_cv in (("2012-2026",(1304,500)),("2018-2026",(198,21))):
    _cz=_cu[_ck].split("points:")[1].split(";")[0]; chk(f"S5 cumulative unexplained return {_ck}: CAPM",float(_cz.split("CAPM")[1].split(",")[0]),_cv[0],0.5); chk(f"S5 cumulative unexplained return {_ck}: MCM",float(_cz.split("MCM")[1]),_cv[1],0.5)
_ah=[l for l in open(os.path.join(OUT,"adoption_hazard.txt")).read().splitlines() if l.startswith("$")]
for _ahl,_ahv in zip(_ah,((29,17,22,12),(23,13,18,10),(13,7,8,4),(5,2,4,2),(3,2,4,2))):
    _ahp=[float(x_.rstrip("%")) for x_ in _ahl.replace("|"," ").split() if x_.endswith("%")]
    for _ahn,_aho,_ahe in zip(("dead in 2y","rate","not fading: dead in 2y","not fading: rate"),_ahp,_ahv): chk(f"C.2 adoption table, {_ahl[:26].strip()}: {_ahn}",_aho,_ahe,0.01)
_ahm=[int(l.replace("|"," ").split("%")[0].split()[-2]) for l in _ah]; chk("C.2 adoption table: asset-months",sum(_ahm),33055,0); chk("S3 under $1m a day: one in four dead within two years",(_ahm[0]*29+_ahm[1]*24)/(_ahm[0]+_ahm[1]),25,1.0)
_ahb=open(os.path.join(OUT,"adoption_hazard.txt")).read().split("Bitcoin,")[1]; 
for _ahy,_ahx in ((2011,0.11),(2013,4.40),(2014,23.26),(2017,235.93)): chk(f"C.2 Bitcoin's daily volume mid-{_ahy}, $m",float(_ahb.split(f"{_ahy}: $")[1].split("m")[0].replace(",","")),_ahx,0.01)
_tr={l.split(" to ")[1].split(":")[0]:l for l in open(os.path.join(OUT,"monthly_test.txt")).read().splitlines() if l.startswith("trailing three-year")}
for _tk,_tv in (("2017-12-31",(129,80)),("2020-12-31",(55,25)),("2026-04-30",(6,-6))):
     _tz=_tr[_tk].split(";")[0]; chk(f"S5 trailing three-year unexplained return {_tk}: CAPM",float(_tz.split("CAPM")[1].split(",")[0]),_tv[0],0.5); chk(f"S5 trailing three-year unexplained return {_tk}: MCM",float(_tz.split("MCM")[1]),_tv[1],0.5)
_shl={l.split("explained, ")[1].split(":")[0]:l for l in open(os.path.join(OUT,"monthly_test.txt")).read().splitlines() if l.startswith("share of Bitcoin")}
for _sk,_sv in (("whole sample",(21,70)),("since 2018",(45,94))): chk(f"S5 share explained, {_sk}: CAPM",float(_shl[_sk].split("CAPM ")[1].split("%")[0]),_sv[0],0.5); chk(f"S5 share explained, {_sk}: MCM",float(_shl[_sk].split("MCM ")[1].split("%")[0]),_sv[1],0.5)
_shp={l.split()[2].rstrip(":"):l for l in open(os.path.join(OUT,"monthly_test.txt")).read().splitlines() if l.startswith("share explained ")}
for _sk,_sv in (("2012–14",(13,71)),("2015–17",(18,49)),("2018–20",(18,63)),("2021–23",(57,131)),("2024–26",(104,138))): chk(f"D.2 share explained {_sk}: CAPM",float(_shp[_sk].split("CAPM ")[1].split("%")[0]),_sv[0],0.5); chk(f"D.2 share explained {_sk}: MCM",float(_shp[_sk].split("MCM ")[1].split("%")[0]),_sv[1],0.5)
_shD=pd.DataFrame({"r":px.shift(-1)/px-1}); _shD["rf"]=np.exp(rf/12)-1; _shD["ex"]=_shD.r-_shD.rf
# Sharpe decomposition, rebalanced example, net-of-death figures, compound at 55% volatility
chk("RV Sharpe units: market term 7/42",7/42,0.17,0.005); chk("RV Sharpe units: sum",7/42+1.9*0.42*0.13+1.9/42,0.32,0.005); chk("RV Sharpe units: diluted",7/42+1.9/42,0.21,0.005)
_rvv=((0.95*0.141)**2+(0.05*0.42)**2+2*0.95*0.05*1.75*0.141**2)**0.5
chk("RV rebalanced 5%: return added",0.05*(18.1-9.0),0.46,0.006); chk("RV rebalanced 5%: portfolio volatility",100*_rvv,14.7,0.05); chk("RV rebalanced 5%: extra drag",100*(_rvv**2-0.141**2)/2,0.09,0.005)
chk("RV net of death: Bitcoin average",18.1-1.9,16.2,0.001); chk("RV net of death: Bitcoin compound",9.3-1.9,7.4,0.001); chk("RV net of death: Ether average",23.0-1.9,21.1,0.001); chk("RV net of death: Ether compound",2.5-1.9,0.6,0.001)
_rv55=5+7+1.9+1.9*0.13*0.55**2*100; chk("RV at 55% volatility: average",_rv55,21,0.5); chk("RV at 55% volatility: compound",_rv55-0.55**2*50,6,0.5)
chk("RV double count: w times beta times ERP, about one point",0.13*7,1,0.1); chk("RV put: cost per year of protection",0.86*12/7.4,1.4,0.05)
chk("Table 7 Ether average",_med("Ether, average crypto owner (kappa 0.7)"),23.0,0.05)

# Appendix A.6, third approximation (39_index_exposure.py)
_ix=0.42**2/0.141**2; _ixw=(0.05+0.10+0.07)/100
chk("A.6 variance ratio BTC to index",_ix,9,0.2); chk("A.6 exposed constituents, % of index",100*_ixw,0.2,0.03); chk("A.6 addition to beta",_ixw*_ix,0.02,0.004); chk("A.6 addition to required return under 0.1",float(100*_ixw*_ix*0.04<0.1),1,0)
chk("A.6 addition to beta at x=1%",0.01*_ix,0.09,0.004); chk("A.6 points at x=1% below 0.4",float(100*0.01*_ix*0.04<0.4),1,0); chk("A.6 x=1% is more than four times the weight",float(0.01/_ixw>4),1,0); chk("A.6 Tesla bitcoin under $1bn",11509*73477.85/1e9,0.85,0.01)

# Appendix A.1: beta against a global index (appended to 34_beta_windows.py)
_acw=pd.DataFrame({"b":np.log(px).diff(),"s":_pxm(os.path.join(DATA,"acwi_monthly.csv")),"v":_pxm(os.path.join(DATA,"voo_monthly.csv"))}).dropna()[:"2026-05"]
def _acwb(x): return np.cov(x.b,x.s)[0,1]/x.s.var()
chk("A.1 beta on ACWI, last 4y",_acwb(_acw.iloc[-48:]),1.6,0.05); chk("A.1 beta on ACWI, last 5y",_acwb(_acw.iloc[-60:]),1.7,0.05); chk("A.1 beta on ACWI, since 2020",_acwb(_acw["2020":]),1.9,0.05); chk("A.1 corr ACWI and S&P 500",_acw["2012":].s.corr(_acw["2012":].v),0.97,0.006)

# Appendix C.3: hand-entered collapse dates moved to either end of the documented windows (40_death_date_check.py)
_ddc=open(os.path.join(OUT,"death_date_check.txt")).read()
chk("C.3 date variants identical to baseline",_ddc.count("apart from the three dates: True"),3,0); chk("C.3 FTT fall on 8 Nov 2022, %",100*(1-5.547440/22.042748),75,0.6)

# Section 3 and Appendix D.1: the mortality range (0.3 to 3.5) and its readings taken alone (appended runs of 23_uncertainty.py)
_u3=dict(l.split(" median ") for l in open(os.path.join(OUT,"uncertainty_propagation.txt")).read().strip().split("\n"))
for _kk,_mm,_l5,_h5 in (("Bitcoin, mortality 0.3-2.4 (2025 deaths set aside)",17.5,14.9,21.1),("Bitcoin, mortality fixed at 3.5 (high reading)",19.6,17.3,23.2),("Bitcoin, mortality fixed at 0.3 (low reading)",16.4,14.1,20.0)):
    _vv=[v for k,v in _u3.items() if k.strip()==_kk][0]; _rr=_vv.split("90% ")[1].split(" |")[0].replace("%","").split("-")
    chk(f"D.1 {_kk} median",float(_vv.split("%")[0]),_mm,0.05); chk(f"D.1 {_kk} 5%",float(_rr[0]),_l5,0.05); chk(f"D.1 {_kk} 95%",float(_rr[1]),_h5,0.05)
chk("S3 midpoint of the mortality range",(0.3+3.5)/2,1.9,0.001)

# Appendix A.7 (41_volatility_table.py) and Appendix E.1: volatility by window and currency; gold's beta
with contextlib.redirect_stdout(io.StringIO()): _vt=runpy.run_path(os.path.join(SCRIPTS,"41_volatility_table.py"))
_vtU=_vt["table"](_vt["D"]); _vtE=_vt["table"](_vt["D"].sub(_vt["fx"].reindex(_vt["D"].index),axis=0))
_vtP={"Global equities (ACWI)":(13.8,14.9,12.2,12.7,14.5),"S&P 500":(14.1,15.7,12.9,13.1,15.1),"Nasdaq-100":(17.2,20.4,16.4,18.7,20.1),"Russell 2000":(19.1,20.5,20.0,14.5,19.8),"Gold":(15.5,15.8,16.2,22.0,21.6),"Bitcoin":(86.9,57.9,45.2,34.7,43.4),"Ether":(111.6,73.0,63.9,71.4,66.2)}
for _vk,_vv in _vtP.items():
    for _vi,_vx in enumerate(_vv): chk(f"A.7 vol USD {_vk} col {_vi+1}",_vtU.loc[_vk].iloc[_vi],_vx,0.051)
for _vk,_vv in {"Global equities (ACWI)":(12.6,13.0,11.2,9.9,12.9),"S&P 500":(13.8,14.7,13.0,11.1,14.4)}.items():
    for _vi,_vx in enumerate(_vv): chk(f"A.7 vol EUR {_vk} col {_vi+1}",_vtE.loc[_vk].iloc[_vi],_vx,0.051)
_vd=_vtU["recent months weighted"]-_vtU["2012-01 to 2026-04"]; _ve=_vd.iloc[:4]
chk("A.7 recent basis: equities more volatile, min",_ve.min(),0.7,0.06); chk("A.7 equities more volatile, max",_ve.max(),2.9,0.06); chk("A.7 gold more volatile",_vd["Gold"],6.1,0.06)
_vc=[(_vtU["recent months weighted"][k]**2-_vtU["2012-01 to 2026-04"][k]**2)/200 for k in list(_vtP)[:5]]
chk("A.7 compound lower, equities min",min(_vc[:4]),0.1,0.05); chk("A.7 compound lower, equities max",max(_vc[:4]),0.5,0.05); chk("A.7 compound lower, gold",_vc[4],1.1,0.05)
_vn=[m-_vtU["recent months weighted"][k]**2/200 for k,m in zip(list(_vtP)[:4],(8.8,9.0,9.5,9.7))]
chk("A.7 equity compound on recent basis, min",min(_vn),7.5,0.05); chk("A.7 equity compound on recent basis, max",max(_vn),7.9,0.05)
_vg=(_vtU-_vtU.loc["Global equities (ACWI)"]).loc["S&P 500"]; _vh=(_vtE-_vtE.loc["Global equities (ACWI)"]).loc["S&P 500"]
chk("A.7 USD gap S&P less ACWI, min",_vg.min(),0.3,0.11); chk("A.7 USD gap, max",_vg.max(),0.8,0.11); chk("A.7 EUR gap, min",_vh.min(),1.2,0.11); chk("A.7 EUR gap, max",_vh.max(),1.8,0.11)
_vX=_vt["D"]["2012-01":"2026-04"]; chk("A.7 corr euro change, ACWI",_vX.iloc[:,0].corr(_vt["fx"]),0.4,0.05); chk("A.7 corr euro change, S&P",_vX.iloc[:,1].corr(_vt["fx"]),0.3,0.05)
chk("A.7 Ether recent-weighted May 2026",100*np.sqrt(_vt["D"]["Ether"][:"2026-05"].pow(2).ewm(halflife=9).mean().iloc[-1]*12),64.0,0.05); chk("A.7 BTC recent-weighted May 2026",100*np.sqrt(_vt["D"]["Bitcoin"][:"2026-05"].pow(2).ewm(halflife=9).mean().iloc[-1]*12),41.8,0.05)
def _gb(x):
    g=x[["Gold","S&P 500"]].dropna(); return g.cov().iloc[0,1]/g["S&P 500"].var()
chk("E.1 gold beta 2012-26",_gb(_vX),0.10,0.006); chk("E.1 gold beta since 2020",_gb(_vX["2020":]),0.17,0.006); chk("E.1 beta 0.1 adds 0.4 points",0.1*4,0.4,0.001); chk("E.1 jewelry plus reserves share",44+18,62,0.5)

# Appendix A.7: the rest of the world backed out of the global index, in dollars and in euros
_vS=np.expm1(_vX[["Global equities (ACWI)","S&P 500"]]); _vf=np.expm1(_vt["fx"].reindex(_vX.index)); _vr=(_vS.iloc[:,0]-0.6*_vS.iloc[:,1])/0.4
chk("A.7 rest of world vol in dollars",100*_vr.std()*12**.5,15,0.5); chk("A.7 rest of world vol in euros",100*((1+_vr)/(1+_vf)-1).std()*12**.5,13,0.5)

# Appendix A.7: the dollar and equity downturns
_vb=_vS.iloc[:,1]<-0.05; _v25=_vS.iloc[:,1]["2025":].corr(_vf["2025":])
chk("A.7 months with S&P below -5%",int(_vb.sum()),14,0); chk("A.7 euro down in those months",int((_vf[_vb]<0).sum()),8,0); chk("A.7 mean euro change in those months",100*_vf[_vb].mean(),-1.0,0.05)
chk("A.7 corr since 2025 about zero",_v25,0.0,0.06); chk("A.7 months since 2025",len(_vS["2025":]),16,0); chk("A.7 March 2025: S&P down, euro up",float(_vS.iloc[:,1]["2025-03"].iloc[0]<0 and _vf["2025-03"].iloc[0]>0),1,0)

# Appendix D.2: the band's upper-edge formula carries the high end of the mortality range (3.5 points)
import re as _re2
chk("D.2 upper-edge mortality constant, points",100*float(_re2.search(r"G_HI\*sig2\*w_hi\+([0-9.]+)",open(os.path.join(SCRIPTS,"22_pretty_figs.py")).read()).group(1)),3.5,0.001)

# Table 3: how the 8% lower end of the holder weight is built
chk("T3 Bitcoin capitalization, $tn",cap.reindex(px.index).iloc[-1]/1e12,1.5,0.05); chk("T3 surveyed owners' wealth, $tn",Wp.iloc[-1]/1e12,8,0.5); chk("T3 fund and treasury investors' wealth at 1.5%, $tn",inst_val.iloc[-1]/0.015/1e12,13,0.5)
chk("T3 combined weight, %",100*cap.reindex(px.index).iloc[-1]/(Wp.iloc[-1]+inst_val.iloc[-1]/0.015),7,0.5)

# Section 5 and Appendix A.7: the volatility weights
chk("A.7 weight of the latest 9 months, %",100*(1-0.5**(9/9)),50,0.01); chk("A.7 weight of the latest 18 months, %",100*(1-0.5**(18/9)),75,0.01); chk("A.7 weight of the latest 3 years, %",100*(1-0.5**(36/9)),94,0.3)
_lw=np.log(px).diff().dropna(); _ww=0.5**(np.arange(len(_lw))[::-1]/9); chk("A.7 formula reproduces the script's volatility, May 2026 (%)",100*np.sqrt(12*(_ww*_lw.values**2).sum()/_ww.sum()),100*np.sqrt(sig2.iloc[-1]),0.01)

# Table 4: the band worked out at five dates (script 43_band_table.py)
_bt_early=rf+seg*sig2
_BT={"2013-06-30":(2.5,151,3.00,19,19,100,56,142,231,231,144),"2017-06-30":(2.3,80,2.15,17,19,100,21,50,67,67,44),"2019-06-30":(2.0,90,0.70,16,19,51,18,51,43,51,35),
     "2021-09-30":(1.5,77,1.30,12,19,11,14,43,8,43,28),"2026-05-31":(4.5,42,1.75,7,19,10,12,25,6,25,19)}
for _bd,(_b1,_b2,_b3,_b4,_b5,_b6,_b7,_b8,_b9,_b10,_b11) in _BT.items():
    _bi=at(_bd); _by=_bd[:7]
    chk(f"T4 {_by} risk-free rate",100*rf.iloc[_bi],_b1,0.051); chk(f"T4 {_by} volatility",100*sig.iloc[_bi],_b2,0.5); chk(f"T4 {_by} beta",beta_roll.iloc[_bi],_b3,0.005)
    chk(f"T4 {_by} average owner's weight, low",100*w_lo.iloc[_bi],_b4,0.5); chk(f"T4 {_by} average owner's weight, high",100*w_hi.iloc[_bi],_b5,0.5); chk(f"T4 {_by} early holder's weight",100*seg.iloc[_bi],_b6,0.5)
    chk(f"T4 {_by} lower edge",100*foc_lo.iloc[_bi],_b7,0.5); chk(f"T4 {_by} upper (a)",100*foc_hi.iloc[_bi],_b8,0.5); chk(f"T4 {_by} upper (b)",100*_bt_early.iloc[_bi],_b9,0.5)
    chk(f"T4 {_by} upper edge is the larger",100*req_hi.iloc[_bi],_b10,0.5); chk(f"T4 {_by} midpoint",100*req_mid.iloc[_bi],_b11,0.5)
    chk(f"T4 {_by} lower edge from its formula",100*(rf.iloc[_bi]+0.85*beta_roll.iloc[_bi]*0.04+sig2.iloc[_bi]*w_lo.iloc[_bi]+0.003),100*foc_lo.iloc[_bi],0.01)
    chk(f"T4 {_by} upper (a) from its formula",100*(rf.iloc[_bi]+1.15*beta_roll.iloc[_bi]*0.04+2.8*sig2.iloc[_bi]*w_hi.iloc[_bi]+0.035),100*foc_hi.iloc[_bi],0.01)
chk("T4 market term moves 15% either way: 1.5/1.75",1.5/1.75,0.85,0.01); chk("T4 market term moves 15% either way: 2.0/1.75",2.0/1.75,1.15,0.01)
chk("Reading 1: weight 2026 with fund and treasury investors",100*w_lo.iloc[-1],7,0.5); chk("Reading 1: weight 2026 without",100*w_hi.iloc[-1],19,0.001)

# Appendix A.3: when the co-movement with equities appeared (script 34_beta_windows.py)
def _cm(x):
    _b=np.cov(x.b,x.s)[0,1]/x.s.var(); _e=x.b-x.b.mean()-_b*(x.s-x.s.mean()); return _b,np.sqrt(_e.var(ddof=2)/((x.s-x.s.mean())**2).sum()),x.b.corr(x.s)
chk("A.3 correlation 2012-19",_cm(_d["2012":"2019"])[2],0.16,0.005); chk("A.3 correlation 2016-19",_cm(_d["2016":"2019"])[2],0.00,0.005)
chk("A.3 correlation 2020-23",_cm(_d["2020":"2023"])[2],0.56,0.005); chk("A.3 correlation 2024 to May 2026",_cm(_d["2024":])[2],0.49,0.005)
chk("A.3 beta 2020-23",_cm(_d["2020":"2023"])[0],2.0,0.05); chk("A.3 beta s.e. 2020-23",_cm(_d["2020":"2023"])[1],0.4,0.05); chk("A.3 beta 2024 to May 2026",_cm(_d["2024":])[0],1.8,0.05); chk("A.3 beta s.e. 2024 to May 2026",_cm(_d["2024":])[1],0.6,0.05)
_cm12=_d.b.rolling(12).corr(_d.s); chk("A.3 twelve-month correlation, end of 2019",_cm12.loc["2019-12-31"],-0.4,0.05); chk("A.3 twelve-month correlation, end of 2020",_cm12.loc["2020-12-31"],0.7,0.05)
chk("intro: correlation before 2020 about 0.2",_cm(_d["2012":"2019"])[2],0.2,0.05); chk("intro: correlation since 2020 about 0.5",_cm(_d["2020":])[2],0.5,0.05)
chk("A.3 ownership 2018 survey, %",100*q.iloc[at("2018-06-30")],1.2,0.05); chk("A.3 ownership 2021Q3, %",100*q.iloc[at("2021-09-30")],11,0.05)
chk("A.3 gold: jewelry plus central-bank reserves, % of stock",44+18,62,0)
# Section 5, equation (3) and Appendix B.3: the documented fund and treasury series
_gb={"2013-12-31":0.070,"2014-12-31":0.135,"2015-12-31":0.141,"2016-12-31":0.172,"2017-12-31":0.176,"2018-12-31":0.204,"2019-12-31":0.261,"2020-12-31":0.607,"2021-12-31":0.645,"2022-12-31":0.632,"2023-12-31":0.620}
_pc={"2019-12-31":0.020,"2020-12-31":0.096,"2021-12-31":0.216,"2022-12-31":0.225,"2023-12-31":0.281}
for _dd,_vv in _gb.items(): chk(f"B.3 Grayscale trust plus public companies, {_dd[:4]} year-end, million BTC",inst_btc.iloc[at(_dd)]/1e6,_vv+_pc.get(_dd,0.0),0.001)
chk("B.3 public companies 2022: MicroStrategy 132,500 plus others at 2021 level",0.1325+0.092,0.225,0.001); chk("B.3 public companies 2023: MicroStrategy 189,150 plus others",0.18915+0.092,0.281,0.001); chk("B.3 others at 2021 level: 0.216 less MicroStrategy's 124,391",0.216-0.124391,0.092,0.001)
chk("B.3 holdings zero before the trust (September 2013)",inst_btc.iloc[at("2013-09-30")],0,1); chk("B.2 trust year-end range 2014-19 lo",0.135,0.13,0.006); chk("B.2 trust year-end range 2014-19 hi",0.261,0.26,0.006); chk("B.2 trust range 2020-23 lo",0.607,0.61,0.006); chk("B.2 trust range 2020-23 hi",0.645,0.64,0.006)
for _yy,_vv in ((2024,1.15),(2025,2.1)): chk(f"B.3 fund and treasury holdings mid-{_yy}, million BTC",inst_btc.iloc[at(f"{_yy}-06-30")]/1e6,_vv,0.005)
chk("B.3 fund and treasury holdings 2026, million BTC",inst_btc.iloc[-1]/1e6,2.5,0.05)
chk("eq 3: band mid-2017 low",100*w_lo.iloc[at("2017-06-30")],17,0.5); chk("eq 3: band mid-2019 low",100*w_lo.iloc[at("2019-06-30")],16,0.5); chk("eq 3: band mid-2019 high",100*w_hi.iloc[at("2019-06-30")],19,0.001)
chk("eq 3: band 2021Q3 low",100*w_lo.iloc[at("2021-09-30")],12,0.5); chk("eq 3: band 2021Q3 high",100*w_hi.iloc[at("2021-09-30")],19,0.5); chk("eq 3: weight 2013, both ends",100*w_lo.iloc[at("2013-06-30")],19,0.001); chk("eq 3: weight 2017",100*w_hi.iloc[at("2017-06-30")],19,0.001)
chk("D.4 wealth per owner 2012",float(_ramp.iloc[at("2012-06-30")]),0.25,0.005); chk("D.4 wealth per owner 2026",float(_ramp.iloc[-1]),1.4,0.01)

# Appendix A.3, "A test on holdings" (script 44_holders_and_comovement.py) and the sensitivity of Appendix B.3
_hc_sply=pd.read_csv(os.path.join(CSV,"btc.csv"),usecols=["time","SplyCur"],parse_dates=["time"]).set_index("time")["SplyCur"]; _hc_sply.index=_hc_sply.index.tz_localize(None) if _hc_sply.index.tz is not None else _hc_sply.index
_hc_sply=_hc_sply.resample("ME").last().reindex(px.index).ffill()
def _hc_path(an):
    _dd=pd.Series({pd.Timestamp(k):v for k,v in an.items()}).sort_index()
    return pd.Series(np.interp(px.index.astype("int64").values.astype(float),_dd.index.astype("int64").values.astype(float),_dd.values,left=0.0),index=px.index)
_hc_f=dict(_GBTC); _hc_f.update({"2024-01-11":0.62,"2024-07-22":0.90,"2024-12-31":1.13,"2025-06-28":1.24,"2026-06-01":1.29})
_hc_p=dict(_PUBCO); _hc_p.update({"2024-09-30":0.33,"2024-12-31":0.58,"2025-05-31":0.67,"2025-09-30":1.00,"2025-12-31":1.10,"2026-04-19":1.13,"2026-09-21":1.27})
_hc_t=100*1e6*(_hc_path(_hc_f)+_hc_path(_hc_p))/_hc_sply
chk("A.3 share held, average 2014-19 (about 1%)",_hc_t["2014":"2019"].mean(),1.0,0.2); chk("A.3 share held, end of 2019",_hc_t.loc["2019-12-31"],1.5,0.06); chk("A.3 share held, end of 2020",_hc_t.loc["2020-12-31"],3.8,0.05)
chk("A.3 share held, minimum from end-2020 to end-2023",_hc_t["2020-12-31":"2023-12-31"].min(),3.8,0.05); chk("A.3 share held, maximum from end-2020 to end-2023",_hc_t["2020-12-31":"2023-12-31"].max(),4.6,0.05); chk("A.3 share held, May 2026",_hc_t.iloc[-1],12,0.5)
chk("A.3 correlation 2014-19",_cm(_d["2014":"2019"])[2],0.09,0.005); _hc_x=_d["2020":"2023"].drop(pd.Timestamp("2020-03-31")); chk("A.3 correlation 2020-23 without March 2020",_hc_x.b.corr(_hc_x.s),0.52,0.005)
chk("A.3 model series and chart series agree, May 2026 (million BTC)",(_hc_path(_hc_f)+_hc_path(_hc_p)).iloc[-1],inst_btc.iloc[-1]/1e6,0.1)
def _hc_run(sc):
    _I={d:_GBTC[d]+sc*_PUBCO.get(d,0.0) for d in _GBTC}; _I.update({"2024-06-30":1.15,"2025-06-30":2.1,"2026-06-30":2.5})
    _ib=pd.Series(np.interp(age,[(pd.Timestamp(d)-GEN).days/365.25 for d in _I],[1e6*v for v in _I.values()]),index=px.index)
    _wl=(cap.reindex(px.index)/(Wp+_ib*px/0.015)).clip(upper=0.9); _lo=rf+0.85*beta_term+G_LO*sig2*_wl+0.003; _mi=0.5*(_lo+req_hi)
    _DD=pd.DataFrame({"r":px.shift(-1)/px-1,"m":np.exp(_mi/12)-1}).dropna(); _DD=_DD[(_DD.index>="2012-01-01")&(_DD.index<="2026-04-30")]
    return 100*(_lo-foc_lo).abs().max(),1200*(_DD.r-_DD.m).mean(),1200*(_DD["2018":].r-_DD["2018":].m).mean()
_hc_b=_hc_run(1.0)
for _sc in (0.5,2.0):
    _hc_r=_hc_run(_sc); chk(f"B.3 public-company figures x{_sc}: lower edge moves by at most one point",float(_hc_r[0]<=1.0),1,0); chk(f"B.3 public-company figures x{_sc}: gaps move by at most 0.1",float(max(abs(_hc_r[1]-_hc_b[1]),abs(_hc_r[2]-_hc_b[2]))<=0.15),1,0)
chk("E.3 J.P. Morgan weights sum",65+30+5,100,0); chk("E.3 J.P. Morgan weighted base case",0.65*10.7+0.30*10.7+0.05*(-3.2),10.0,0.1)

# Appendix E.4: Table 7 for a euro investor (script 45_euro_table.py)
_eu_rf=3.4; chk("E.4 Bund yield, mean of 3.58, 3.34 and 3.3",(3.58+3.34+3.3)/3,_eu_rf,0.05); chk("E.4 interest differential",5.0-_eu_rf,1.6,0.001)
_eu_fx=np.log(pd.read_csv(os.path.join(DATA,"eurusd_monthly.csv"),parse_dates=["Date"]).sort_values("Date").set_index("Date")["Close"]).diff()
_eu_fx_me=_eu_fx.copy(); _eu_fx_me.index=_eu_fx_me.index+pd.offsets.MonthEnd(0)
_eu_R=pd.DataFrame({k:_lr(os.path.join(DATA,f"{f}_monthly.csv")) for k,f in (("ACWI","acwi"),("VOO","voo"),("QQQ","qqq"),("IWM","iwm"),("GLD","gld"))})["2012-01":"2026-04"]
_eu_E=_eu_R.sub(_eu_fx.reindex(_eu_R.index),axis=0)
_eu_v={"global":100*_eu_E.ACWI.std()*12**.5,"sp500":100*_eu_E.VOO.std()*12**.5,"nasdaq":100*_eu_E.QQQ.std()*12**.5,"russell":100*_eu_E.IWM.std()*12**.5,"gold":100*_eu_E.GLD.std()*12**.5,
       "btc":100*np.sqrt((np.log(px).diff()-_eu_fx_me.reindex(px.index))[:"2026-05"].pow(2).ewm(halflife=9).mean().iloc[-1]*12)}
_eu_out=open(os.path.join(OUT,"euro_table.txt")).read(); _eu_v["eth"]=float([l for l in _eu_out.splitlines() if l.startswith("volatility in euros, unrounded")][0].split("Ether ")[1].split()[0].rstrip(","))
_EU={"global":(3.8,7.2,12.6,0.8,6.4,0.30,0.24),"sp500":(4.0,7.4,13.8,1.0,6.4,0.29,0.22),"nasdaq":(4.48,7.9,16.9,1.4,6.5,0.27,0.18),"russell":(4.72,8.1,18.8,1.8,6.3,0.25,0.16),
     "gold":(0.5,3.9,14.5,1.1,2.8,0.03,-0.04),"btc":(13.1,16.5,42,8.8,7.7,0.31,0.10),"eth":(18.0,21.4,64,20.5,0.9,0.28,-0.04)}
for _k,(_pr,_mu,_sg,_dr,_cp,_sh,_sc) in _EU.items():
    chk(f"E.4 {_k}: average = 3.4 + premium",_eu_rf+_pr,_mu,0.051); chk(f"E.4 {_k}: volatility in euros",_eu_v[_k],_sg,0.05 if _k not in ("btc","eth") else 0.5)
    chk(f"E.4 {_k}: drag",_sg**2/200,_dr,0.051); chk(f"E.4 {_k}: compound",_mu-_sg**2/200,_cp,0.051); chk(f"E.4 {_k}: Sharpe",(_mu-_eu_rf)/_sg,_sh,0.0051); chk(f"E.4 {_k}: Sharpe on the compound return",(_mu-_sg**2/200-_eu_rf)/_sg,_sc,0.0051)
chk("E.4 volatility lower in euros, smallest gap",min(14.1-13.8,17.2-16.9,19.1-18.8),0.3,0.001); chk("E.4 volatility lower in euros, largest gap",13.8-12.6,1.2,0.001)
chk("E.4 euro volatility against the dollar",100*_eu_fx["2012-01":"2026-04"].std()*12**.5,7,0.5); chk("E.4 correlation of the euro's change with Bitcoin's return",(np.log(px).diff())["2012-01":"2026-04"].corr(_eu_fx_me),0.05,0.005)
for _k,_x in (("global",_eu_R.ACWI),("sp500",_eu_R.VOO),("nasdaq",_eu_R.QQQ),("russell",_eu_R.IWM),("gold",_eu_R.GLD)): chk(f"E.4 correlation of the euro's change with {_k} is between 0.2 and 0.4",float(0.195<=_x.corr(_eu_fx.reindex(_x.index))<=0.445),1,0)
chk("E.4 Bitcoin over global equities, compound, euros",7.7-6.4,1.3,0.001); chk("E.4 Bitcoin over global equities, compound, dollars",9.3-7.8,1.5,0.001); chk("E.4 volatility ratio above three, euros",float(42/12.6>3),1,0); chk("TNX file's November value is the 11 November download",_tn.loc["2026-11-01"],5.0,0.05)

_eu_bt=lambda c: float(_eu_E[c].cov(_eu_E.VOO)/_eu_E.VOO.var())
chk("E.4 note: beta of the global index in euros",_eu_bt("ACWI"),0.88,0.005); chk("E.4 note: beta of gold in euros",_eu_bt("GLD"),0.00,0.005); chk("E.4 note: Nasdaq-100 and Russell 2000 betas in euros within 0.03 of dollars",float(abs(_eu_bt("QQQ")-1.12)<=0.03 and abs(_eu_bt("IWM")-1.18)<=0.03),1,0)
_eu_bx=pd.DataFrame({"b":np.log(px).diff(),"s":_pxm(os.path.join(DATA,"voo_monthly.csv")),"f":_eu_fx_me}).dropna()["2022-05":"2026-04"]
chk("E.4 note: Bitcoin's four-year beta in euros within 0.03 of dollars",float(abs((_eu_bx.b-_eu_bx.f).cov(_eu_bx.s-_eu_bx.f)/(_eu_bx.s-_eu_bx.f).var()-_eu_bx.b.cov(_eu_bx.s)/_eu_bx.s.var())<=0.03),1,0)

# Appendix D.4, table of other paths for the holder weight; Appendix B, table of fund and company holdings
for _dd,_tt in (("2019-12-31",0.281),("2020-12-31",0.703),("2021-12-31",0.861),("2022-12-31",0.857),("2023-12-31",0.901)): chk(f"B table: total {_dd[:4]}",inst_btc.iloc[at(_dd)]/1e6,_tt,0.001)

# ---------- The holder weight held at its survey value: Section 4, Section 5, Appendix B.2, D.2, D.3 and D.4 ----------
# Surveys of holdings (script 49_holder_surveys.py, data/holder_surveys.csv)
_hw_r=px.shift(-1)/px-1; _hw_mo=lambda mu: np.exp(mu/12)-1
_hw_D=pd.DataFrame({"r":_hw_r,"lo":_hw_mo(foc_lo),"mid":_hw_mo(req_mid),"hi":_hw_mo(req_hi)}).dropna(); _hw_D=_hw_D[_hw_D.index>="2012-01-01"]
_hs=pd.read_csv(os.path.join(DATA,"holder_surveys.csv"),dtype={"price_from":str,"price_to":str}); _hs_p=btcf["PriceUSD"].dropna(); _hs["btc"]=[_hs_p[a_:b_].mean() for a_,b_ in zip(_hs.price_from,_hs.price_to)]
_uk=_hs[_hs.country=="UK"].reset_index(drop=True); _ca=_hs[_hs.country=="Canada"].reset_index(drop=True); _hs_sl=lambda y,x: np.polyfit(np.log(x),np.log(y),1)[0]
for _i,(_mn,_md,_ow) in enumerate(((1575,260,1.9),(1775,300,2.3),(1595,175.5,5.0),(1845,375.5,7.0))):
    chk(f"B.2 UK wave {_i+1}: mean holding",_uk.mean_holding[_i],_mn,0.5); chk(f"B.2 UK wave {_i+1}: median holding",_uk.median_holding[_i],_md,0.05); chk(f"B.2 UK wave {_i+1}: owners, million",_uk.owners_million[_i],_ow,0.05)
for _i,_v in ((1,4.8),(2,3.1),(3,8.3)): chk(f"B.2 UK wave {_i+1}: Bitcoin's price over its December 2019 level",_uk.btc[_i]/_uk.btc[0],_v,0.05)
chk("S4 UK: price rose eightfold between the first and the last wave",_uk.btc[3]/_uk.btc[0],8,0.5)
chk("B.2 UK: elasticity of the mean holding to the price",_hs_sl(_uk.mean_holding,_uk.btc),0.08,0.005); chk("B.2 UK: elasticity of the median holding to the price",_hs_sl(_uk.median_holding,_uk.btc),0.17,0.005)
_uk_t=_uk.owners_million*_uk.mean_holding; _uk_dn=np.log(_uk.owners_million[3]/_uk.owners_million[0]); _uk_dt=np.log(_uk_t[3]/_uk_t[0])
chk("B.2 UK: share of the growth that is more owners, %",100*_uk_dn/_uk_dt,89,0.5); chk("B.2 UK: share that is more per owner, %",100*(1-_uk_dn/_uk_dt),11,0.5)
for _i,_v in enumerate((500,250,503,500,500)): chk(f"B.2 Canada wave {_i+1}: median holding",_ca.median_holding[_i],_v,0.5)
chk("S4 Canada: about 500 in four of five waves",float((abs(_ca.median_holding-500)<=3).sum()),4,0); chk("S4 Canada: the price varied fifteenfold",_ca.btc.max()/_ca.btc.min(),15,0.5); chk("B.2 Canada: highest price over its 2018 level",_ca.btc.max()/_ca.btc[0],15,0.5)
chk("B.2 Canada: lowest price is that of 2018",float(_ca.btc.idxmin()==0),1,0); chk("B.2 Canada: elasticity of the median holding to the price",_hs_sl(_ca.median_holding,_ca.btc),0.11,0.005)
_hs_o=open(os.path.join(OUT,"holder_surveys.txt")).read()
chk("holder_surveys.txt: UK elasticity of the mean",float(_hs_o.split("elasticity of the mean holding to Bitcoin's price across the waves: ")[1].split()[0]),0.08,0.001); chk("holder_surveys.txt: Canada elasticity of the median",float(_hs_o.split("Canada:")[1].split("elasticity of the median holding to Bitcoin's price across the waves: ")[1].split()[0]),0.11,0.001)
_hs_g=_hs_p["2025-06"].mean()/_hs_p["2021-09"].mean(); chk("B.2 price, September 2021 to June 2025: times",_hs_g,2.3,0.05); chk("B.2 a 19% share held without trading becomes, %",100*0.19*_hs_g/(1+0.19*(_hs_g-1)),35,0.5)
chk("S4 median owner's share, interpolated between 5% (40% below) and 15% (70% below)",5+10*(50-40)/(70-40),8,0.5)
# Owners' wealth and the weights of equation (3)
chk("B.2 owners' wealth is capitalization over 0.19 at every date",float((Wp/cap.reindex(px.index)).dropna().sub(1/0.19).abs().max()),0,1e-9)
chk("S5 the weight with fund and treasury investors, 2021Q3",100*w_lo.iloc[at("2021-09-30")],12,0.5); chk("B.3 the same, mid-2019",100*w_lo.iloc[at("2019-06-30")],16,0.5)
# The early-holder era ended at the 2014 survey instead of the 2018 survey (Section 5, Appendix D.2)
assert src.count("Q_FEW=0.012")==1
_e14={"__file__":__file__}; _e14s=src.replace("Q_FEW=0.012","Q_FEW=0.004")
exec(_e14s.split("# ============ FIG 1")[0],_e14); exec(_e14s[_e14s.index("# ============ FIG 5"):_e14s.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")],_e14)
_e14D=pd.DataFrame({"r":_hw_r,"hi":_hw_mo(_e14["req_hi"]),"mid":_hw_mo(_e14["req_mid"])}).dropna(); _e14D=_e14D[_e14D.index>="2012-01-01"]
chk("S5 early era to 2014: upper edge 2015-17",1200*_e14D["2015":"2017"].hi.mean(),75,0.5); chk("S5 early era to 2014: upper edge 2018-20",1200*_e14D["2018":"2020"].hi.mean(),49,0.5)
chk("S5 baseline upper edge 2015-17",1200*_hw_D["2015":"2017"].hi.mean(),98,0.5); chk("S5 baseline upper edge 2018-20",1200*_hw_D["2018":"2020"].hi.mean(),57,0.5)
_x=_e14D["2015":"2017"]; _x=_x.r-_x.hi; chk("S5 early era to 2014: delivered over the upper edge 2015-17",1200*_x.mean(),85,0.5); chk("S5 early era to 2014: its t",_x.mean()/(_x.std(ddof=1)/np.sqrt(len(_x))),1.8,0.05)
chk("S5 baseline: delivered over the upper edge 2015-17",1200*(_hw_D["2015":"2017"].r-_hw_D["2015":"2017"].hi).mean(),62,0.5)
chk("S5 early era to 2014: nothing changes from 2021",float((_e14["req_hi"]-req_hi)["2021":].abs().max()),0,1e-12)
chk("D.2 early era to 2014: full-sample gap to the upper edge",1200*(_e14D.r-_e14D.hi).mean(),16,0.5); chk("D.2 baseline full-sample gap to the upper edge",1200*(_hw_D.r-_hw_D.hi).mean(),9,0.5)
# Appendix D.3: forward five-year log growth on sigma squared times the owners' weight
import statsmodels.api as _sm3
_lg5=np.log(px.shift(-60)/px)/5; _m5=(age>=3.0)&_lg5.notna()
_f5=_sm3.OLS(_lg5[_m5],_sm3.add_constant((sig2*w_hi)[_m5])).fit(); chk("D.3 coefficient on sigma^2 w",_f5.params.iloc[1],0.5,0.05); chk("D.3 its t",_f5.tvalues.iloc[1],3.1,0.05)
_f5c=_sm3.OLS(_lg5[_m5],_sm3.add_constant((sig2*wr.clip(upper=0.9))[_m5])).fit(); chk("D.3 coefficient with the weight that follows the market value",_f5c.params.iloc[1],-0.8,0.05); chk("D.3 its t, market-value weight",_f5c.tvalues.iloc[1],-6.9,0.05)
# Appendix D.4: the table of other choices (script 50_holder_weight_variants.py) and the rows of the uncertainty file
_v4=[b.splitlines() for b in open(os.path.join(OUT,"holder_weight_variants.txt")).read().strip().split("\n\n")]; _u4=open(os.path.join(OUT,"uncertainty_propagation.txt")).read()
_v4m=lambda key: float(_u4.split(key)[1].split("median")[1].split("%")[0])
def _v4row(b):
    g=lambda k: [l for l in b if l.strip().startswith(k)][0]
    w=g("May 2026 weights").split(":")[1].split("%")[0].split("-"); b13=g("2013-06").split("band")[1].split("%")[0].split("-"); b26=g("2026-05").split("band")[1].split("%")[0].split("-")
    return [float(w[0]),float(w[1]),float(b13[0]),float(b13[1]),float(b26[0]),float(b26[1]),float(g("2012-17").split("midpoint")[2].split("(")[0]),float(g("2018-26").split("midpoint")[2].split("(")[0]),float(g("2018-26").split("(se")[1].split(")")[0]),float(g("five-year").split("correlation")[1].split(";")[0]),float(g("2012-17").split("band")[1].split("-")[0])]
_V4=(("19%",0,(7,19,56,231,12,25,101,15,23,0.43),18.1,"Bitcoin  "),("12%",1,(6,12,40,231,12,22,107,21,23,0.44),16.9,"Bitcoin, w 0.06-0.12"),("8%",2,(5,8,31,231,12,20,111,23,24,0.44),16.1,"Bitcoin, w 0.05-0.08"),
     ("market value",3,(8,23,21,231,12,27,109,15,24,0.28),18.3,"Bitcoin, w 0.08-0.19"),("ownership 3%",4,(7,19,56,231,12,25,101,15,23,0.43),18.1,"Bitcoin  "))
for _n,_i,_e,_rq,_key in _V4:
    _c=_v4row(_v4[_i])
    for _lab,_cc,_ee,_tt in zip(("w low","w high","band 2013 low","band 2013 high","band 2026 low","band 2026 high","gap 2012-17","gap 2018-26","se 2018-26","five-year correlation"),_c,_e,(0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.005)): chk(f"D.4 table, {_n}: {_lab}",_cc,_ee,_tt)
    chk(f"D.4 table, {_n}: required return 2026",_v4m(_key),_rq,0.05)
chk("D.4 lower edge 2012-17 at a weight of 19%",_v4row(_v4[0])[10],44,0.5); chk("D.4 lower edge 2012-17 at a weight of 8%",_v4row(_v4[2])[10],25,0.5); chk("D.4 standard error of the gap 2012-17",1200*(_hw_D["2012":"2017"].r-_hw_D["2012":"2017"].mid).std(ddof=1)/np.sqrt(72),87,0.5)
chk("D.4 table, baseline row equals the paper's Table 5 gap since 2018",_v4row(_v4[0])[7],round(1200*(_hw_D["2018":].r-_hw_D["2018":].mid).mean()),0.5)


# Appendix C.3: the migrations named in the paper (17 + 6 + 27 = 50), and Section 6: an asset's slice of the market is not its weight
_mg=pd.read_csv(os.path.join(OUT,"panel_v3.csv"),usecols=["asset","migration"]); _mg=set(_mg[_mg.migration.astype(str).str.lower().isin(["true","1","1.0"])].asset)
_mg_named="matic eos ftm gnt rndr btt nu strat maid ht rep agix xzc tomo npxs bnx ocean lend klay poly ant sai dgd quick dyp fxs gal keep bzrx cqt tvk rbn dar front pla cocos agi bit mpl noia orn mft lit chsb mco loki yamv2 rgt gxs key".split()
chk("C.3 migrations flagged in the census",len(_mg),50,0); chk("C.3 migrations named in the paper",len(_mg_named),50,0); chk("C.3 the names in the paper are the flagged assets",float(set(_mg_named)==_mg),1,0)

# Every check above, as data, added to the census checks written by 12_audit.py.
import json
_path=os.path.join(OUT,"results.json"); _doc=json.load(open(_path,encoding="utf-8")) if os.path.exists(_path) else {}
_doc["model_checks"]=records
with open(_path,"w",encoding="utf-8") as _f: json.dump(_doc,_f,indent=2,ensure_ascii=False)
