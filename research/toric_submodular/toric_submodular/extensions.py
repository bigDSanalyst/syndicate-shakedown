"""Layers 2-4 - continuous extensions, the torus, and what its topology says.

Two extensions of a set function f (normalized f(empty) = 0) to w in [0,1]^n:

  Lovasz       L(w) = sum_S fhat(S) min_{i in S} w_i  = max_{x in B(f)} <w, x>
  multilinear  M(w) = sum_S fhat(S) prod_{i in S} w_i

L is convex iff f is submodular (Lovasz 1983). Both are pulled back to the
torus T^n = (R/2piZ)^n by w_i = sin^2(theta_i/2) = (1 - cos theta_i)/2, which is
2-to-1 onto [0,1]^n and hits the vertices exactly at the 2-torsion points
T^n[2] = {0, pi}^n.

What survives from the source framework, and what does not:

* No boundary, so no KKT multipliers: true - theta is unconstrained.
* "Convexity survives on the torus": false. A geodesically convex function on a
  compact manifold is constant, so L(w(theta)) cannot be convex unless f is.
* The pullback of the multilinear extension is a trigonometric polynomial whose
  cosine coefficients are *exactly* the Walsh-Fourier coefficients of f:
      F(theta) = sum_S c(S) prod_{i in S} cos theta_i.
  At theta = pi*x it equals f(x). This is the real content of "torsion points
  carry the discrete truth": Pontryagin duality on (Z/2)^n, not class field
  theory.
* Local minima: the two lifts behave differently, and the chi(T^n) = 0
  argument proves nothing about either. It fixes only the signed count of
  critical points.
  - Multilinear lift F. Every torsion point is critical (dw/dtheta =
    sin(theta)/2 = 0), and the Hessian there is diagonal with entries
    (f(x xor e_i) - f(x))/2, the single-flip gains (`torsion_hessian`). The
    Morse index is the number of improving flips. So every strict 1-flip local
    minimum of f is a strict local minimum of F, and submodular f do have
    non-global ones (TRAP in tests/test_torus.py).
  - Lovasz lift L o w, the potential the source framework names. For
    submodular f it has no spurious local minima. L is convex on the cube,
    and w = sin^2(theta/2) maps every neighbourhood of theta onto a relative
    neighbourhood of w(theta) in [0,1]^n. So a local minimum of L o w is a
    local minimum of L on the cube, hence global. At TRAP's theta = 0 the lift
    descends along (0, s, s).
  The sign flow fails anyway (flow.py). The chain-rule subgradient vanishes at
  every torsion point, minimum or not, so it stalls at points that are not
  minima of the potential it is descending.
"""
import math
from fractions import Fraction

from .lattice import members, mobius, popcount


# ---------------------------------------------------------------- greedy / Lovasz

def greedy_vertex(f, order, f_empty=None):
    """Vertex of the base polytope B(f) for a permutation `order` of V.

    x[order[k]] = f(S_k) - f(S_{k-1}), S_k = first k+1 elements. With f
    submodular this is an extreme point of B(f) (Edmonds 1970).
    """
    x = [0] * len(order)
    prev = f(frozenset()) if f_empty is None else f_empty
    S = set()
    for i in order:
        S.add(i)
        cur = f(frozenset(S))
        x[i] = cur - prev
        prev = cur
    return x


def lovasz(f, w):
    """L(w) - f(empty), by the greedy formula; n oracle calls."""
    order = sorted(range(len(w)), key=lambda i: -w[i])
    x = greedy_vertex(f, order)
    return sum(wi * xi for wi, xi in zip(w, x))


def lovasz_subgradient(f, w):
    """A subgradient of L at w: the greedy vertex for w sorted descending."""
    return greedy_vertex(f, sorted(range(len(w)), key=lambda i: -w[i]))


def lovasz_from_mobius(fhat, w):
    """sum_S fhat(S) min_{i in S} w_i  (table form, for cross-checking)."""
    total = 0
    for m, a in enumerate(fhat):
        if m and a:
            total += a * min(w[i] for i in members(m))
    return total


def level_set_rounding(f, w):
    """Best level set {i : w_i >= t}. Guarantees f(A) - f(empty) <= L(w).

    L(w) = sum_k (w_(k) - w_(k+1)) f(S_k) is a sub-convex combination of the
    level sets' values (and f(empty)), so the best of them is no worse. This is
    the exact, provable "collapse" of a continuous point to a lattice point.
    """
    n = len(w)
    order = sorted(range(n), key=lambda i: -w[i])
    best, best_val, S = frozenset(), f(frozenset()), set()
    for i in order:
        S.add(i)
        v = f(frozenset(S))
        if v < best_val:
            best, best_val = frozenset(S), v
    return best, best_val


# ---------------------------------------------------------------- the torus

def w_of_theta(theta):
    return [math.sin(t / 2) ** 2 for t in theta]


def toric_lovasz(f, theta):
    return lovasz(f, w_of_theta(theta))


def toric_lovasz_subgradient(f, theta):
    """Chain rule: dL/dtheta_i = g_i(w) * sin(theta_i) / 2."""
    g = lovasz_subgradient(f, w_of_theta(theta))
    return [gi * math.sin(t) / 2 for gi, t in zip(g, theta)]


def toric_multilinear(fhat, theta):
    """F(theta) = sum_S fhat(S) prod_{i in S} sin^2(theta_i/2)."""
    w = w_of_theta(theta)
    total = 0.0
    for m, a in enumerate(fhat):
        if a:
            p = float(a)
            for i in members(m):
                p *= w[i]
            total += p
    return total


def toric_fourier(c, theta):
    """F(theta) = sum_S c(S) prod_{i in S} cos theta_i, c = walsh(f)."""
    cs = [math.cos(t) for t in theta]
    total = 0.0
    for m, a in enumerate(c):
        if a:
            p = float(a)
            for i in members(m):
                p *= cs[i]
            total += p
    return total


def torsion_point(x_mask, n):
    """theta = pi * x for a vertex x of the cube."""
    return [math.pi if x_mask >> i & 1 else 0.0 for i in range(n)]


def torsion_hessian(f, x_mask):
    """Exact Hessian of F at the torsion point pi*x (table f).

    Diagonal, with H_ii = (f(x xor e_i) - f(x)) / 2; off-diagonal terms carry a
    factor sin(theta_i) sin(theta_j) and vanish. Returned as a list of the
    diagonal entries, as Fractions.
    """
    n = len(f).bit_length() - 1
    return [Fraction(f[x_mask ^ (1 << i)] - f[x_mask], 2) for i in range(n)]


def morse_index(f, x_mask):
    """(index, nullity) of the torsion point pi*x as a critical point of F."""
    h = torsion_hessian(f, x_mask)
    return sum(1 for v in h if v < 0), sum(1 for v in h if v == 0)


def spurious_torus_minima(f):
    """Torsion points that are strict local minima of the multilinear lift F
    but not global minima of f. (The Lovasz lift has none for submodular f;
    see the module docstring.)
    """
    n = len(f).bit_length() - 1
    lo = min(f)
    out = []
    for m in range(1 << n):
        if f[m] > lo and all(v > 0 for v in torsion_hessian(f, m)):
            out.append(m)
    return out
