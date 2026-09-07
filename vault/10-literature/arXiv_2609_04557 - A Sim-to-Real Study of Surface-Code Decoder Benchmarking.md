---
aliases: ["A Sim-to-Real Study of Surface-Code Decoder Benchmarking"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.04557"
url: "http://arxiv.org/abs/2609.04557v1"
published: "2026-09-03T23:24:40Z"
ingested: "2026-09-07T11:32:16Z"
authors:
  - "Shay J. Manor"
  - "Leila S. Erhili"
  - "Yassine Jebbouri"
---

# A Sim-to-Real Study of Surface-Code Decoder Benchmarking

## Abstract

> Quantum error-correction decoders are typically benchmarked against synthetic circuit-level
> noise, under the assumption that a decoder's ranking under such noise transfers to hardware and
> improves as the noise model becomes more realistic. The Willow processor, the first to operate
> below the surface-code threshold, allows us to test this assumption. We rank a panel of six
> decoders using a four-rung ladder of noise models with increasing fidelity, evaluated against
> real data across three code distances, two bases, and fifteen round counts. Rank agreement with
> hardware appears once the noise model gives each operation type its own error rate. Calibrating
> the model to the device improves absolute error rates but not rank agreement. We additionally
> provide the first independent evaluation of NVIDIA's Ising pre-decoder on hardware, at code
> distances below its training receptive field and via a mapping onto the lattice on which it was
> trained. Under these conditions, it holds no accuracy-latency advantage: another panel decoder
> matches or improves on it in both per-cycle error rate and decode latency in 278 of the 280
> evaluations. We release the full pipeline and the per-shot outcome of every evaluation, so
> future decoders and devices can be compared.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

