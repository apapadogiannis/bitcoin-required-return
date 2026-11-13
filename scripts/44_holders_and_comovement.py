"""Appendix A.3: Bitcoin's correlation with the S&P 500 through time, against the share of the Bitcoin supply held through funds
(the Grayscale trust, then the US spot ETFs) and by public companies (treasury companies). Two panels on one time axis.
Outputs: fig_holders_comovement.pdf/png, holders_comovement.txt
Anchors (million BTC), linear in between:
  funds: Grayscale Bitcoin Trust year-end balances from its SEC filings (2013-2023); US spot ETFs including the converted trust:
         0.62 at launch (January 11, 2024), 0.90 (July 22, 2024), 1.13 (end of 2024), 1.24 (June 28, 2025), 1.29 (June 1, 2026), from press
         reports of issuer data.
  public companies: 0.02 (end of 2019), 0.096 (2020), 0.216 (2021), 0.225 (2022), 0.281 (2023) as in 22_pretty_figs.py; then 0.33
         (September 30, 2024), 0.58 (end of 2024), 0.67 (May 2025), 1.00 (September 30, 2025), 1.10 (end of 2025), 1.13 (April 19, 2026),
         1.27 (September 21, 2026), from Bitcoin Treasuries reports."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import io, contextlib
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src = open(os.path.join(SCRIPTS, "22_pretty_figs.py")).read()
with contextlib.redirect_stdout(io.StringIO()):
    exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])   # style, px, _d (monthly log returns of Bitcoin and the S&P 500), _GBTC, _PUBCO
sply = pd.read_csv(os.path.join(CSV, "btc.csv"), usecols=["time", "SplyCur"], parse_dates=["time"]).set_index("time")["SplyCur"]
sply.index = sply.index.tz_localize(None) if sply.index.tz is not None else sply.index
sply = sply.resample("ME").last().reindex(px.index).ffill()
def path(anchors):
    d = pd.Series({pd.Timestamp(k): v for k, v in anchors.items()}).sort_index()
    t = px.index.astype("int64").values.astype(float); x = d.index.astype("int64").values.astype(float)
    return pd.Series(np.interp(t, x, d.values, left=0.0), index=px.index)
FUNDS = dict(_GBTC); FUNDS.update({"2024-01-11": 0.62, "2024-07-22": 0.90, "2024-12-31": 1.13, "2025-06-28": 1.24, "2026-06-01": 1.29})
PUBCO = dict(_PUBCO); PUBCO.update({"2024-09-30": 0.33, "2024-12-31": 0.58, "2025-05-31": 0.67, "2025-09-30": 1.00, "2025-12-31": 1.10, "2026-04-19": 1.13, "2026-09-21": 1.27})
funds = 100 * 1e6 * path(FUNDS) / sply; pub = 100 * 1e6 * path(PUBCO) / sply; tot = funds + pub
c24 = _d.b.rolling(24).corr(_d.s); c12 = _d.b.rolling(12).corr(_d.s)
out = open(os.path.join(OUT, "holders_comovement.txt"), "w")
def p(s=""):
    print(s); out.write(s + "\n")
p("Share of the Bitcoin supply held through funds and by public companies, and Bitcoin's correlation with the S&P 500 (monthly log returns)")
p(f"{'period':16s}{'months':>7s}{'correlation':>13s}{'funds %':>9s}{'companies %':>13s}{'together %':>12s}")
for lab, a, b in (("2012-2013", "2012", "2013"), ("2014-2019", "2014", "2019"), ("2020-2023", "2020", "2023"), ("2024-May 2026", "2024", "2026")):
    x = _d[a:b]; p(f"{lab:16s}{len(x):7d}{x.b.corr(x.s):13.2f}{funds[a:b].mean():9.1f}{pub[a:b].mean():13.1f}{tot[a:b].mean():12.1f}")
p()
for d in ("2019-12-31", "2020-06-30", "2020-12-31", "2021-12-31", "2023-12-31", "2024-12-31", "2025-12-31", "2026-05-31"):
    p(f"{d}: funds {funds.loc[d]:5.2f}%  companies {pub.loc[d]:5.2f}%  together {tot.loc[d]:5.2f}%  | 12-month correlation {c12.loc[d]:+.2f}  24-month {c24.loc[d]:+.2f}")
tot_a = tot.reindex(c24.index); m = c24.notna() & tot_a.notna() & (c24.index >= "2014-01-31")
p(); p(f"24-month correlation against the share held (levels, {int(m.sum())} overlapping months): correlation {np.corrcoef(c24[m], tot_a[m])[0,1]:.2f}")
for lab, a, b in (("2014-2019", "2014", "2019"), ("2020-2023", "2020", "2023"), ("2024-May 2026", "2024", "2026")):
    mm_ = m & (c24.index >= a) & (c24.index <= b + "-12-31"); p(f"  within {lab}: correlation of the 24-month correlation with the share held {np.corrcoef(c24[mm_], tot_a[mm_])[0,1]:+.2f}")
out.close()
# ---------------- figure: two panels, one time axis ----------------
plt.rcParams["axes.titlepad"] = 10
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 5.6), sharex=True, gridspec_kw=dict(height_ratios=[1.0, 1.0], hspace=0.28))
T0, T1 = pd.Timestamp("2013-01-01"), pd.Timestamp("2026-07-15")
a1.axhline(0, color=BASE, lw=0.9, zorder=1)
a1.plot(c24.index, c24, color=BLUE, lw=2.0, zorder=4)
for lab, a, b in (("2014", "2014", "2019"), ("2020", "2020", "2023"), ("2024", "2024", "2026")):
    x = _d[a:b]; v = x.b.corr(x.s); a1.plot([x.index[0], x.index[-1]], [v, v], color=INK, lw=1.3, ls=(0, (4, 2)), zorder=3)
    a1.text(x.index[0] + (x.index[-1] - x.index[0]) / 2, v + 0.045, f"{v:.2f}", fontsize=8.2, color=INK, ha="center", va="bottom")
a1.set_ylim(-0.45, 0.95); a1.set_ylabel("correlation"); a1.set_title("(a) Bitcoin's correlation with the S&P 500", loc="left")
a1.text(pd.Timestamp("2013-03-01"), 0.83, "line: previous 24 months; dashes: average of the period", fontsize=7.8, color=INK2, va="center")
a2.stackplot(funds.index, funds.values, pub.values, colors=[BLUE, ORANGE], alpha=0.92, lw=0, edgecolor="white")
a2.plot(funds.index, funds.values, color="white", lw=1.2, zorder=3)
a2.set_ylim(0, 14); a2.set_ylabel("% of the Bitcoin supply"); a2.set_title("(b) Bitcoin held through funds and by public companies", loc="left")
a2.text(pd.Timestamp("2022-01-15"), 1.5, "funds: Grayscale trust,\nthen spot ETFs", fontsize=8.0, color="white", ha="center", va="center", weight="bold")
a2.annotate("public companies", xy=(pd.Timestamp("2025-09-30"), 9.0), xytext=(pd.Timestamp("2021-09-01"), 10.6), fontsize=8.0, color=ORANGE, weight="bold", ha="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=ORANGE))
for ax in (a1, a2):
    ax.set_xlim(T0, T1); ax.grid(axis="y", alpha=1.0); ax.set_axisbelow(True)
    for dd in ("2020-03-31", "2024-01-11"): ax.axvline(pd.Timestamp(dd), color=MUT, lw=0.9, ls=(0, (2, 2)), zorder=2)
a1.text(pd.Timestamp("2020-02-10"), -0.36, "March 2020", fontsize=7.8, color=INK2, ha="right"); a1.text(pd.Timestamp("2024-02-25"), -0.36, "spot ETFs", fontsize=7.8, color=INK2, ha="left")
a2.text(T1 + pd.Timedelta(days=40), tot.iloc[-1], f"{tot.iloc[-1]:.0f}%", fontsize=8.0, color=INK, va="center", clip_on=False)
fig.subplots_adjust(left=0.09, right=0.95, top=0.94, bottom=0.07)
fig.savefig(f"{FIG}/fig_holders_comovement.pdf"); fig.savefig(f"{FIG}/fig_holders_comovement.png", dpi=150); print("saved fig_holders_comovement")
