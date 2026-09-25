"""The engine: exact minimization, against brute force and against max-flow."""
from collections import deque
from fractions import Fraction

import pytest
from conftest import GENERATORS, as_oracle, rng

from toric_submodular.lattice import members, minimizer_lattice, table
from toric_submodular.solver import minimize, verify_certificate


@pytest.mark.parametrize("gen", GENERATORS)
@pytest.mark.parametrize("seed", range(15))
def test_matches_brute_force_including_extreme_minimizers(gen, seed):
    r = rng(1000 + seed)
    n = r.randint(1, 10)
    f = gen(n, r)
    t = table(f, n)
    res = minimize(f, n)
    mins = minimizer_lattice(t)
    lo = hi = mins[0]
    for m in mins:
        lo &= m
        hi |= m
    assert res.certified, res.certificate
    assert res.value == min(t)
    assert res.minimal == frozenset(members(lo))
    assert res.maximal == frozenset(members(hi))
    assert verify_certificate(f, res.certificate, check_submodular=True)[0]


def test_rational_values_stay_exact():
    t = [Fraction(0), Fraction(1, 3), Fraction(1, 7), Fraction(-2, 21)]
    res = minimize(as_oracle(t), 2)
    assert res.certified and res.value == Fraction(-2, 21)


def test_empty_ground_set():
    res = minimize(lambda A: 5, 0)
    assert res.certified and res.value == 5


def _max_flow(cap, s, t):
    """Edmonds-Karp on a dense capacity matrix - an independent oracle."""
    n = len(cap)
    flow = 0
    res = [row[:] for row in cap]
    while True:
        par = [-1] * n
        par[s] = s
        q = deque([s])
        while q and par[t] < 0:
            u = q.popleft()
            for v in range(n):
                if par[v] < 0 and res[u][v] > 0:
                    par[v] = u
                    q.append(v)
        if par[t] < 0:
            return flow
        b, v = float("inf"), t
        while v != s:
            b = min(b, res[par[v]][v]); v = par[v]
        v = t
        while v != s:
            res[par[v]][v] -= b; res[v][par[v]] += b; v = par[v]
        flow += b


@pytest.mark.parametrize("seed", range(3))
def test_large_s_t_cut_matches_max_flow(seed):
    r = rng(seed)
    n = 40
    E = [(i, j, r.randint(1, 5)) for i in range(n) for j in range(i + 1, n) if r.random() < 0.12]
    src = [r.randint(0, 9) for _ in range(n)]   # s -> i, paid when i not in A
    snk = [r.randint(0, 9) for _ in range(n)]   # i -> t, paid when i in A
    f = lambda A: (sum(w for i, j, w in E if (i in A) != (j in A))
                   + sum(snk[i] for i in A) + sum(src[i] for i in range(n) if i not in A))
    cap = [[0] * (n + 2) for _ in range(n + 2)]
    s, t = n, n + 1
    for i, j, w in E:
        cap[i][j] += w; cap[j][i] += w
    for i in range(n):
        cap[s][i] += src[i]; cap[i][t] += snk[i]
    res = minimize(f, n)
    assert res.certified
    assert res.value == _max_flow(cap, s, t)


def _cert():
    t = [0, 7, 1, 4, 2, 7, -1, 0]
    f = as_oracle(t)
    return f, minimize(f, 3).certificate


def test_certificate_verifies():
    f, c = _cert()
    assert verify_certificate(f, c) == (True, "exact duality gap is zero")


@pytest.mark.parametrize("tamper, reason", [
    (lambda c: c.update(set=[1], value="1"), "gap"),
    (lambda c: c.update(value="-2"), "recorded value"),
    (lambda c: c["weights"].__setitem__(0, str(Fraction(c["weights"][0]) + 1)), "sum"),
    (lambda c: c["orders"].__setitem__(0, [0, 0, 1]), "permutation"),
    (lambda c: c["weights"].pop(), "length"),
])
def test_tampered_certificates_are_refused(tamper, reason):
    f, c = _cert()
    tamper(c)
    ok, why = verify_certificate(f, c)
    assert not ok and reason in why


def test_negative_weight_refused():
    f, c = _cert()
    c["orders"].append(c["orders"][0]); c["weights"] = [str(Fraction(w)) for w in c["weights"]]
    c["weights"].append("-1"); c["weights"][0] = str(Fraction(c["weights"][0]) + 1)
    ok, why = verify_certificate(f, c)
    assert not ok and "negative" in why


def test_non_submodular_is_refused_when_asked():
    t = [0, 1, -5, 1]                            # not submodular; min is f({1}) = -5
    f = as_oracle(t)
    c = {"n": 2, "set": [], "value": "0", "orders": [[0, 1]], "weights": ["1"]}
    assert verify_certificate(f, c)[0]           # zero gap, yet the empty set is not optimal
    ok, why = verify_certificate(f, c, check_submodular=True)
    assert not ok and "not submodular" in why


def test_float_mode_does_not_claim_a_certificate():
    f = as_oracle([0, 7, 1, 4, 2, 7, -1, 0])
    res = minimize(f, 3, exact=False)
    assert res.value == -1 and not res.certified
