---
aliases: ["Conditional Quantum Flow Matching for Data-Scarce Physiological Signal Augmentation"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.14019"
url: "http://arxiv.org/abs/2609.14019v1"
published: "2026-09-12T16:06:56Z"
ingested: "2026-09-17T00:46:22Z"
authors:
  - "Chi-Sheng Chen"
  - "Samuel Yen-Chi Chen"
---

# Conditional Quantum Flow Matching for Data-Scarce Physiological Signal Augmentation

## Abstract

> Generative augmentation is a standard remedy for label scarcity in physiological signal
> classification, but existing quantum generative models start from uninformative noise, ignoring
> class structure that is already available. We propose Conditional Quantum Flow Matching (CQFM):
> a single 306-parameter circuit, conditioned on both flow time and class label, transports a
> compact class-conditional prior toward the target distribution. Quantum flow matching as
> published is unconditional, so this is to our knowledge the first conditional one, and the first
> EEG augmentation on a parameterized quantum circuit. A nonnegative spectral embedding removes
> the need for tomography at readout. On BCI Competition IV-2a, starting from a prior rather than
> noise is worth $+5.1$ accuracy points over QuDDPM (9/9 subjects), though at that operating point
> a class-conditional Gaussian matches CQFM. Where the prior fails the transport earns its keep:
> given one transferred from other subjects it regains $+7.2$ TSTR points (9/9).

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

