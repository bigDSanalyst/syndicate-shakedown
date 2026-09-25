"""Layer 1: exact transforms and the sign-cone correction."""
from fractions import Fraction

import pytest
from conftest import GENERATORS, rng

from toric_submodular.lattice import (coverage_counterexample, in_sign_cone, is_submodular,
                                      minimizer_lattice, mobius, popcount,
                                      submodularity_witness, table, walsh, walsh_from_mobius, zeta)


def random_table(n, r):
    return [Fraction(r.randint(-9, 9), r.randint(1, 4)) for _ in range(1 << n)]


@pytest.mark.parametrize("seed", range(20))
def test_mobius_inverts_zeta(seed):
    r = rng(seed)
    t = random_table(r.randint(0, 6), r)
    assert zeta(mobius(t)) == t and mobius(zeta(t)) == t


@pytest.mark.parametrize("seed", range(20))
def test_walsh_coefficients_from_atoms(seed):
    r = rng(seed)
    t = random_table(r.randint(0, 6), r)
    assert walsh(t) == walsh_from_mobius(mobius(t))


def test_walsh_inverts():
    t = [3, -1, 4, 1, -5, 9, 2, -6]
    c = walsh(t)
    back = [sum(c[S] * (-1) ** popcount(S & A) for S in range(8)) for A in range(8)]
    assert back == t


@pytest.mark.parametrize("seed", range(20))
def test_sign_cone_implies_submodular(seed):
    r = rng(seed)
    n = r.randint(2, 6)
    atoms = [0] + [r.randint(-5, 5) if popcount(m) == 1 else -r.randint(0, 3)
                   for m in range(1, 1 << n)]
    t = zeta(atoms)
    assert in_sign_cone(t)
    assert is_submodular(t)


def test_sign_cone_is_strictly_smaller():
    t = coverage_counterexample()
    assert is_submodular(t)
    assert not in_sign_cone(t)
    assert mobius(t)[0b111] == 1


def test_witness_is_a_real_violation():
    t = [0, 1, 1, 3]  # supermodular: f(12) + f(0) > f(1) + f(2)
    A, i, j = submodularity_witness(t)
    assert (A, i, j) == ([], 0, 1)
    assert not is_submodular(t)


@pytest.mark.parametrize("gen", GENERATORS)
@pytest.mark.parametrize("seed", range(8))
def test_generators_are_submodular_and_minimizers_form_a_lattice(gen, seed):
    r = rng(seed)
    n = r.randint(1, 7)
    t = table(gen(n, r), n)
    assert is_submodular(t)
    mins = minimizer_lattice(t)
    for a in mins:
        for b in mins:
            assert a | b in mins and a & b in mins


def test_sign_cone_includes_pairwise_atoms():
    t = [0, 1, 1, 3]            # fhat({0,1}) = +1: supermodular, outside the cone
    assert mobius(t)[0b11] == 1
    assert not in_sign_cone(t)
