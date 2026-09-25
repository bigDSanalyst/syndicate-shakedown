import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from toric_submodular.lattice import members, to_mask  # noqa: E402


def as_oracle(t):
    return lambda A: t[to_mask(A)]


def cut_plus_modular(n, rng, p=0.4, wmax=4, amax=6):
    E = [(i, j, rng.randint(1, wmax)) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
    a = [rng.randint(-amax, amax) for _ in range(n)]
    return lambda A: sum(w for i, j, w in E if (i in A) != (j in A)) + sum(a[i] for i in A)


def concave_card_plus_modular(n, rng):
    c = [rng.randint(1, 3) for _ in range(n)]
    cap = rng.randint(2, 2 * n)
    a = [rng.randint(-3, 1) for _ in range(n)]
    return lambda A: min(cap, sum(c[i] for i in A)) + sum(a[i] for i in A)


def facility_minus_modular(n, rng, m=4):
    W = [[rng.randint(0, 6) for _ in range(m)] for _ in range(n)]
    a = [rng.randint(0, 7) for _ in range(n)]
    return lambda A: sum(max((W[i][j] for i in A), default=0) for j in range(m)) - sum(a[i] for i in A)


GENERATORS = [cut_plus_modular, concave_card_plus_modular, facility_minus_modular]


def rng(seed):
    return random.Random(seed)
