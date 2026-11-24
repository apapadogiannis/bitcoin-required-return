"""The deaths of the census in calendar time (Appendix C.4).

1. The death rate by calendar year, and the death rates of Table 1 with the census ended at December 2024.
2. The census retaken at earlier dates with the same rules, and what became of its deaths by the end of the data:
   how often a death by the mechanical rules is reversed later.
Reads outputs/panel_v3.csv, outputs/elite_top20_curated.csv, outputs/volume_monthly.pkl and the daily files.
Writes outputs/earlier_censuses.txt."""
import os
import numpy as np, pandas as pd

CSV = os.environ.get("CM_CSV_DIR", "data/cmdata/csv"); OUT = os.environ.get("OUT_DIR", "outputs"); YR = 365.25
CUT = pd.Timestamp("2024-12-31")
L = []
def say(s=""):
    L.append(s); print(s)

panel = pd.read_csv(f"{OUT}/panel_v3.csv", parse_dates=["birth", "last", "death_cur_date"])
END = panel["last"].max()
core = panel[~panel["stable2"] & ~panel["tokstock"] & ~panel["wrapped_like"]]
core = core[(core["last"] - core["birth"]).dt.days >= 30].set_index("asset")

# ---- 1. calendar time
def rate(birth, dead, date, stop=None, event=None):
    """Deaths dated up to `stop` (of the kind `event`, if given) and asset-years lived up to it, counted in days.
    Without `stop`: every death, and the living followed to the end of the data."""
    m = birth < (stop if stop is not None else END)
    d = dead[m] & ((date[m] <= stop) if stop is not None else True)
    end = pd.to_datetime(np.where(d, date[m], stop if stop is not None else END))
    n = d if event is None else d & event[m]
    return int(n.sum()), ((end - birth[m]).dt.days / YR).sum()

def rate_months(c, stop=None):
    """The same in asset-months, as the tables of the census count exposure (07_curated.py)."""
    deaths = months = 0
    for b, d, t in zip(c["birth"], c["dead_cur"], c["death_cur_date"]):
        d = bool(d) and (stop is None or t <= stop)
        e = t if d else (stop if stop is not None else END)
        if e < b:
            continue
        per = pd.period_range(b, e, freq="M")
        n = sum(((m.to_timestamp() + pd.Timedelta(days=14)) - b).days > 0 for m in per)
        months += n; deaths += int(d and n > 0)
    return deaths, months / 12

say("Death rate by calendar year: deaths dated in the year, asset-years lived in the year, percent a year")
last = pd.Series(pd.to_datetime(np.where(core["dead_cur"], core["death_cur_date"], END)), index=core.index).clip(upper=END)
for y in range(2018, END.year + 1):
    a, b = pd.Timestamp(f"{y}-01-01"), min(pd.Timestamp(f"{y}-12-31"), END)
    ex = ((last.clip(upper=b) - core["birth"].clip(lower=a)).dt.days.clip(lower=0) / YR).sum()
    d = int((core["dead_cur"] & (core["death_cur_date"] >= a) & (core["death_cur_date"] <= b)).sum())
    say(f"  {y}: {d:4d} {ex:7.0f} {100 * d / ex:5.1f}")
say()
say("Death rates with the census ended at December 2024, and at the end of the data: deaths, percent a year")
d0, x0 = rate_months(core, CUT); d1, x1 = rate_months(core)
say(f"  all assets          : {d0:4d} {100 * d0 / x0:5.1f} | {d1:4d} {100 * d1 / x1:5.1f}")
V = pd.read_pickle(f"{OUT}/volume_monthly.pkl"); pk = V.max().reindex(core.index).dropna()
qs = pd.qcut(pk, 4, labels=["smallest quarter", "second quarter", "third quarter", "largest quarter"])
for g in qs.cat.categories:
    c = core.loc[qs.index[qs == g]]
    d0, x0 = rate_months(c, CUT); d1, x1 = rate_months(c)
    say(f"  {g:20s}: {d0:4d} {100 * d0 / x0:5.1f} | {d1:4d} {100 * d1 / x1:5.1f}")
E20 = pd.read_csv(f"{OUT}/elite_top20_curated.csv", parse_dates=["first_top", "death_date"])
for lab, ev in (("ever top twenty", None), ("  sudden collapses", E20["cat"] == 1)):
    d0, x0 = rate(E20["first_top"], E20["death"] == 1, E20["death_date"], CUT, ev)
    d1, x1 = rate(E20["first_top"], E20["death"] == 1, E20["death_date"], None, ev)
    say(f"  {lab:20s}: {d0:4d} {100 * d0 / x0:5.2f} | {d1:4d} {100 * d1 / x1:5.2f}   (asset-years {x0:,.0f} | {x1:,.0f})")

# ---- 2. the census at earlier dates
vol, px = {}, {}
for a in core.index:
    df = pd.read_csv(os.path.join(CSV, a + ".csv"), usecols=lambda c: c in ("time", "PriceUSD", "ReferenceRateUSD", "volume_reported_spot_usd_1d"), parse_dates=["time"]).set_index("time")
    if "volume_reported_spot_usd_1d" in df:
        v = pd.to_numeric(df["volume_reported_spot_usd_1d"], errors="coerce"); vol[a] = v[(v > 0) & (v < 1e12)]
    pa = pd.to_numeric(df["PriceUSD"], errors="coerce") if "PriceUSD" in df else pd.Series(np.nan, index=df.index)
    pb = pd.to_numeric(df["ReferenceRateUSD"], errors="coerce") if "ReferenceRateUSD" in df else pd.Series(np.nan, index=df.index)
    p = pa.fillna(pb) if pa.notna().sum() >= pb.notna().sum() else pb.fillna(pa)
    px[a] = p[p > 0]
CAT = core.loc[core["catastrophe"], "death_cur_date"]
NONE = pd.Series(dtype=float, index=pd.DatetimeIndex([]))

def census(as_of):
    """The rules of Section 3 on the data up to `as_of`. Returns dead (bool) and death date, by asset."""
    T = pd.Timestamp(as_of); rows = {}
    for a in core.index:
        v = vol.get(a, NONE); v = v[v.index <= T]; p = px[a][px[a].index <= T]
        ends = [s.index for s in (v, p) if len(s)]
        if not ends or (len(p) == 0 and len(v) < 30):
            continue
        birth, lastobs = min(i[0] for i in ends), max(i[-1] for i in ends)
        if (lastobs - birth).days < 30:
            continue
        dates = []
        rows[a] = [lastobs, dates, len(p), v]
    end = max(r[0] for r in rows.values())
    out = {}
    for a, (lastobs, dates, npx, v) in rows.items():
        if (end - lastobs).days > 180:
            dates.append(lastobs)
        p = px[a][px[a].index <= T]
        if len(p) >= 90 and p.iloc[-1] < 0.01 * p.max():
            above = np.where(p.values >= 0.01 * p.max())[0]; dates.append(p.index[above[-1] + 1 if len(above) else 0])
        if len(v) >= 10:
            s = v.resample("ME").mean().dropna()
            if len(s) >= 6:
                peak = s.rolling(12, min_periods=3).mean().max()
                below = (s.rolling(3, min_periods=1).mean() < 0.01 * peak).values
                if peak > 0 and below[-1] and s.tail(3).mean() < 2.5e5:
                    alive = np.where(~below)[0]; dates.append(s.index[alive[-1] + 1 if len(alive) else 0])
        dead, date = bool(dates), (min(dates) if dates else pd.NaT)
        if core.at[a, "migration"]:
            dead, date = False, pd.NaT
        if a in CAT.index:
            dead, date = (True, CAT[a]) if CAT[a] <= end else (False, pd.NaT)
        out[a] = (dead, date)
    r = pd.DataFrame(out, index=["dead", "date"]).T
    r["dead"] = r["dead"].astype(bool); r["date"] = pd.to_datetime(r["date"])
    return r, end

final, _ = census(END)
same = (final["dead"].reindex(core.index).fillna(False) == core["dead_cur"]).all()
say(); say(f"The rules as written here reproduce the census at the end of the data: {bool(same)} ({int(final['dead'].sum())} deaths)")
assert same
say("Census retaken at earlier dates: assets, deaths, of which alive again at the end of the data; deaths dated in the 17 months before, of which alive again")
tot = [0, 0, 0, 0]
for as_of in ("2022-05-24", "2023-05-24", "2023-12-31", "2024-05-24", "2024-12-31", "2025-05-24", "2025-11-24"):
    c, e = census(as_of); dead = c[c["dead"]]
    back = dead.index[~core["dead_cur"].reindex(dead.index)]
    rec = dead[dead["date"] > e - pd.DateOffset(months=17)]; back_r = [a for a in rec.index if a in set(back)]
    say(f"  {as_of}: {len(c):5d} {len(dead):4d} {len(back):3d} ({100 * len(back) / len(dead):2.0f}%) | {len(rec):4d} {len(back_r):3d} ({100 * len(back_r) / max(len(rec), 1):2.0f}%)")
rec = core[core["dead_cur"] & (core["death_cur_date"] >= "2025-01-01")]
only_v = rec["vol_dead_c"] & ~rec["feed_dead"] & ~rec["econ_dead"].fillna(False).astype(bool)
say(f"Deaths dated 2025 or 2026: {len(rec)} of {int(core['dead_cur'].sum())}; feed ended {int(rec['feed_dead'].sum())}; resting on the volume rule alone {int(only_v.sum())}, "
    f"with a median volume of ${rec.loc[only_v, 'final_vol_3m'].median():,.0f} a day over the last three months")
open(f"{OUT}/earlier_censuses.txt", "w").write("\n".join(L) + "\n")
