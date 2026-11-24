"""Friday robustness: (a) birth-cohort FE as alternative to period FE in the
Lindy regression; (b) parametric Weibull and log-logistic survival fits.
Age+cohort+period are collinear (age = period - cohort), so we report the two
two-way specifications side by side.
"""
import os
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
from lifelines import WeibullFitter, LogLogisticFitter, KaplanMeierFitter

OUT = os.environ.get("OUT_DIR","outputs"); YR = 365.25
panel = pd.read_csv(f"{OUT}/panel_v3.csv",
                    parse_dates=["birth", "last", "death_cur_date"])
core = panel[~panel["stable2"] & ~panel["tokstock"] & ~panel["wrapped_like"]].copy()
core = core[(core["last"] - core["birth"]).dt.days >= 30].reset_index(drop=True)
dataset_end = panel["last"].max()
print("core:", len(core), "deaths:", core["dead_cur"].sum())

# person-period
recs = []
for _, r in core.iterrows():
    end = r["death_cur_date"] if r["dead_cur"] else dataset_end
    if pd.isna(end) or end < r["birth"]:
        continue
    months = pd.period_range(r["birth"], end, freq="M")
    if len(months) == 0:
        continue
    for m in months:
        age = ((m.to_timestamp() + pd.Timedelta(days=14)) - r["birth"]).days / YR
        if age <= 0:
            continue
        recs.append([r["asset"], str(m), age, 0, r["birth"].year])
    if r["dead_cur"]:
        recs[-1][3] = 1
pp = pd.DataFrame(recs, columns=["asset", "month", "age", "death", "byear"])
pp["logage"] = np.log(pp["age"])
pp["period"] = pp["month"].str[:4].astype(int).clip(lower=2016).astype(str)
# cohort groups: pre-2016, 2016-17, 2018-19, 2020-21, 2022-23, 2024+
def cgrp(y):
    if y < 2016: return "pre16"
    if y < 2018: return "c1617"
    if y < 2020: return "c1819"
    if y < 2022: return "c2021"
    if y < 2024: return "c2223"
    return "c24p"
pp["cohort"] = pp["byear"].map(cgrp)
pp["off"] = np.log(1 / 12)

specs = {
    "age only": "death ~ logage",
    "age + period FE": "death ~ logage + C(period)",
    "age + cohort FE": "death ~ logage + C(cohort)",
}
print("\n=== Poisson hazard regressions (curated deaths) ===")
for name, f in specs.items():
    m = smf.glm(f, data=pp, family=sm.families.Poisson(), offset=pp["off"]
                ).fit(cov_type="cluster", cov_kwds={"groups": pp["asset"]})
    print(f"{name:18s}: gamma_age = {m.params['logage']:+.3f} ({m.bse['logage']:.3f})")

# ---- the other rows of the table of age elasticities (Appendix C.4), on the same assets ----
# Each definition of death gives its own death date; an asset alive under a definition is followed to the end of the data.
def person_months(df, dead, date, end=dataset_end):
    rows = []
    for a, b, d, t in zip(df["asset"], df["birth"], df[dead], df[date]):
        stop = t if d else end
        if pd.isna(stop) or stop < b:
            continue
        n0 = len(rows)
        for m in pd.period_range(b, stop, freq="M"):
            age = ((m.to_timestamp() + pd.Timedelta(days=14)) - b).days / YR
            if age > 0:
                rows.append([a, str(m), age, 0])
        if d and len(rows) > n0:
            rows[-1][3] = 1
    q = pd.DataFrame(rows, columns=["asset", "month", "age", "death"])
    q["logage"] = np.log(q["age"]); q["off"] = np.log(1 / 12)
    q["period"] = q["month"].str[:4].astype(int).clip(lower=2016).astype(str)
    return q

def elasticity(q, year_effects):
    m = smf.glm("death ~ logage" + (" + C(period)" if year_effects else ""), data=q, family=sm.families.Poisson(),
                offset=q["off"]).fit(cov_type="cluster", cov_kwds={"groups": q["asset"]})
    return m.params["logage"], m.bse["logage"]

full = pd.read_csv(f"{OUT}/panel_v3.csv", parse_dates=["birth", "last", "death_cur_date", "death_strict_date",
                                                        "death_broad_date", "death_any_date"])
full = full[full["asset"].isin(core["asset"])].copy()
full["dead_any"] = full["dead_any"].astype(bool)
print("\n=== Age elasticity by definition of death (same assets) ===")
for name, dead, date in (("strict (feed ended)", "feed_dead", "death_strict_date"),
                         ("broad (feed or price)", "dead_broad", "death_broad_date"),
                         ("abandonment (all mechanical)", "dead_any", "death_any_date"),
                         ("curated (final)", "dead_cur", "death_cur_date")):
    q = person_months(full, dead, date)
    g0, s0 = elasticity(q, False); g1, s1 = elasticity(q, True)
    print(f"{name:30s}: deaths {int(q['death'].sum()):4d} | no year effects {g0:+.3f} ({s0:.3f}) | with year effects {g1:+.3f} ({s1:.3f})")
# the census ended at December 2024: later months are dropped, so the deaths of 2025 and 2026 do not count
q = person_months(full, "dead_cur", "death_cur_date"); q = q[q["month"] <= "2024-12"]
g1, s1 = elasticity(q, True)
print(f"{'curated, months to December 2024':30s}: deaths {int(q['death'].sum()):4d} | with year effects {g1:+.3f} ({s1:.3f})")
by_year = pd.to_datetime(full.loc[full["dead_cur"], "death_cur_date"]).dt.year.value_counts().sort_index()
print("curated deaths by year:", {int(k): int(v) for k, v in by_year.items()})

# parametric fits on duration data
T = np.where(core["dead_cur"],
             (pd.to_datetime(core["death_cur_date"]) - core["birth"]).dt.days / YR,
             (dataset_end - core["birth"]).dt.days / YR)
T = np.clip(T, 1 / 365.25, None)
E = core["dead_cur"].astype(int).values
print("\n=== Parametric survival fits ===")
wf = WeibullFitter().fit(T, E, label="Weibull")
# Weibull hazard rising iff rho > 1
print(f"Weibull: lambda_={wf.lambda_:.2f}, rho_={wf.rho_:.3f} "
      f"(rho>1 => hazard RISES with age; Lindy needs rho<1)")
print(f"  rho 95% CI: {wf.summary.loc['rho_','coef lower 95%']:.3f}"
      f"-{wf.summary.loc['rho_','coef upper 95%']:.3f}")
llf = LogLogisticFitter().fit(T, E, label="LogLogistic")
print(f"Log-logistic: alpha_={llf.alpha_:.2f}, beta_={llf.beta_:.3f} "
      f"(beta>1 => hazard hump-shaped rising then falling)")
print(f"AIC: Weibull {wf.AIC_:.0f} | LogLogistic {llf.AIC_:.0f}")

# median survival implied
print(f"Weibull median lifetime: {wf.median_survival_time_:.1f} yr")
print(f"KM median: ", KaplanMeierFitter().fit(T, E).median_survival_time_)
