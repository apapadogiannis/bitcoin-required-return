import os
"""Publication-grade exhibit: Kaplan-Meier survival curves by size quartile
plus the ever-top-20 cohort. Vector PDF + PNG."""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "figure.dpi": 200,
    "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False})

OUT = os.environ.get("OUT_DIR","outputs"); YR = 365.25
panel = pd.read_csv(f"{OUT}/panel_v3.csv", parse_dates=["birth", "last", "death_cur_date"])
core = panel[~panel["stable2"] & ~panel["tokstock"] & ~panel["wrapped_like"]].copy()
core = core[(core["last"] - core["birth"]).dt.days >= 30].set_index("asset")
dataset_end = panel["last"].max()
V = pd.read_pickle(f"{OUT}/volume_monthly.pkl")
core["peak_vol"] = V.max().reindex(core.index)

T = np.where(core["dead_cur"],
             (pd.to_datetime(core["death_cur_date"]) - core["birth"]).dt.days / YR,
             (dataset_end - core["birth"]).dt.days / YR)
core["T"] = np.clip(T, 1 / 365.25, None)
core["E"] = core["dead_cur"].astype(int)

has = core["peak_vol"].notna()
qs = pd.qcut(core.loc[has, "peak_vol"], 4, labels=["Q1 (smallest)", "Q2", "Q3", "Q4 (largest)"])

# elite flag
ranks = V.rank(axis=1, ascending=False)
elite = [a for a in V.columns if (ranks[a] <= 20).any() and a in core.index]

fig, ax = plt.subplots(figsize=(6.6, 4.6))
colors = {"Q1 (smallest)": "#b23b3b", "Q2": "#b2762b", "Q3": "#8aa8c8", "Q4 (largest)": "#1f4e8c"}
for q in qs.cat.categories:
    sub = core.loc[has][qs == q]
    kmf = KaplanMeierFitter().fit(sub["T"], sub["E"], label=f"{q}  (n={len(sub)})")
    kmf.plot_survival_function(ax=ax, color=colors[q], lw=1.6, ci_alpha=0.12)
sub = core.loc[core.index.isin(elite)]
kmf = KaplanMeierFitter().fit(sub["T"], sub["E"], label=f"ever top-20  (n={len(sub)})")
kmf.plot_survival_function(ax=ax, color="black", lw=2.0, ls="--", ci_alpha=0.10)

ax.set_xlabel("age (years)"); ax.set_ylabel("fraction surviving, S(age)")
ax.set_xlim(0, 13); ax.set_ylim(0, 1.02)
ax.set_title("Survival by size: Kaplan–Meier curves by peak-volume quartile\n"
             "1,815 cryptoassets, curated deaths, 2010–2026")
ax.legend(fontsize=8, loc="lower left", frameon=False)
ax.grid(alpha=0.22)
# annotate medians
for q in ["Q1 (smallest)"]:
    sub = core.loc[has][qs == q]
    med = KaplanMeierFitter().fit(sub["T"], sub["E"]).median_survival_time_
    print(q, "median:", round(float(med), 2))
for lab, sub in [("Q4", core.loc[has][qs == "Q4 (largest)"]), ("top20", core.loc[core.index.isin(elite)])]:
    km = KaplanMeierFitter().fit(sub["T"], sub["E"])
    med = km.median_survival_time_
    s10 = float(km.survival_function_at_times(10).iloc[0])
    print(lab, "median:", med if np.isfinite(med) else ">window", " S(10y) =", round(s10, 2))
fig.tight_layout()
fig.savefig(f"{OUT}/fig5_km_size.pdf")
fig.savefig(f"{OUT}/fig5_km_size.png", dpi=200)
print("saved fig5_km_size.{pdf,png}")
