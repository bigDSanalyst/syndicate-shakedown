---
aliases: ["Likelihood-free inference with nuisance parameters through normalizing flows"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.10534"
url: "http://arxiv.org/abs/2609.10534v1"
published: "2026-09-09T17:58:15Z"
ingested: "2026-09-10T10:34:16Z"
authors:
  - "Phil Assheton"
---

# Likelihood-free inference with nuisance parameters through normalizing flows

## Abstract

> We present a simple decomposition of a neural-network-based normalizing flow that naturally
> uncovers a pivotal statistic (or something close) in the presence of nuisance parameters, based
> only on a sample generator from the distribution of interest. We show that the statistic is
> near-pivotal in the sense of minimum average KL-divergence of its $p$-values versus uniform and
> we argue that it can be expected to have good power when the dimension of the statistic equals
> the dimension of the parameter. It is able to incorporate prior knowledge about group
> invariances such as translation and scale. It can discover the one-sample $t$-test almost
> exactly, outperforms the Welch test in terms of worst-case size over a constrained variance-
> ratio range and achieves good calibration on partial biserial correlations, while showing higher
> power (and being much faster) on small-to-moderate samples than profile likelihood-ratio
> techniques.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

