---
aliases: ["Classical Active-Space Hybrid Quantum Subspace Expansion (CASH-QSE): Quantum Corrections without Remeasuring the Classically Calculable Energy"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.08170"
url: "http://arxiv.org/abs/2609.08170v1"
published: "2026-09-08T02:59:48Z"
ingested: "2026-09-09T10:43:58Z"
authors:
  - "Artur F. Izmaylov"
---

# Classical Active-Space Hybrid Quantum Subspace Expansion (CASH-QSE): Quantum Corrections without Remeasuring the Classically Calculable Energy

## Abstract

> The wave function prepared by a variational quantum eigensolver (VQE) can contain a substantial
> classically tractable component, yet its energy contribution is sampled on the quantum device.
> Representing the wave function as a combination of a classical reference and separately prepared
> quantum states allows the reference energy to be evaluated without quantum sampling. However,
> near-linear dependence among these components can amplify measurement errors and destabilize the
> resulting energy estimate. We introduce Classical Active-Space Hybrid Quantum Subspace Expansion
> (CASH-QSE), which retains a complete-active-space self-consistent field (CASSCF) reference
> classically and uses occupation structure to construct quantum states exactly orthogonal to the
> reference and to one another. The energy follows from an ordinary Hermitian eigenvalue problem
> without overlap measurements, while the same occupation constraints simplify the measured
> operators. Using full configuration interaction to guide component selection, we test CASH-QSE
> along H$_2$O and N$_2$ bond-stretching coordinates spanning weakly to strongly correlated
> regimes. The benchmarks use STO--3G for both molecules and a restricted cc-pVDZ orbital space
> for H$_2$O. CASH-QSE reaches chemical accuracy while limiting the largest complete measurement
> circuits to a few hundred all-to-all logical controlled-NOT gates. In favorable cases, it also
> reduces the idealized final-energy sampling cost by several orders of magnitude relative to VQE
> with an adaptive derivative-assembled pseudo-Trotter ansatz (ADAPT-VQE).

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

