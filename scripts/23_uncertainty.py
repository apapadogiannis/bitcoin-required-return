"""Propagate input uncertainty in the marginal-holder condition (Appendix D.1, Table 5, Appendix E)."""
import numpy as np
rng = np.random.default_rng(1); N = 400_000; rf = 0.05; ERP = 0.04
def run(label, sig, blo, bhi, wlo, whi, mlo, mhi, glo=1.0, ghi=2.8):
    s = sig if np.isscalar(sig) else rng.uniform(*sig, N)
    x = rf + rng.uniform(blo, bhi, N)*ERP + rng.uniform(glo, ghi, N)*s**2*rng.uniform(wlo, whi, N) + rng.uniform(mlo, mhi, N)
    q = np.percentile(x, [5, 16, 50, 84, 95])
    s0, s1 = (sig, sig) if np.isscalar(sig) else sig
    lo = rf + blo*ERP + glo*s0**2*wlo + mlo; hi = rf + bhi*ERP + ghi*s1**2*whi + mhi
    print(f"{label:30s} median {q[2]:5.1%} | 68% {q[1]:5.1%}-{q[3]:5.1%} | 90% {q[0]:5.1%}-{q[4]:5.1%} | envelope {lo:5.1%}-{hi:5.1%}")
    return q
if __name__ == "__main__":
    run("Bitcoin", 0.42, 1.5, 2.0, 0.08, 0.19, 0.003, 0.03)
    run("Bitcoin, mortality 0.3-1.5", 0.42, 1.5, 2.0, 0.08, 0.19, 0.003, 0.015)
    run("Bitcoin, w 0.12-0.19", 0.42, 1.5, 2.0, 0.12, 0.19, 0.003, 0.03)
    run("Bitcoin, gamma 1.7-2.8 (household range)", 0.42, 1.5, 2.0, 0.08, 0.19, 0.003, 0.03, glo=1.7)
    run("Bitcoin, w 0.075-0.139 (crypto-wide back-cast)", 0.42, 1.5, 2.0, 0.075, 0.139, 0.003, 0.03)
    run("Ether", 0.64, 2.0, 2.7, 0.08, 0.19, 0.003, 0.03)
    run("Large altcoin", 0.80, 2.0, 2.7, 0.10, 0.30, 0.01, 0.03)
    run("Small coin", (1.0, 1.3), 2.0, 2.7, 0.10, 0.30, 0.157, 0.174)
    run("Gold", (0.13, 0.20), -0.1, 0.1, 0.02, 0.10, 0.0, 0.003)
    run("Bitcoin at gold sigma and w", 0.15, 1.5, 2.0, 0.02, 0.10, 0.003, 0.03)
