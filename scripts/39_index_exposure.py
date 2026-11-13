"""Appendix A.6: how much of Bitcoin's measured beta is Bitcoin moving the stock index itself.
If firms that move one for one with Bitcoin are a share x of the index, the mechanical addition to beta is x * var(BTC) / var(index).
Index weights: holdings of the iShares Core S&P 500 ETF (IVV) as of 10 November 2026 (BlackRock, ishares.com).
Strategy (MSTR), MARA, Riot and Galaxy Digital are not constituents; Tesla (1.65%) held 11,509 BTC at 31 March 2026 (Form 10-Q). Output: index_exposure.txt"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
SCRIPTS = _HERE; DATA = os.environ.get("DATA_DIR", os.path.join(_ROOT, "data")); OUT = os.environ.get("OUT_DIR", os.path.join(_ROOT, "outputs"))
FIG = os.environ.get("FIG_DIR", os.path.join(_ROOT, "figures")); CSV = os.environ.get("CM_CSV_DIR", os.path.join(DATA, "cmdata", "csv"))
weights = {"Coinbase": 0.05, "Robinhood": 0.10, "Block": 0.07}      # percent of the S&P 500
sig_btc, sig_idx, erp = 0.42, 0.141, 0.04                          # volatilities as in Table 8; equity premium 4%
ratio = sig_btc**2 / sig_idx**2
out = open(os.path.join(OUT,"index_exposure.txt"), "w")
def line(s):
    print(s); out.write(s + "\n")
line(f"variance ratio, Bitcoin to index: {ratio:.2f}")
x = sum(weights.values())
line(f"Coinbase + Robinhood + Block: x = {x:.2f}% of the index -> addition to beta {x/100*ratio:.3f}, to the required return {100*x/100*ratio*erp:.2f} points")
for xx in (0.5, 1.0):
    line(f"x = {xx:.1f}% -> addition to beta {xx/100*ratio:.3f}, to the required return {100*xx/100*ratio*erp:.2f} points")
out.close()
