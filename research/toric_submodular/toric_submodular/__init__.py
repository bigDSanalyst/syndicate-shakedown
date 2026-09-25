"""Toric submodular engine - the corrected, working form of the
"Boolean lattice -> torus -> torsion points" framework.

See ../README.md for which claims of the source survive, which were corrected,
and which were removed.
"""
from .lattice import (coverage_counterexample, in_sign_cone, is_submodular, minimizer_lattice,
                      mobius, submodularity_witness, table, walsh, walsh_from_mobius, zeta)
from .extensions import (greedy_vertex, level_set_rounding, lovasz, lovasz_from_mobius,
                         morse_index, spurious_torus_minima, torsion_hessian, toric_fourier,
                         toric_lovasz, toric_multilinear)
from .solver import Result, minimize, verify_certificate
from .flow import sign_flow

__all__ = [n for n in dir() if not n.startswith("_")]
