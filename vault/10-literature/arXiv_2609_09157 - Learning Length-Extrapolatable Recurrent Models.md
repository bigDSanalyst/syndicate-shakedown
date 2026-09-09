---
aliases: ["Learning Length-Extrapolatable Recurrent Models"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.09157"
url: "http://arxiv.org/abs/2609.09157v1"
published: "2026-09-08T17:59:53Z"
ingested: "2026-09-09T10:44:02Z"
authors:
  - "Hanwen Jiang"
---

# Learning Length-Extrapolatable Recurrent Models

## Abstract

> Recurrent models provide a natural path to long-context modeling, yet models trained with
> backpropagation through time (BPTT) often fail beyond their training horizon. Classical analyses
> emphasize gradients that vanish or explode along temporal paths. However, dense per-token losses
> can still train a shared recurrent rule despite severe decay, showing that decay alone does not
> determine whether learning fails. We instead study state credit: the signal through which future
> losses reach earlier recurrent states before contributing to parameter updates. Accordingly, we
> intervene directly on state credit and propose Credit Stabilization through Time (CST). During
> backward propagation, CST locally rescales the state-credit signal to stabilize its norm without
> rotating the component being corrected, while leaving the forward computation unchanged. Because
> controlled synthetic tasks and real data exhibit different credit dynamics, we specialize CST to
> each regime. In both settings, CST improves performance beyond the training horizon, with gains
> observed at up to 128x the training length.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

