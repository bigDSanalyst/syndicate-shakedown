# Toric submodular engine

A working, tested form of the "Boolean lattice → torus → torsion points"
framework. It keeps the parts of the original that are true, fixes the parts
that are false, and replaces the part that does not work (the sign flow as an
optimizer) with one that does: exact submodular minimization that returns a
**certificate anyone can check**.

```
python3 -m toric_submodular            # run from this directory; walks every layer
python3 -m pytest -q tests             # 204 tests, pure Python 3.11, no numpy
```

Pure standard library. Values stay in `int`/`Fraction` from start to finish,
so nothing you get back has been rounded.

## The corrected framework, layer by layer

| Layer | Original claim | Status | What is actually true (and where it is tested) |
|---|---|---|---|
| 1 | Möbius atoms f̂(S) decompose f uniquely | **True** | `lattice.mobius` / `zeta`, O(n 2ⁿ), exact (`test_mobius_inverts_zeta`) |
| 1 | Submodularity ⇔ sign cone M₋ (f̂(S) ≤ 0) | **Corrected** | M₋ ⇒ submodular, **but not the other way round**. A coverage function is submodular and has f̂({0,1,2}) = +1 (`test_sign_cone_is_strictly_smaller`). What submodularity actually requires: for every A, i, j, the sum of f̂(S) over {i,j} ⊆ S ⊆ A∪{i,j} is ≤ 0. |
| 1 | M₋ "guarantees convexity" | **Corrected** | Lovász extension L(w) = Σ f̂(S) min_{i∈S} wᵢ is convex on [0,1]ⁿ **iff f is submodular**, which is weaker than M₋ (`test_lovasz_greedy_equals_mobius_form`) |
| 2 | w = sin²(θ/2) embeds into Tⁿ, no boundary, no KKT | **True** | θ needs no constraints. But the map is 2-to-1 and dw/dθ vanishes at every θᵢ ∈ {0, π} |
| 2 | Convexity survives on the torus | **False** | On a compact manifold, a geodesically convex function has to be constant. L(w(θ)) is not convex |
| 2 | "Pontryagin duality" | **Made precise** | Pull the multilinear extension back to the torus and you get a trigonometric polynomial, F(θ) = Σ_S c(S) Π_{i∈S} cos θᵢ. Its coefficients c are **exactly the Walsh–Fourier coefficients of f**, i.e. Fourier analysis on Tⁿ[2] ≅ (ℤ/2)ⁿ (`test_walsh_coefficients_from_atoms`, `test_toric_potential_is_the_walsh_series…`) |
| 3 | D(θ) = diag(1/\|gᵢ\|) is a Riemannian metric; sign descent is stable | **False** | D depends on the gradient, not on position, and it is undefined wherever gᵢ = 0. At every torsion point, gᵢ = 0 in every coordinate. So the flow is signSGD, and it cannot leave a torsion point (`flow.py`, `test_specified_flow_stalls…`) |
| 4 | Poincaré–Hopf (χ(Tⁿ) = 0) rules out false minima | **False** | χ = 0 only fixes the signed count of critical points. **New exact result:** every torsion point πx is a critical point of F, and its Hessian is diagonal with H_ii = (f(x⊕eᵢ) − f(x))/2. So its Morse index is its number of improving single flips. Every 1-flip local minimum of f is therefore a local minimum on the torus, and submodular f do have non-global ones: `TRAP = [0,7,1,4,2,7,-1,0]` (`test_torsion_hessian_is_half_the_flip_gains`, `test_trap_is_submodular_and_a_spurious_minimum`) |
| 4 | Tarski ⇒ the flow ends at a lattice fixed point | **Replaced** | The true lattice statement: for submodular f, **the minimizers form a sublattice**, closed under ∪ and ∩. Its bottom and top elements are read off one continuous point, the min-norm point x* of the base polytope: A_min = {x* < 0}, A_max = {x* ≤ 0} (Fujishige 1980) (`test_…minimizers_form_a_lattice`, `test_matches_brute_force_including_extreme_minimizers`) |
| 5 | Atoms are prime ideals; Kronecker–Weber extraction | **Removed** | f̂(S) are real numbers, not ideals, and no abelian extension of ℚ is involved. The honest algebra: functions on {0,1}ⁿ form the ring ℝ[x]/(xᵢ² − xᵢ). Its maximal ideals (xᵢ − aᵢ) correspond one-to-one to vertices, which are the torsion points. The atoms are coordinates in its monomial basis |
| — | "Zero-friction collapse" to the exact answer | **Built** | `solver.minimize`, below |

## The engine

`minimize(f, n)` runs the Fujishige–Wolfe minimum-norm-point algorithm on the
base polytope B(f). It takes only a value oracle, `f(frozenset) -> number`, and
calls it about n times per iteration, so n is bounded by time, not by 2ⁿ.

1. A float pass finds the active vertex set (the corral).
2. An exact `Fraction` pass starts from that corral and finishes the job.
3. What you get back: min f, the smallest and largest minimizers, and a
   certificate `{set, value, orders, weights}`.

`verify_certificate(f, cert)` is independent of the solver. It rebuilds every
greedy vertex from the oracle and checks that the weights are a convex
combination. It then checks that f(A) − f(∅) = Σᵢ min(xᵢ, 0) exactly. By
Edmonds' min–max theorem, that proves A is a global minimizer.

**What the certificate does not prove:** it assumes f is submodular. For a
non-submodular f, greedy vectors can fall outside B(f), and a zero gap then
proves nothing. `test_non_submodular_is_refused_when_asked` builds exactly that
false certificate. For small n, pass `check_submodular=True` to have the
verifier check submodularity too. For a large oracle, submodularity is an
assumption about your function, and you should state it.

Cross-checks:
- Brute force over every subset, for three families of submodular functions
  (cut + modular, concave-of-cardinality + modular, facility location −
  modular), n ≤ 10. The value and both extreme minimizers must match exactly.
- An independent Edmonds–Karp max-flow at n = 40 (s–t min cut).
- The demo solves an n = 50 instance (2⁵⁰ subsets) and certifies it in about
  1 s.

## Mutation testing

Following this repository's standard (CLAUDE.md), 11 mutations were applied one
at a time, each run with bytecode caching disabled:

- the minimal-minimizer threshold;
- the three certificate checks: duality gap, negative weights, weight sum;
- Wolfe's minor cycle;
- the Hessian factor ½;
- the greedy sort direction;
- the last level set in rounding;
- the Walsh sign;
- the submodularity inequality;
- the sign-cone order;
- the flow stall flag.

The suite failed under every one. The sign-cone mutation survived at first,
and `test_sign_cone_includes_pairwise_atoms` was added to catch it.

## Scope

This is research code under `research/`. It is not inherited template
machinery, and CI does not run it (`verify-claims.yml` runs `tests/` only). It
makes no ledger claim. Recording one would be a member's act, and an agent may
author a claim but not review or approve it.
