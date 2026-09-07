---
aliases: ["CrossDepth: Geometry-Constrained Attention for Generalizable Multi-View Surround Depth Estimation"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.05397"
url: "http://arxiv.org/abs/2609.05397v1"
published: "2026-09-04T17:45:06Z"
ingested: "2026-09-07T11:32:19Z"
authors:
  - "Samer Abualhanud"
  - "Max Mehltretter"
---

# CrossDepth: Geometry-Constrained Attention for Generalizable Multi-View Surround Depth Estimation

## Abstract

> Reliable 3D understanding of the surrounding environment is a core requirement for autonomous
> driving. Multi-view surround camera rigs provide broad scene coverage, but the spatially
> adjacent images typically overlap only minimally. Consequently, the depth of most pixels must be
> inferred from monocular appearance cues. These cues can appear differently across images and may
> therefore be interpreted differently by the depth estimation model. We target two main sources
> of cross-image inconsistency: differences in camera intrinsics and the limited receptive field
> of each image. We address the former by conditioning the features on per-pixel camera-aware ray
> embeddings, enabling the network to account for camera-dependent variations in monocular cues.
> We address the latter by extending each pixel's context beyond its own image through cross-image
> attention constrained to geometrically plausible regions, derived from the calibrated rig setup.
> The model is trained in a fully self-supervised manner based on photometric consistency.
> Evaluations on DDAD and nuScenes show improved overall depth accuracy and cross-image depth
> consistency over state-of-the-art self-supervised methods under in-domain and cross-domain
> evaluation. Code is available at https://abualhanud.github.io/CrossDepthPage/.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

