---
aliases: ["Point4D: Long-range 4D Motion Reconstruction"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.09145"
url: "http://arxiv.org/abs/2609.09145v1"
published: "2026-09-08T17:58:35Z"
ingested: "2026-09-09T10:44:02Z"
authors:
  - "Minsik Jeon"
  - "Jay Karhade"
  - "Deva Ramanan"
  - "Shubham Tulsiani"
---

# Point4D: Long-range 4D Motion Reconstruction

## Abstract

> We introduce Point4D, a feed-forward model for 4D reconstruction of long-range video sequences.
> Point4D is able to reliably infer dense per-point 3D trajectories across multi-hundred-frame
> videos, unlike existing 4D methods that are limited to short input windows of at most a few
> dozen frames. A key innovation that enables this is our flexible 3D query-based motion decoder
> that decouples trajectory prediction from image-plane visibility. The predicted 3D endpoints are
> then directly re-queried in the next chunk without re-projection or matching. Furthermore, we
> show that extracting and reusing a visual descriptor from an arbitrary frame where the point is
> visible leads to better performance than relying solely on the source patch. Overall, Point4D
> achieves state-of-the-art performance across diverse long-video tracking benchmarks spanning
> over 200 frames and largely outperforms previous feed-forward 4D method. Project page:
> https://point-4d.github.io

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

