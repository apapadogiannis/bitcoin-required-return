"""Earlier figure, not in the paper: Bitcoin's rolling four-year beta and correlation with the S&P 500 (month-end log returns;
expanding window before four years of data; beta capped at 3). Output: fig_beta.pdf and fig_beta.png"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src = open(os.path.join(SCRIPTS, "22_pretty_figs.py")).read()
exec(src.split("# ============ FIG 1")[0]); exec(src[src.index("# ============ FIG 5"):src.index("fig,ax=plt.subplots(figsize=(7.6,4.9))")])   # style, px, age, beta_roll, corr_roll
mm = (age >= 3.0) & (age <= 17.45); A = age[mm].values
etf_age = (pd.Timestamp("2024-01-11") - GEN).days / 365.25
plt.rcParams["axes.titlepad"] = 16
fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.4))
axs[0].plot(A, beta_roll[mm], color=BLUE, lw=1.8); axs[0].set_ylim(0, 3.3); axs[0].set_title("Rolling four-year beta to the S&P 500")
axs[1].plot(A, corr_roll[mm], color=ORANGE, lw=1.8); axs[1].set_ylim(-0.05, 0.7); axs[1].set_title("Rolling four-year correlation")
axs[1].text(etf_age + 0.1, 0.03, "spot ETFs", fontsize=7.8, color=INK2, ha="left", va="bottom")
c19_age = (pd.Timestamp("2020-03-31") - GEN).days / 365.25   # the month the co-movement appears (Appendix A.3)
axs[1].text(c19_age - 0.1, 0.62, "March 2020", fontsize=7.8, color=INK2, ha="right", va="bottom")
for ax in axs:
    ax.set_xlim(3, 17.6); ax.grid(axis="y", alpha=1.0); ax.set_axisbelow(True); ax.axvline(etf_age, color=MUT, lw=0.9, ls=(0, (2, 2)), zorder=1); ax.axvline(c19_age, color=MUT, lw=0.9, ls=(0, (2, 2)), zorder=1)
    sec = ax.secondary_xaxis("top", functions=(lambda x: x + 2009.0, lambda y: y - 2009.0)); sec.set_xticks([2013, 2016, 2019, 2022, 2025]); sec.tick_params(labelsize=7.5, colors=MUT, length=0, pad=1); sec.spines["top"].set_visible(False)
    ax.set_xlabel("Bitcoin age (years)")
fig.tight_layout()
fig.savefig(f"{FIG}/fig_beta.pdf"); fig.savefig(f"{FIG}/fig_beta.png", dpi=140); print("saved fig_beta")
