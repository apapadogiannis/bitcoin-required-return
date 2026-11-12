"""Appendix A.6: how much of Bitcoin's measured beta is Bitcoin moving the stock index itself.
If firms that move one for one with Bitcoin are a share x of the index, the mechanical addition to beta is x * var(BTC) / var(index).
Index weights: S&P 500 component weights as listed by Slickcharts (slickcharts.com/sp500), retrieved 12 November 2026.
Strategy (MSTR), MARA, Riot and Galaxy Digital are not constituents. Output: index_exposure.txt"""
weights = {"Coinbase": 0.10, "Robinhood": 0.16, "Block": 0.06}      # percent of the S&P 500
sig_btc, sig_idx, erp = 0.42, 0.141, 0.04                          # volatilities as in Table 8; equity premium 4%
ratio = sig_btc**2 / sig_idx**2
out = open("/home/claude/model/index_exposure.txt", "w")
def line(s):
    print(s); out.write(s + "\n")
line(f"variance ratio, Bitcoin to index: {ratio:.2f}")
x = sum(weights.values())
line(f"Coinbase + Robinhood + Block: x = {x:.2f}% of the index -> addition to beta {x/100*ratio:.3f}, to the required return {100*x/100*ratio*erp:.2f} points")
for xx in (0.5, 1.0):
    line(f"x = {xx:.1f}% -> addition to beta {xx/100*ratio:.3f}, to the required return {100*xx/100*ratio*erp:.2f} points")
out.close()
