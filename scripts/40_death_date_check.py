"""Appendix C.3: the three jump-collapses (LUNA, UST, FTT) are dated by hand from the public record
(May 12 and November 10, 2022). This reruns 07_curated.py with the dates moved to either end of the documented
collapse windows (May 7 or 13; November 8 or 11) and compares every line it prints (hazards, confidence
intervals, age elasticities) with the baseline. Needs panel_v2.csv and volume_monthly.pkl in OUT_DIR
(written by 06_voldeath.py; run_all.sh produces them). Output: death_date_check.txt"""
import os, re, shutil, subprocess, sys, tempfile
OUT = os.environ.get("OUT_DIR", "outputs"); here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "07_curated.py")).read()
variants = {"baseline (May 12, November 10)": {},
            "early (May 7, November 8)": {"2022-05-12": "2022-05-07", "2022-11-10": "2022-11-08"},
            "late (May 13, November 11)": {"2022-05-12": "2022-05-13", "2022-11-10": "2022-11-11"}}
def run(sub):
    code = src
    for a, b in sub.items(): code = code.replace(f'"{a}"', f'"{b}"')
    with tempfile.TemporaryDirectory() as d:
        for f in ("panel_v2.csv", "volume_monthly.pkl"): shutil.copy(os.path.join(OUT, f), d)
        open(os.path.join(d, "curated_variant.py"), "w").write(code)
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(d, "curated_variant.py")], env={**os.environ, "OUT_DIR": d}, capture_output=True, text=True, check=True)
    dated = re.compile(r"^\s*(ust|luna|ftt)\s+2022-\d\d-\d\d\s")           # the three rows of the death table that carry the hand-entered day
    return [l for l in r.stdout.splitlines() if not dated.match(l)]
res = {k: run(v) for k, v in variants.items()}; base = res["baseline (May 12, November 10)"]
out = open(os.path.join(OUT, "death_date_check.txt"), "w")
def line(s):
    print(s); out.write(s + "\n")
for k, v in res.items():
    line(f"{k}: {len(v)} printed lines; identical to baseline apart from the three dates: {v == base}")
for l in base:
    if "gamma(FE)" in l or l.startswith("[ever top-20]"): line("  " + l)
out.close()
