"""Draft figures and wedge_table.csv from an earlier calibration of the required return, kept for the record.
Nothing in the paper uses them; the paper's figures come from the scripts numbered 22 and above."""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "figure.dpi": 200,
                     "font.family": "serif", "axes.spines.top": False,
                     "axes.spines.right": False})
OUT = os.environ.get("OUT_DIR","outputs")
CSV = os.environ.get("CM_CSV_DIR","data/cmdata/csv")

def monthly(asset, col="PriceUSD"):
    df = pd.read_csv(f"{CSV}/{asset}.csv", parse_dates=["time"],
                     usecols=lambda c: c in ("time", "PriceUSD", "CapMrktCurUSD", "AdrBalCnt"))
    out = {}
    out["px"] = pd.to_numeric(df.set_index("time")["PriceUSD"], errors="coerce").dropna().resample("ME").last()
    if "CapMrktCurUSD" in df.columns:
        out["cap"] = pd.to_numeric(df.set_index("time")["CapMrktCurUSD"], errors="coerce").dropna().resample("ME").last()
    if "AdrBalCnt" in df.columns:
        out["adr"] = pd.to_numeric(df.set_index("time")["AdrBalCnt"], errors="coerce").dropna().resample("ME").mean()
    return out

btc = monthly("btc"); eth = monthly("eth")
px, cap, adr = btc["px"], btc["cap"], btc["adr"].reindex(btc["px"].index).interpolate()
lr = np.log(px).diff(); sig2 = lr.pow(2).ewm(halflife=9).mean() * 12
GEN = pd.Timestamp("2009-01-03")
age = pd.Series((px.index - GEN).days / 365.25, index=px.index)

i21 = px.index.get_indexer([pd.Timestamp("2021-09-30")], method="nearest")[0]
q = adr * (0.11 / adr.iloc[i21])
def interp(d):
    xs = [(pd.Timestamp(f"{y}-06-30") - GEN).days / 365.25 for y in sorted(d)]
    return pd.Series(np.interp(age, xs, [d[y] for y in sorted(d)]), index=px.index)
rf = interp({2012: .018, 2014: .025, 2016: .018, 2018: .029, 2020: .009, 2022: .030, 2024: .043, 2026: .050})
Wp = cap.iloc[i21] / 0.19 * (q / q.iloc[i21]) * (interp({2012: 0.25, 2021: 1.0, 2026: 1.4}) / 1.0)
wbar = (cap.reindex(px.index) / Wp).clip(upper=0.9)
foc_lo = rf + 0.0132 + 1.7 * sig2 * wbar + 0.003
foc_hi = rf + 0.042 + 2.8 * sig2 * wbar + 0.03
seg = interp({2012: 1.0, 2020: 1.0, 2022: 0.6, 2025: 0.15, 2026: 0.10})
req_hi = np.maximum(foc_hi, rf + seg * sig2)
req_mid = 0.5 * (foc_lo + req_hi)
BETA = 5.62
age_rule = (1 + 5 / age) ** (BETA / 5) - 1
fwd5 = (px.shift(-60) / px) ** (1 / 5) - 1

m = age >= 3.0
fig, ax = plt.subplots(figsize=(7.8, 5.0))
ax.fill_between(age[m], 100 * foc_lo[m], 100 * req_hi[m], color="#1f4e8c", alpha=0.18,
                label="required-return band: holder FOC (γ∈[1.7,2.8]) to option all-in bound")
ax.plot(age[m], 100 * req_mid[m], color="#1f4e8c", lw=1.8, label="required return (mid)")
ax.plot(age[m], 100 * fwd5[m], color="0.2", lw=1.1, label="realized forward 5-yr CAGR")
ax.plot(age[m], 100 * age_rule[m], color="#b23b3b", lw=1.5, label="age rule 5-yr forecast (β=5.62)")
mm = m & fwd5.notna()
ax.fill_between(age[mm], 100 * req_mid[mm], 100 * fwd5[mm], where=(fwd5[mm] > req_mid[mm]),
                color="#2e7d57", alpha=0.17, label="wedge: realized minus required")
ax.fill_between(age[mm], 100 * req_mid[mm], 100 * fwd5[mm], where=(fwd5[mm] <= req_mid[mm]),
                color="#b23b3b", alpha=0.14)
# ETF marker
etf_age = (pd.Timestamp("2024-01-11") - GEN).days / 365.25
ax.axvline(etf_age, color="0.35", lw=0.9, ls=":")
ax.annotate("spot ETFs approved\n(Jan 2024)", xy=(etf_age, 150), fontsize=7.5,
            color="0.3", ha="center",
            xytext=(etf_age - 0.1, 168),
            arrowprops=dict(arrowstyle="-", lw=0.6, color="0.4"))
for (yr, val, lab, dx, dy) in [(2021.75, 22, "holders expected 22% ('21)", -4.1, 16),
                               (2025.4, 13.8, "13.8% ('25)", -0.4, 22)]:
    A = yr - 2009.0
    ax.plot([A], [val], marker="D", color="#2e7d57", ms=5)
    ax.annotate(lab, xy=(A, val), xytext=(A + dx, val + dy), fontsize=7.5, color="#2e7d57",
                arrowprops=dict(arrowstyle="-", lw=0.6, color="#2e7d57"))
ax.axhline(0, color="k", lw=0.6)
ax.set_xlabel("Bitcoin age (years)"); ax.set_ylabel("% per year")
ax.set_xlim(3, 18.5); ax.set_ylim(-15, 232); ax.grid(alpha=0.22)
ax.set_title("Required return vs realized drift vs the age rule\nthe age rule tracks the decaying wedge, not a risk premium")
ax.legend(fontsize=7.5, loc="upper right")
fig.tight_layout()
fig.savefig(f"{OUT}/fig_wedge.pdf"); fig.savefig(f"{OUT}/fig_wedge.png", dpi=200)
print("fig_wedge rebuilt with ETF marker")

# Table 6.1 of the paper: the same series at two-year intervals.
rows = []
for yr in [2013, 2015, 2017, 2019, 2021, 2023, 2026]:
    i = px.index.get_indexer([pd.Timestamp(f"{yr}-06-30")], method="nearest")[0]
    rows.append(dict(year=yr, sigma=f"{np.sqrt(sig2.iloc[i]):.0%}", wbar=f"{wbar.iloc[i]:.0%}",
        required=f"{foc_lo.iloc[i]:.0%}–{req_hi.iloc[i]:.0%}",
        realized=(f"{fwd5.iloc[i]:.0%}" if np.isfinite(fwd5.iloc[i]) else "—"),
        wedge=(f"{fwd5.iloc[i]-req_mid.iloc[i]:+.0%}" if np.isfinite(fwd5.iloc[i]) else "—"),
        age_rule=f"{age_rule.iloc[i]:.0%}"))
T = pd.DataFrame(rows); print(T.to_string(index=False))
T.to_csv(f"{OUT}/wedge_table.csv", index=False)


# ---- Ether compression ----
epx = eth["px"]; elr = np.log(epx).diff()
esig = np.sqrt(elr.pow(2).ewm(halflife=9).mean() * 12)
bsig = np.sqrt(sig2)
efwd3 = (epx.shift(-36) / epx) ** (1 / 3) - 1
bfwd3 = (px.shift(-36) / px) ** (1 / 3) - 1

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0))
ax = axes[0]
ax.plot(px.index, 100 * bsig, color="#1f4e8c", lw=1.4, label="Bitcoin")
ax.plot(epx.index, 100 * esig, color="#2e7d57", lw=1.4, label="Ether")
ax.axvline(pd.Timestamp("2024-01-11"), color="0.4", ls=":", lw=0.9)
ax.axvline(pd.Timestamp("2024-07-23"), color="0.6", ls=":", lw=0.9)
ax.annotate("BTC ETFs", xy=(pd.Timestamp("2023-02-01"), 155), fontsize=7.5, color="0.35")
ax.annotate("ETH ETFs", xy=(pd.Timestamp("2024-09-01"), 140), fontsize=7.5, color="0.5")
ax.set_ylabel("annualized volatility (%)"); ax.set_ylim(0, 230)
ax.set_title("volatility: both compress into the ETF era")
ax.legend(fontsize=8); ax.grid(alpha=0.22)
ax = axes[1]
ax.plot(px.index, 100 * bfwd3, color="#1f4e8c", lw=1.2, label="Bitcoin")
ax.plot(epx.index, 100 * efwd3, color="#2e7d57", lw=1.2, label="Ether")
ax.axhline(0, color="k", lw=0.6)
ax.set_ylabel("forward 3-yr CAGR (%)"); ax.set_ylim(-80, 400)
ax.set_title("forward 3-yr returns: the same drift compression")
ax.legend(fontsize=8); ax.grid(alpha=0.22)
for a in axes:
    a.set_xlim(pd.Timestamp("2016-01-01"), pd.Timestamp("2026-07-01"))
fig.suptitle("Auxiliary prediction: compression is a mechanism, not a Bitcoin idiosyncrasy", fontsize=10)
fig.tight_layout()
fig.savefig(f"{OUT}/fig6_eth.pdf"); fig.savefig(f"{OUT}/fig6_eth.png", dpi=200)
# numbers for the text
for lab, s, f in [("BTC", bsig, bfwd3), ("ETH", esig, efwd3)]:
    i19 = s.index.get_indexer([pd.Timestamp("2019-06-30")], method="nearest")[0]
    print(f"{lab}: sigma 2019={s.iloc[i19]:.0%} -> 2026={s.iloc[-2]:.0%}; "
          f"fwd3y from 2019={f.iloc[i19]:.0%} vs from 2022-mid={f.iloc[f.index.get_indexer([pd.Timestamp('2022-12-31')],method='nearest')[0]]:.0%}")
