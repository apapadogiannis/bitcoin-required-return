"""Rebuild panel correctly: coalesce price columns by coverage; use volume
span when longer; fiat excluded; proper flags from explicit lists."""
import os, numpy as np, pandas as pd

CSV_DIR = os.environ.get("CM_CSV_DIR","data/cmdata/csv")
OUT = os.environ.get("OUT_DIR","outputs")
YR = 365.25

ISO_FIAT = set("""aed afn all amd ang aoa ars aud awg azn bam bbd bdt bgn bhd bif bmd bnd bob brl bsd btn bwp byn bzd cad cdf chf clp cny cop crc cup cve czk djf dkk dop dzd egp ern etb eur fjd fkp gbp gel ghs gip gmd gnf gtq gyd hkd hnl hrk htg huf idr ils inr iqd irr isk jmd jod jpy kes kgs khr kmf kpw krw kwd kyd kzt lak lbp lkr lrd lsl lyd mad mdl mga mkd mmk mnt mop mru mur mvr mwk mxn myr mzn nad ngn nio nok npr nzd omr pab pen pgk php pkr pln pyg qar ron rsd rub rwf sar sbd scr sdg sek sgd shp sll sos srd ssp stn svc syp szl thb tjs tmt tnd top try ttd twd tzs uah ugx usd uyu uzs ves vnd vuv wst xaf xcd xof xpf yer zar zmw zwl xau xag xpt xpd""".split())

rows = []
monthly = {}
for f in sorted(os.listdir(CSV_DIR)):
    a = f[:-4]
    if a in ISO_FIAT:
        continue
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, f),
                         usecols=lambda c: c in ("time", "PriceUSD", "ReferenceRateUSD",
                                                 "CapMrktCurUSD", "volume_reported_spot_usd_1d"),
                         parse_dates=["time"])
    except Exception:
        continue
    px_a = pd.to_numeric(df.get("PriceUSD"), errors="coerce") if "PriceUSD" in df.columns else pd.Series(np.nan, index=df.index)
    px_b = pd.to_numeric(df.get("ReferenceRateUSD"), errors="coerce") if "ReferenceRateUSD" in df.columns else pd.Series(np.nan, index=df.index)
    # coalesce: prefer the series with more coverage as base, fill from the other
    if px_a.notna().sum() >= px_b.notna().sum():
        px = px_a.fillna(px_b)
    else:
        px = px_b.fillna(px_a)
    px = px.where(px > 0)
    vol = pd.to_numeric(df.get("volume_reported_spot_usd_1d"), errors="coerce") if "volume_reported_spot_usd_1d" in df.columns else pd.Series(np.nan, index=df.index)
    vol = vol.where((vol > 0) & (vol < 1e12))   # a reported volume above $1 trillion a day is a feed error (PAXG, GNO and five token pairs in 2026)

    t = df["time"]
    p_mask, v_mask = px.notna(), vol.notna()
    n_px, n_vol = int(p_mask.sum()), int(v_mask.sum())
    if n_px == 0 and n_vol < 30:
        continue

    # lifetime span = union of price and volume activity
    firsts = [t[m].iloc[0] for m in (p_mask, v_mask) if m.any()]
    lasts  = [t[m].iloc[-1] for m in (p_mask, v_mask) if m.any()]
    birth, last = min(firsts), max(lasts)

    rec = dict(asset=a, birth=birth, last=last, n_px=n_px, n_vol=n_vol)
    if n_px >= 90:
        d = pd.DataFrame({"time": t[p_mask], "px": px[p_mask]}).sort_values("time")
        ath = d["px"].max()
        final_px = d["px"].iloc[-1]
        thresh = 0.01 * ath
        econ_dead, econ_dt = False, pd.NaT
        if final_px < thresh:
            below = (d["px"] < thresh).values
            above_idx = np.where(~below)[0]
            start = (above_idx[-1] + 1) if len(above_idx) else 0
            econ_dead, econ_dt = True, d["time"].iloc[start]
        med = d["px"].median()
        rec.update(ath=ath, final_px=final_px, final_over_ath=final_px / ath,
                   ath_date=d.loc[d["px"].idxmax(), "time"],
                   econ_dead=econ_dead, econ_death_date=econ_dt,
                   stable=(0.95 <= med <= 1.05) and (ath < 2.0),
                   last_px_date=d["time"].iloc[-1])
        if "CapMrktCurUSD" in df.columns:
            rec["peak_cap"] = pd.to_numeric(df["CapMrktCurUSD"], errors="coerce").max()
        monthly[a] = d.set_index("time")["px"].resample("ME").last().dropna()
    else:
        rec.update(ath=np.nan, final_px=np.nan, final_over_ath=np.nan, ath_date=pd.NaT,
                   econ_dead=False, econ_death_date=pd.NaT, stable=False,
                   last_px_date=pd.NaT, peak_cap=np.nan)
    rows.append(rec)

panel = pd.DataFrame(rows)
dataset_end = panel["last"].max()
print("assets:", len(panel), "| dataset end:", dataset_end.date())

panel["feed_dead"] = (dataset_end - panel["last"]).dt.days > 180
panel["death_strict_date"] = panel["last"].where(panel["feed_dead"])
panel["dead_broad"] = panel["feed_dead"] | panel["econ_dead"]
panel["death_broad_date"] = panel[["death_strict_date", "econ_death_date"]].min(axis=1)
panel.loc[~panel["dead_broad"], "death_broad_date"] = pd.NaT
panel["age_end_strict"] = np.where(panel["feed_dead"],
    (panel["death_strict_date"] - panel["birth"]).dt.days / YR,
    (dataset_end - panel["birth"]).dt.days / YR)
panel["age_end_broad"] = np.where(panel["dead_broad"],
    (panel["death_broad_date"] - panel["birth"]).dt.days / YR,
    (dataset_end - panel["birth"]).dt.days / YR)

# explicit tokenized-equity suffix families (xStocks 'x', Ondo-style 'on')
STEMS = "aal aapl abbv abnb abt acn adbe amd amzn avgo axp ba bac brk brkb cat coin crcl crm csco cvx dfdv dis gld glxy gme goog googl hd hon hood iau ibm intc jnj jpm ko lin lly ma mcd meta mrk mrvl msft mstr nflx nke nvda orcl pep pfe pg pltr qqq slv spy tqqq tsla unh uso v vst vti vz wmt xom azn nvo sap tm".split()
tok = set()
for s in STEMS:
    tok.add(s + "x"); tok.add(s + "on")
panel["tokstock"] = panel["asset"].isin(tok)
WRAPPED = set("wbtc weth wsteth steth cbbtc cbeth reth rseth wbeth frxeth sfrxeth tbtc renbtc hbtc btcb wbnb wsol bnsol jitosol msol ezeth weeth rsweth sweth oseth lseth meth ankreth btse cmeth stsol solvbtc wavax wmatic wpol".split())
panel["wrapped_like"] = panel["asset"].isin(WRAPPED)

panel.to_csv(f"{OUT}/panel_full.csv", index=False)
pd.DataFrame(monthly).to_pickle(f"{OUT}/prices_monthly.pkl")

core = panel[~panel["stable"] & ~panel["tokstock"] & ~panel["wrapped_like"]]
core = core[(core["last"] - core["birth"]).dt.days >= 30]
print("core universe:", len(core))
print("feed-dead:", core["feed_dead"].sum(), "| broad dead:", core["dead_broad"].sum())
print("\nbirths by year:"); print(core.groupby(core["birth"].dt.year).size().to_string())
print("\ndeaths (strict) by last-obs month, top 12:")
print(core.loc[core["feed_dead"], "last"].dt.to_period("M").value_counts().head(12).to_string())
