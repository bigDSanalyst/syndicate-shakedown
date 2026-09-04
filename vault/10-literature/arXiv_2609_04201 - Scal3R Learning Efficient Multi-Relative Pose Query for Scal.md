---
aliases: ["Scal3R: Learning Efficient Multi-Relative Pose Query for Scalable Online 3D Reconstruction"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.04201"
url: "http://arxiv.org/abs/2609.04201v1"
published: "2026-09-03T17:59:53Z"
ingested: "2026-09-04T20:49:54Z"
authors:
  - "Chin-Yang Lin"
  - "Yang-Che Sun"
  - "Cheng Sun"
  - "Fu-En Yang"
  - "Min-Hung Chen"
  - "Yen-Yu Lin"
  - "Wei-Chen Chiu"
  - "Yu-Lun Liu"
---

# Scal3R: Learning Efficient Multi-Relative Pose Query for Scalable Online 3D Reconstruction

## Abstract

> Online 3D reconstruction models perform poorly on long videos. This happens because regressing
> poses relative to a fixed first-frame anchor forces extrapolation far beyond the training
> distribution. Small drifts accumulate and amplify into significant geometric collapse. However,
> we observe that per-frame depth remains stable throughout this failure. The backbone's local
> geometry remains intact; only the global pose head breaks down. Motivated by this decoupling, we
> introduce Scal3R. This approach reformulates online reconstruction as multi-reference relative
> pose querying. We use lightweight learnable tokens, which make up about ~1% of the parameters,
> and inject them into a completely frozen backbone via asymmetric attention. This setup queries
> poses relative to multiple past keyframes. An online pose-graph optimization system with loop
> closure suppresses long-range drift. Scal3R reaches convergence in 8 hours on a single GPU. It
> reduces the average ATE by over 60% on KITTI compared to the online baseline. It also achieves
> state-of-the-art performance across Virtual KITTI, Sintel, TUM-Dynamic, ScanNet, and 7-Scenes.
> Project page: https://linjohnss.github.io/scal3r/

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

