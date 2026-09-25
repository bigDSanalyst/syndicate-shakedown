"""Layer 3 as specified - the toric sign flow - kept so it can be measured.

    theta_{k+1} = theta_k - dt_k * sign( dL(w(theta))/dtheta )

The source calls D(theta) = diag(1/|g_i|) a Riemannian metric. It is not one:
it depends on the gradient rather than the position, and is undefined wherever
g_i = 0 - which, because dw_i/dtheta_i = sin(theta_i)/2, is every coordinate at
0 or pi. The flow is coordinate-wise sign descent (signSGD). Consequences the
suite checks rather than asserts:

  * it cannot leave a torsion point: every sign there is 0. That includes
    torsion points that are not local minima of L o w (TRAP at theta = 0);
  * with a fixed dt every non-zero coordinate moves by dt at every step, so
    iterates settle only by landing exactly on a zero-sign point;
  * it carries no optimality guarantee. Level-set rounding of its iterates is
    monotone (never worse than L at the iterate) but nothing more.

Use `solver.minimize` for answers. Use this to study the flow.
"""
import math
from dataclasses import dataclass

from .extensions import level_set_rounding, toric_lovasz, toric_lovasz_subgradient, w_of_theta


def _sign(v, eps=0.0):
    return 0 if abs(v) <= eps else (1 if v > 0 else -1)


@dataclass
class FlowTrace:
    theta: list
    potential: list        # L(w(theta_k)) - f(empty) per step
    best_set: frozenset    # best level-set rounding seen
    best_value: object
    stalled_at_start: bool # zero sign vector at theta_0


def sign_flow(f, theta0, steps=200, dt=0.5, schedule="sqrt"):
    """Run the flow. schedule: 'const' (as specified) or 'sqrt' (dt/sqrt(k+1))."""
    if not 0 < dt <= 0.5:
        raise ValueError("the source specifies 0 < dt <= 0.5")
    theta = [t % (2 * math.pi) for t in theta0]
    f0 = f(frozenset())
    best, best_val = level_set_rounding(f, w_of_theta(theta))
    pot = [toric_lovasz(f, theta)]
    g0 = toric_lovasz_subgradient(f, theta)
    stalled = all(_sign(g, 1e-15) == 0 for g in g0)
    for k in range(steps):
        g = toric_lovasz_subgradient(f, theta)
        if all(_sign(gi, 1e-15) == 0 for gi in g):
            break
        h = dt if schedule == "const" else dt / math.sqrt(k + 1)
        theta = [(t - h * _sign(gi, 1e-15)) % (2 * math.pi) for t, gi in zip(theta, g)]
        pot.append(toric_lovasz(f, theta))
        A, v = level_set_rounding(f, w_of_theta(theta))
        if v < best_val:
            best, best_val = A, v
    return FlowTrace(theta, pot, best, best_val, stalled)
