---
aliases: ["Certification cost of quantum models: measurement correlation, not parameter count"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.14424"
url: "http://arxiv.org/abs/2609.14424v1"
published: "2026-09-13T10:47:03Z"
ingested: "2026-09-17T00:46:22Z"
authors:
  - "Pavel Sulimov"
  - "Claude Lehmann"
---

# Certification cost of quantum models: measurement correlation, not parameter count

## Abstract

> Reporting the Fisher geometry of a trained variational quantum model is routine; quoting the
> shot budget that would establish it is not. Certifying an empirical Fisher matrix to relative
> Frobenius error $\varepsilon$ under coordinate-wise parameter shift costs $Θ(B p^{2}
> V/(\varepsilon^{2} G))$ circuit executions, where $V$ is the measured readout variance and $G$
> the measured squared gradient norm, with uniform allocation optimal in that class. One constant
> reproduces the cost of two circuit families whose exponents differ by a full power of $p$. The
> exponent is an identity in how $nV$ and $nG$ scale with the register, holding family by family
> to $0.001$ across 624 matrix-product-state cells once the finite-$p$ prefactor is removed. The
> cubic cost is therefore a finite-size window, set by whether the readout light cone grows with
> the register. A product family to 256 qubits gives $1.966$ (95% CI $1.934$--$1.997$); a
> brickwork entangler falls from $2.853$ below ten qubits to $1.715$ beyond sixty-four; a blocked
> entangler gives $1.984$ at a fixed cone width against $3.034$ at a proportional one. Fixed
> device connectivity fixes the cone, so a cubic budget from a small simulation overestimates a
> large machine, on top of hardware multipliers $2.07\times$ ($1.41$--$3.02$), $2.38\times$ and
> $1.91\times$ on ibm_marrakesh, ibm_fez and ibm_kingston. Cost-optimal readout weights cut the
> measured shot budget by $2.67\times$ ($1.33$--$4.00$) on hardware, flat from four to twelve
> qubits. A discrepancy model fitted on cheap circuits transfers its mean inside the calibration
> grid and, at six larger sizes named before the data, does not: nominal 90% intervals cover 36%,
> and split conformal is the only rung that stays near nominal.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

