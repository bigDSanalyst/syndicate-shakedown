---
aliases: ["Near-Optimal Quantum Lower Bounds for Convex Optimization via Fourier Rank"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.09035"
url: "http://arxiv.org/abs/2609.09035v1"
published: "2026-09-08T17:01:51Z"
ingested: "2026-09-09T10:43:58Z"
authors:
  - "Brandon Augustino"
  - "Shouvanik Chakrabarti"
  - "Enrico Fontana"
  - "Dylan Herman"
  - "Junhyung Lyle Kim"
  - "Guneykan Ozgul"
  - "Nadezhda Voronova"
---

# Near-Optimal Quantum Lower Bounds for Convex Optimization via Fourier Rank

## Abstract

> We establish a near-linear quantum query lower bound for high-accuracy convex optimization over
> an explicit family of $n$-dimensional ellipsoids. We focus on linear optimization with an
> explicitly given objective, where the feasible set is accessed through a membership oracle. We
> show that any algorithm that, for every unit linear objective, returns an exactly feasible point
> with additive objective error $Θ(n^{-2})$ requires $Ω\!\left(\frac{n}{\log n\,\log\log
> n}\right)$ membership queries. The same lower bound can be shown to hold if the returned point
> is only required to be approximately feasible, within $Θ(n^{-2})$ distance from the feasible
> set. This resolves, up to logarithmic factors, an open question posed by Chakrabarti, Childs,
> Li, and Wu~(\textit{Quantum}, 2020) and by van Apeldoorn, Gilyén, Gribling, and de
> Wolf~(\textit{Quantum}, 2020). Coupled with the upper bounds in these papers, the query
> complexity of high-accuracy convex optimization is characterized tightly up to logarithmic
> factors. The proof is built around a lower bound for determinant computation that is derived via
> a novel polynomial method based on Fourier-rank. In the continuous matrix phase-query model,
> computing the determinant of a real $n\times n$ matrix requires at least $n/2$ matrix-vector
> product queries. The construction also yields an $Ω(n)$ phase-query lower bound for estimating
> the minimum eigenvalue of a real symmetric $n\times n$ matrix to additive accuracy $Θ(n^{-2})$.
> These results extend the determinant and minimum-eigenvalue lower bounds of Childs, Hung, and
> Li~(ICALP 2021) from finite fields to the real-valued setting. Based on the same constructions,
> we also prove a near-optimal gradient-query lower bound for constant-accuracy optimization of
> smooth and strongly convex functions.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

