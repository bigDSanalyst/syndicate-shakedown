"""The engine - exact submodular minimization with a checkable certificate.

The source framework wants a continuous flow that "collapses" onto the exact
discrete optimum. The construction that actually does that is the
Fujishige-Wolfe minimum-norm-point algorithm on the base polytope B(f):

  * x* = argmin { ||x|| : x in B(f) }  is a continuous object;
  * A_min = {i : x*_i < 0} and A_max = {i : x*_i <= 0} are the smallest and
    largest minimizers of f (Fujishige 1980), and every minimizer lies between
    them - the minimizer set is a lattice;
  * f(A_min) - f(empty) = sum_i min(x*_i, 0)  (Edmonds' min-max theorem),
    which is a certificate anyone can check.

Arithmetic: a float pass finds the corral quickly; an exact pass over Fraction,
warm-started from it, finishes the job so the certificate is exact. With a
rational-valued oracle nothing in the returned result is approximate.

What the certificate proves, and what it does not: `verify_certificate`
recomputes every greedy vertex from the oracle and checks the duality gap is
exactly zero. That proves A optimal *provided f is submodular* - for a
non-submodular f greedy vectors need not lie in B(f). For a tabulated f,
`verify_certificate(..., check_submodular=True)` checks that too.
"""
from dataclasses import dataclass, field
from fractions import Fraction

from .extensions import greedy_vertex


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _affine_min_norm(V, exact):
    """Coefficients alpha (sum 1) of the min-norm point of aff(V), or None.

    Solves [G 1; 1^T 0][alpha; mu] = [0; 1], G = V V^T.
    """
    k = len(V)
    A = [[_dot(V[i], V[j]) for j in range(k)] + [1, 0] for i in range(k)]
    A.append([1] * k + [0, 1])
    m = k + 1
    for c in range(m):
        if exact:
            p = next((r for r in range(c, m) if A[r][c] != 0), None)
        else:
            p = max(range(c, m), key=lambda r: abs(A[r][c]))
            if abs(A[p][c]) < 1e-14:
                p = None
        if p is None:
            return None
        A[c], A[p] = A[p], A[c]
        piv = A[c][c]
        A[c] = [v / piv for v in A[c]]
        for r in range(m):
            if r != c and A[r][c] != 0:
                fac = A[r][c]
                A[r] = [a - fac * b for a, b in zip(A[r], A[c])]
    return [A[i][m] for i in range(k)]


@dataclass
class _Corral:
    orders: list
    verts: list
    lam: list

    def point(self, n):
        return [sum(l * v[i] for l, v in zip(self.lam, self.verts)) for i in range(n)]


def _minor(c, exact, tol):
    """Wolfe's minor cycle: move to the min-norm point of aff(corral), pruning
    vertices whose weight hits zero on the way. False if the corral is
    affinely dependent."""
    while True:
        alpha = _affine_min_norm(c.verts, exact)
        if alpha is None:
            return False
        if all(a > tol for a in alpha):
            c.lam = list(alpha)
            return True
        theta = min(l / (l - a) for l, a in zip(c.lam, alpha) if a <= tol and l - a > 0)
        lam = [theta * a + (1 - theta) * l for l, a in zip(c.lam, alpha)]
        keep = [i for i, l in enumerate(lam) if l > tol]
        s = sum(lam[i] for i in keep)
        c.orders = [c.orders[i] for i in keep]
        c.verts = [c.verts[i] for i in keep]
        c.lam = [lam[i] / s for i in keep]


def _wolfe(f, n, c, exact, max_iter, f0):
    """Major cycle. Returns (x, iterations, converged)."""
    num = Fraction if exact else float
    tol = 0 if exact else 1e-12
    x = c.point(n)
    for it in range(1, max_iter + 1):
        order = sorted(range(n), key=lambda i: x[i])
        q = [num(v) for v in greedy_vertex(f, order, f0)]
        scale = max(1, max(_dot(v, v) for v in c.verts + [q]))
        if _dot(x, x) - _dot(x, q) <= tol * scale:
            return x, it, True          # <x, y> >= ||x||^2 for all y in B(f)
        c.orders.append(order); c.verts.append(q); c.lam.append(num(0))
        if not _minor(c, exact, tol):
            if exact:
                raise ArithmeticError("affinely dependent corral in exact pass")
            c.orders.pop(); c.verts.pop(); c.lam.pop()
            return x, it, False
        x_new = c.point(n)
        if x_new == x:                  # float stall: nothing left to gain
            return x, it, not exact
        x = x_new
    return x, max_iter, False


@dataclass
class Result:
    value: object                 # min f, in the oracle's own units
    minimal: frozenset            # smallest minimizer
    maximal: frozenset            # largest minimizer
    certificate: dict             # see verify_certificate
    certified: bool               # exact duality gap == 0
    iterations: dict = field(default_factory=dict)


def minimize(f, n, exact=True, max_iter=10_000):
    """Minimize a submodular oracle f(frozenset) on V = {0..n-1}.

    exact=True polishes in Fraction arithmetic and requires rational values.
    """
    f0 = f(frozenset())
    if n == 0:
        cert = {"n": 0, "set": [], "value": str(f0), "orders": [], "weights": []}
        return Result(f0, frozenset(), frozenset(), cert, True)
    order0 = list(range(n))
    v0 = [float(v) for v in greedy_vertex(f, order0, f0)]
    c = _Corral([order0], [v0], [1.0])
    _, it_f, conv = _wolfe(f, n, c, False, max_iter, f0)
    iters = {"float": it_f, "float_converged": conv}
    if exact:
        k = len(c.orders)
        verts = [[Fraction(v) for v in greedy_vertex(f, o, f0)] for o in c.orders]
        ce = _Corral(list(c.orders), verts, [Fraction(1, k)] * k)
        if not _minor(ce, True, 0):     # float corral degenerate: restart small
            best = max(range(k), key=lambda i: c.lam[i])
            ce = _Corral([c.orders[best]], [verts[best]], [Fraction(1)])
        x, it_e, conv = _wolfe(f, n, ce, True, max_iter, f0)
        iters.update(exact=it_e, exact_converged=conv)
        c = ce
    else:
        x = c.point(n)
    tol = 0 if exact else 1e-9
    A_min = frozenset(i for i in range(n) if x[i] < -tol)
    A_max = frozenset(i for i in range(n) if x[i] <= tol)
    val = f(A_min)
    cert = {
        "n": n,
        "set": sorted(A_min),
        "value": str(val),
        "orders": [list(o) for o in c.orders],
        "weights": [str(l) for l in c.lam],
    }
    ok = verify_certificate(f, cert)[0] if exact else False
    return Result(val, A_min, A_max, cert, ok, iters)


def verify_certificate(f, cert, check_submodular=False):
    """Independent exact check. Returns (ok, reason).

    Recomputes x = sum_j lambda_j * greedy(order_j) from the oracle and checks
    lambda >= 0, sum lambda = 1, and f(A) - f(empty) == sum_i min(x_i, 0).
    Weak duality (x in B(f) => x(B) <= f(B) - f(empty) for all B, and
    x(B) >= sum min(x_i, 0)) then makes A a global minimizer - given f
    submodular. Pass check_submodular=True for small n to check that as well.
    """
    n = cert["n"]
    lam = [Fraction(s) for s in cert["weights"]]
    orders = cert["orders"]
    if len(lam) != len(orders):
        return False, "weights and orders differ in length"
    if any(sorted(o) != list(range(n)) for o in orders):
        return False, "an order is not a permutation of V"
    if any(l < 0 for l in lam):
        return False, "negative weight"
    if n and sum(lam) != 1:
        return False, f"weights sum to {sum(lam)}, not 1"
    f0 = Fraction(f(frozenset()))
    x = [Fraction(0)] * n
    for l, o in zip(lam, orders):
        v = greedy_vertex(f, o, f0)
        for i in range(n):
            x[i] += l * Fraction(v[i])
    A = frozenset(cert["set"])
    fA = Fraction(f(A))
    if str(f(A)) != cert["value"] and Fraction(cert["value"]) != fA:
        return False, "recorded value does not match f(set)"
    lower = sum(min(xi, 0) for xi in x)
    if fA - f0 != lower:
        return False, f"duality gap {fA - f0 - lower} != 0"
    if check_submodular:
        from .lattice import is_submodular, table
        if not is_submodular(table(f, n)):
            return False, "f is not submodular; greedy vectors need not lie in B(f)"
    return True, "exact duality gap is zero"
