"""Layers 2-4: extensions, the toric pullback, and Morse theory at torsion."""
import math
from fractions import Fraction

import pytest
from conftest import GENERATORS, as_oracle, rng

from toric_submodular.extensions import (level_set_rounding, lovasz, lovasz_from_mobius,
                                         morse_index, spurious_torus_minima, torsion_hessian,
                                         torsion_point, toric_fourier, toric_lovasz,
                                         toric_multilinear)
from toric_submodular.flow import sign_flow
from toric_submodular.lattice import is_submodular, mobius, table, walsh
from toric_submodular.solver import minimize

# Submodular (cut + modular on 3 nodes), with a spurious strict local minimum
# of the torus potential at theta = 0 (the empty set): f(empty) = 0 while the
# minimum is f({1,2}) = -1. Found by search; pinned here as a fixture.
TRAP = [0, 7, 1, 4, 2, 7, -1, 0]


def normalized(t):
    return [v - t[0] for v in t]


@pytest.mark.parametrize("gen", GENERATORS)
@pytest.mark.parametrize("seed", range(6))
def test_lovasz_greedy_equals_mobius_form(gen, seed):
    r = rng(seed)
    n = r.randint(1, 6)
    t = normalized(table(gen(n, r), n))
    w = [Fraction(r.randint(0, 20), 20) for _ in range(n)]
    assert lovasz(as_oracle(t), w) == lovasz_from_mobius(mobius(t), w)


@pytest.mark.parametrize("seed", range(20))
def test_level_set_rounding_never_worse(seed):
    r = rng(seed)
    n = r.randint(1, 7)
    f = GENERATORS[seed % 3](n, r)
    w = [Fraction(r.randint(0, 50), 50) for _ in range(n)]
    _, v = level_set_rounding(f, w)
    assert v - f(frozenset()) <= lovasz(f, w)


@pytest.mark.parametrize("seed", range(10))
def test_toric_potential_is_the_walsh_series_and_hits_f_at_torsion(seed):
    r = rng(seed)
    n = r.randint(1, 6)
    t = [r.randint(-9, 9) for _ in range(1 << n)]
    t[0] = 0
    fhat, c = mobius(t), walsh(t)
    for _ in range(5):
        th = [r.uniform(0, 2 * math.pi) for _ in range(n)]
        assert toric_multilinear(fhat, th) == pytest.approx(toric_fourier(c, th), abs=1e-9)
    for x in range(1 << n):
        assert toric_multilinear(fhat, torsion_point(x, n)) == pytest.approx(t[x], abs=1e-9)


def _num_hessian(F, th, h=1e-4):
    n = len(th)
    H = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            def at(di, dj):
                p = list(th); p[i] += di; p[j] += dj
                return F(p)
            H[i][j] = (at(h, h) - at(h, -h) - at(-h, h) + at(-h, -h)) / (4 * h * h)
    return H


@pytest.mark.parametrize("seed", range(6))
def test_torsion_hessian_is_half_the_flip_gains(seed):
    r = rng(seed)
    n = r.randint(1, 5)
    t = [r.randint(-9, 9) for _ in range(1 << n)]
    fhat = mobius(t)
    F = lambda th: toric_multilinear(fhat, th)
    for x in range(1 << n):
        th = torsion_point(x, n)
        exact = torsion_hessian(t, x)
        num = _num_hessian(F, th)
        for i in range(n):
            # every torsion point is critical
            e = [0.0] * n; e[i] = 1e-6
            grad_i = (F([a + b for a, b in zip(th, e)]) - F([a - b for a, b in zip(th, e)])) / 2e-6
            assert grad_i == pytest.approx(0, abs=1e-6)
            for j in range(n):
                want = float(exact[i]) if i == j else 0.0
                assert num[i][j] == pytest.approx(want, abs=1e-4)


def test_trap_is_submodular_and_a_spurious_minimum():
    assert is_submodular(TRAP)
    assert spurious_torus_minima(TRAP) == [0]
    assert morse_index(TRAP, 0) == (0, 0)
    assert min(TRAP) == -1


def test_specified_flow_stalls_where_the_solver_does_not():
    f = as_oracle(TRAP)
    trace = sign_flow(f, [0.0, 0.0, 0.0])
    assert trace.stalled_at_start
    assert trace.best_value == 0            # the flow never reaches -1
    res = minimize(f, 3)
    assert res.certified and res.value == -1 and res.minimal == frozenset({1, 2})


def test_flow_rejects_step_outside_spec():
    with pytest.raises(ValueError):
        sign_flow(as_oracle(TRAP), [1.0] * 3, dt=0.6)


# ---- which transform is in the cosine coefficients: pinned independently ----

def _cosine_coefficients_by_quadrature(t):
    """Fourier coefficients of F, extracted by exact quadrature on the grid
    {0, pi/2, pi, 3pi/2}^n. F is evaluated through its Mobius form
    sum_T fhat(T) prod w_i with w = (1 - cos)/2, which is rational on this grid.
    Grid means: E[cos] = 0, E[cos^2] = 1/2, so c(S) = 2^|S| E[F prod_{i in S} cos].
    Independent of walsh() and of walsh_from_mobius()."""
    n = len(t).bit_length() - 1
    fhat = mobius(t)
    cos4 = [1, 0, -1, 0]
    out = []
    for S in range(1 << n):
        acc = Fraction(0)
        for g in range(4 ** n):
            k = [(g // 4 ** i) % 4 for i in range(n)]
            c = [cos4[j] for j in k]
            w = [Fraction(1 - ci, 2) for ci in c]
            F = Fraction(0)
            for T, a in enumerate(fhat):
                if a:
                    p = Fraction(a)
                    for i in range(n):
                        if T >> i & 1:
                            p *= w[i]
                    F += p
            for i in range(n):
                if S >> i & 1:
                    F *= c[i]
            acc += F
        out.append(acc / 4 ** n * 2 ** bin(S).count("1"))
    return out


@pytest.mark.parametrize("seed", range(6))
def test_cosine_coefficients_are_the_hadamard_transform_not_mobius(seed):
    r = rng(seed)
    n = r.randint(1, 4)
    t = [r.randint(-9, 9) for _ in range(1 << n)]
    c = _cosine_coefficients_by_quadrature(t)
    assert c == walsh(t)                   # 2^-n sum_T (-1)^{|S & T|} f(T)


def test_the_two_transforms_are_different_maps():
    t = [0, 1, 0, 0]                       # f = indicator of {0}
    assert _cosine_coefficients_by_quadrature(t) == [Fraction(1, 4), Fraction(-1, 4),
                                                     Fraction(1, 4), Fraction(-1, 4)]
    assert mobius(t) == [0, 1, 0, -1]      # the atoms: coordinates in the (1-cos)/2 basis


# ---- the two lifts differ at torsion points ----

def _theta_of_w(w):
    return [2 * math.asin(math.sqrt(float(wi))) for wi in w]   # branch in [0, pi]


def test_trap_is_a_spurious_minimum_of_multilinear_but_not_of_lovasz():
    fhat, f = mobius(TRAP), as_oracle(TRAP)
    th = [0.0, 1e-2, 1e-2]
    assert toric_multilinear(fhat, th) > 0      # F: theta = 0 is a strict local min
    assert toric_lovasz(f, th) < 0              # L o w: it is not a local min at all


@pytest.mark.parametrize("gen", GENERATORS)
@pytest.mark.parametrize("seed", range(6))
def test_lovasz_lift_has_no_spurious_torsion_minima(gen, seed):
    """For submodular f, every non-optimal torsion point of L o w has a descent
    path: w = x + s(1_A* - x) lowers L strictly by convexity, and its theta
    preimage is within O(sqrt s) of pi*x."""
    r = rng(500 + seed)
    n = r.randint(1, 6)
    t = table(gen(n, r), n)
    t = [v - t[0] for v in t]
    f = as_oracle(t)
    best = min(range(1 << n), key=lambda m: t[m])
    for x in range(1 << n):
        if t[x] == t[best]:
            continue
        for s in (Fraction(1, 100), Fraction(1, 10000)):
            w = [Fraction(x >> i & 1) + s * ((best >> i & 1) - (x >> i & 1)) for i in range(n)]
            assert lovasz(f, w) < t[x]                              # exact
            th = _theta_of_w(w)
            assert max(abs(a - b) for a, b in zip(th, torsion_point(x, n))) < 3 * math.sqrt(s)
            assert toric_lovasz(f, th) < t[x]                       # and on the torus
