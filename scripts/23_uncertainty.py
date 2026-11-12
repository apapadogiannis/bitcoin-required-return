"""Propagate input uncertainty in the marginal-holder condition (Appendix D.1, Table 5, Appendix E)."""
import numpy as np
rng = np.random.default_rng(1); N = 400_000; rf = 0.05; ERP = 0.04
def run(label, sig, blo, bhi, wlo, whi, mlo, mhi, glo=1.0, ghi=2.8, kap=1.0):
    """kap: the share of the crypto weight that moves with this asset (a number, or a range drawn uniformly)."""
    s = sig if np.isscalar(sig) else rng.uniform(*sig, N)
    k = kap if np.isscalar(kap) else rng.uniform(*kap, N)
    x = rf + rng.uniform(blo, bhi, N)*ERP + rng.uniform(glo, ghi, N)*s**2*k*rng.uniform(wlo, whi, N) + rng.uniform(mlo, mhi, N)
    q = np.percentile(x, [5, 16, 50, 84, 95])
    s0, s1 = (sig, sig) if np.isscalar(sig) else sig
    k0, k1 = (kap, kap) if np.isscalar(kap) else kap
    lo = rf + blo*ERP + glo*s0**2*k0*wlo + mlo; hi = rf + bhi*ERP + ghi*s1**2*k1*whi + mhi
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
    run("Bitcoin, sigma 0.35-0.50", (0.35, 0.50), 1.5, 2.0, 0.08, 0.19, 0.003, 0.03)
    run("Bitcoin, sigma 0.40-0.55 (option-implied)", (0.40, 0.55), 1.5, 2.0, 0.08, 0.19, 0.003, 0.03)
    # Section 7: measured inputs (31_cross_section.py). kap is the beta of the crypto market on the asset.
    run("Bitcoin, diversified holder (w=0)", 0.42, 1.5, 2.0, 0.0, 0.0, 0.003, 0.03)
    run("Ether, average crypto owner (kappa 0.7)", 0.64, 2.0, 2.7, 0.08, 0.19, 0.003, 0.03, kap=0.7)
    run("Ether, diversified holder (w=0)", 0.64, 2.0, 2.7, 0.0, 0.0, 0.003, 0.03)
    run("Large altcoin, average crypto owner", (0.66, 0.88), 1.5, 2.7, 0.08, 0.19, 0.01, 0.03, kap=(0.41, 0.56))
    run("Large altcoin, diversified holder (w=0)", (0.66, 0.88), 1.5, 2.7, 0.0, 0.0, 0.01, 0.03)
    run("Small coin, diversified holder (w=0)", (1.0, 1.3), 1.5, 2.7, 0.0, 0.0, 0.157, 0.174)
    # The survey's 19% is an equal-weighted mean of household shares; a wealth-weighted share of 12% as the upper bound.
    run("Bitcoin, w 0.08-0.12 (wealth-weighted share)", 0.42, 1.5, 2.0, 0.08, 0.12, 0.003, 0.03)
    # Dependence between inputs (Appendix D.1): the baseline draws them independently.
    def dep(label, ug, uw, ub, um):
        x = rf + (1.5 + 0.5*ub)*ERP + (1.0 + 1.8*ug)*0.42**2*(0.08 + 0.11*uw) + (0.003 + 0.027*um)
        q = np.percentile(x, [5, 50, 95]); print(f"{label:46s} median {q[1]:5.1%} | 90% {q[0]:5.1%}-{q[2]:5.1%}")
    u1, u2, u3, u4 = (rng.uniform(0, 1, N) for _ in range(4))
    dep("Dependence: gamma and w move together", u1, u1, u3, u4)
    dep("Dependence: gamma and w move oppositely", u1, 1 - u1, u3, u4)
    dep("Dependence: all four inputs move together", u1, u1, u1, u1)
