---
aliases: ["EFI Pairs Without One-Way Puzzles: Oracle Separations from Communication Complexity"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.11901"
url: "http://arxiv.org/abs/2609.11901v1"
published: "2026-09-10T17:54:55Z"
ingested: "2026-09-11T10:34:44Z"
authors:
  - "Atul Mantri"
---

# EFI Pairs Without One-Way Puzzles: Oracle Separations from Communication Complexity

## Abstract

> EFI pairs (Brakerski, Canetti, and Qian, ITCS 2023) and one-way puzzles (Khurana and Tomer, STOC
> 2024) are the leading candidates for the minimal assumption of quantum cryptography. The first
> are efficiently preparable quantum states, statistically far yet computationally
> indistinguishable; the second are classical puzzles, easy to sample and hard to solve. One-way
> puzzles imply EFI pairs, and whether the converse holds is open. We construct a single classical
> oracle relative to which one-way puzzles do not exist, even with an unbounded verifier, while an
> EFI pair survives every distinguisher that queries the oracle classically throughout and holds
> advice about it, making its one superposition query at the end. The oracle answers every
> question about the output probabilities of quantum samplers, which removes the puzzles, and
> hides a Haar-random half-dimensional subspace. To prove security we reduce it to communication
> complexity. An adversary whose knowledge of the subspace arrives as classical query answers can
> be simulated inside a two-party protocol against the party holding it, so it does no better than
> the best classical protocol for Vector-in-Subspace (Klartag and Regev, STOC 2011), whatever the
> oracle computes. That argument does not cover the superposition query, which we bound instead
> using tools from random matrix theory. The same attack gives a classical simulation of any
> quantum party in a classical-message protocol with no entanglement shared in advance, so
> relative to the oracle there is no proof of quantumness either. Quantum polynomial time
> therefore offers no advantage on any task with classical inputs and outputs, while the two
> quantum states stay indistinguishable. We state conjectures on removing the restriction on
> superposition queries.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

