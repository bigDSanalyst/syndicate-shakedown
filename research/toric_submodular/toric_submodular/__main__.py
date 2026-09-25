"""python3 -m toric_submodular  - walk the corrected framework on one example."""
import json
import random
import time

from . import (coverage_counterexample, in_sign_cone, is_submodular, minimize, mobius,
               morse_index, sign_flow, spurious_torus_minima, verify_certificate, walsh)
from .lattice import to_mask

TRAP = [0, 7, 1, 4, 2, 7, -1, 0]


def main():
    f = lambda A: TRAP[to_mask(A)]
    print("Layer 1  f =", TRAP, " submodular:", is_submodular(TRAP))
    print("         Mobius atoms:", mobius(TRAP), " in sign cone M_-:", in_sign_cone(TRAP))
    cov = coverage_counterexample()
    print("         coverage", cov, "submodular:", is_submodular(cov),
          "in M_-:", in_sign_cone(cov), "-> M_- is strictly smaller")
    print("Layer 2  Walsh = cosine coefficients of the torus potential:",
          [str(c) for c in walsh(TRAP)])
    print("Layer 4  Morse index at theta=0:", morse_index(TRAP, 0),
          " spurious torus minima:", spurious_torus_minima(TRAP))
    tr = sign_flow(f, [0.0] * 3)
    print("Layer 3  specified sign flow from theta=0: stalled =", tr.stalled_at_start,
          " best found =", tr.best_value)
    res = minimize(f, 3)
    print("Engine   min-norm point: min =", res.value, " minimizers",
          sorted(res.minimal), "..", sorted(res.maximal), " certified =", res.certified)
    print("         certificate:", json.dumps(res.certificate))

    rng = random.Random(0)
    n = 50
    E = [(i, j, rng.randint(1, 5)) for i in range(n) for j in range(i + 1, n) if rng.random() < .1]
    a = [rng.randint(-9, 8) for _ in range(n)]
    g = lambda A: sum(w for i, j, w in E if (i in A) != (j in A)) + sum(a[i] for i in A)
    t0 = time.perf_counter()
    r = minimize(g, n)
    dt = time.perf_counter() - t0
    print(f"Scale    n={n} cut+modular (2^{n} sets): min = {r.value}, |A| = {len(r.minimal)}, "
          f"certified = {r.certified} ({verify_certificate(g, r.certificate)[1]}) in {dt:.2f}s")


if __name__ == "__main__":
    main()
