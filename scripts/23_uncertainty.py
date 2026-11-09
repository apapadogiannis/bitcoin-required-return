"""Propagate input uncertainty in the marginal-holder condition (Appendix B.5)."""
import numpy as np
rng = np.random.default_rng(1)
N = 400_000
rf, s2 = 0.05, 0.42**2
beta = rng.uniform(0.33, 1.05, N) * 0.04
gam = rng.uniform(1.7, 2.8, N)
w = rng.uniform(0.08, 0.19, N)
mort = rng.uniform(0.003, 0.03, N)
def report(x, label):
    q = np.percentile(x, [5, 16, 50, 84, 95])
    print(f"{label}: median {q[2]:.1%} | 68% {q[1]:.1%}-{q[3]:.1%} | 90% {q[0]:.1%}-{q[4]:.1%} | envelope {x.min():.1%}-{x.max():.1%}")
report(rf + beta + gam*s2*w + mort, "stated ranges              ")
report(rf + beta + gam*s2*w + rng.uniform(0.003, 0.015, N), "mortality 0.3-1.5 pts      ")
report(rf + beta + gam*s2*rng.uniform(0.12, 0.19, N) + rng.uniform(0.003, 0.015, N), "w 0.12-0.19, mort 0.3-1.5  ")

# Table 5: per-asset propagation
def run(label, sig, wlo, whi, mlo, mhi):
    s = sig if np.isscalar(sig) else rng.uniform(*sig, N)
    x = rf + beta + gam*s**2*rng.uniform(wlo, whi, N) + rng.uniform(mlo, mhi, N)
    q = np.percentile(x, [5, 50, 95])
    print(f"{label:14s} median {q[1]:5.1%}  90% {q[0]:5.1%}-{q[2]:5.1%}  envelope {x.min():5.1%}-{x.max():5.1%}")
run("Bitcoin", 0.42, 0.08, 0.19, 0.003, 0.03)
run("Ether", 0.64, 0.08, 0.19, 0.003, 0.03)
run("Large altcoin", 0.80, 0.10, 0.30, 0.01, 0.03)
run("Small coin", (1.0, 1.3), 0.10, 0.30, 0.157, 0.174)
