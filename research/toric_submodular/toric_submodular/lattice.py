"""Layer 1 - the Boolean lattice, exactly.

A set function on V = {0..n-1} is stored as a table of length 2^n indexed by
bitmask. Every transform here is exact over Fraction/int; nothing rounds.

    zeta:    f(A)    = sum_{S subset A} fhat(S)
    mobius:  fhat(S) = sum_{T subset S} (-1)^{|S|-|T|} f(T)
    walsh:   c(S)    = 2^-n sum_A f(A) (-1)^{|S & A|}

Correction to the source framework: the "sign cone" M_- = {fhat(S) <= 0 for
|S| >= 2} is *sufficient* for submodularity, not equivalent to it. The second
difference of f is a sum of atoms,

    f(A+i+j) - f(A+i) - f(A+j) + f(A) = sum_{ {i,j} <= S <= A+i+j } fhat(S),

so non-positive higher atoms force it <= 0; but coverage functions are
submodular with atoms of alternating sign (see `coverage_counterexample`).
"""
from fractions import Fraction
from itertools import combinations


def popcount(m):
    return bin(m).count("1")


def members(mask):
    """Elements of a bitmask, ascending."""
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return out


def to_mask(A):
    m = 0
    for i in A:
        m |= 1 << i
    return m


def table(f, n):
    """Tabulate an oracle f(frozenset) -> number over all 2^n subsets."""
    return [f(frozenset(members(m))) for m in range(1 << n)]


def oracle(t):
    """Turn a table back into an oracle on iterables of ints."""
    return lambda A: t[to_mask(A)]


def _n_of(t):
    n = len(t).bit_length() - 1
    if len(t) != 1 << n:
        raise ValueError(f"table length {len(t)} is not a power of two")
    return n


def zeta(fhat):
    """Subset-sum transform, O(n 2^n)."""
    t = list(fhat)
    n = _n_of(t)
    for i in range(n):
        b = 1 << i
        for m in range(len(t)):
            if m & b:
                t[m] += t[m ^ b]
    return t


def mobius(f):
    """Inverse of zeta: the Mobius atoms fhat(S), O(n 2^n)."""
    t = list(f)
    n = _n_of(t)
    for i in range(n):
        b = 1 << i
        for m in range(len(t)):
            if m & b:
                t[m] -= t[m ^ b]
    return t


def walsh(f):
    """Walsh-Fourier coefficients c(S) = 2^-n sum_A f(A) (-1)^{|S & A|}.

    These are the Fourier coefficients of f viewed as a function on the
    2-torsion subgroup T^n[2] = {0, pi}^n ~ (Z/2)^n (see extensions.py).
    """
    t = [Fraction(v) for v in f]
    n = _n_of(t)
    h = 1
    while h < len(t):
        for s in range(0, len(t), 2 * h):
            for m in range(s, s + h):
                a, b = t[m], t[m + h]
                t[m], t[m + h] = a + b, a - b
        h *= 2
    return [v / (1 << n) for v in t]


def walsh_from_mobius(fhat):
    """c(S) = (-1)^{|S|} sum_{T superset S} fhat(T) 2^{-|T|}  (exact identity).

    Follows from expanding prod_{i in T} (1 - cos t_i)/2 in the monomials
    prod_{i in S} cos t_i. Tested against `walsh` in the suite.
    """
    t = [Fraction(v, 1 << popcount(m)) for m, v in enumerate(fhat)]
    n = _n_of(t)
    for i in range(n):  # superset-sum transform
        b = 1 << i
        for m in range(len(t)):
            if not m & b:
                t[m] += t[m | b]
    return [(-v if popcount(m) % 2 else v) for m, v in enumerate(t)]


def submodularity_witness(f):
    """First (A, i, j) with f(A+i) + f(A+j) < f(A+i+j) + f(A), or None.

    Checking the local (pairwise) inequality over every A, i < j is exactly
    equivalent to submodularity; O(n^2 2^n) and exact.
    """
    n = _n_of(f)
    for A in range(1 << n):
        free = [i for i in range(n) if not A >> i & 1]
        for i, j in combinations(free, 2):
            bi, bj = 1 << i, 1 << j
            if f[A | bi] + f[A | bj] < f[A | bi | bj] + f[A]:
                return (members(A), i, j)
    return None


def is_submodular(f):
    return submodularity_witness(f) is None


def in_sign_cone(f):
    """True iff every Mobius atom of order >= 2 is <= 0 (the cone M_-)."""
    return all(v <= 0 for m, v in enumerate(mobius(f)) if popcount(m) >= 2)


def coverage_counterexample():
    """f(A) = 1 if A nonempty else 0, on n = 3: every set covers one point.

    Submodular (it is a coverage function) yet fhat({0,1,2}) = +1, so it lies
    outside M_-. This is the witness that M_- is a strict subcone.
    """
    return [0 if m == 0 else 1 for m in range(8)]


def minimizer_lattice(f):
    """All minimizers by brute force, as bitmasks. For small-n cross-checks.

    For submodular f the set is closed under union and intersection (a
    sublattice) - this, not Tarski applied to a flow, is the correct
    lattice-theoretic fixed-point statement.
    """
    lo = min(f)
    return [m for m, v in enumerate(f) if v == lo]
