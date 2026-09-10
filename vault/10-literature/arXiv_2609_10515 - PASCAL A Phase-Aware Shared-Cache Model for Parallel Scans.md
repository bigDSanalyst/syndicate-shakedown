---
aliases: ["PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.10515"
url: "http://arxiv.org/abs/2609.10515v1"
published: "2026-09-09T17:48:51Z"
ingested: "2026-09-10T10:34:16Z"
authors:
  - "Zhongchun Zhou"
  - "Chengtao Lai"
  - "Songtao Mao"
---

# PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans

## Abstract

> In modern AI Accelerators and GPGPUs, many concurrent cores repeatedly access the same shared
> data. This pattern occurs in attention, where different query tiles share the same K/V block,
> GEMM, where every tile in a row reads the same panel, and many other operators. We name this
> pattern parallel scan. Due to a significant amount of data reuse in this pattern, the cache is
> expected to capture as much data reuse as possible and largely reduce requests sent to the main
> memory for both performance and energy consumption concerns. However, in reality, because of the
> intrinsic asynchrony of multi-cores, the actual cache miss rate and DRAM traffic can be much
> higher compared to ideal cases. In this paper, we propose PASCAL, a shared-cache model for
> parallel scans. It is aware of the dynamic feature of progress divergence across multi-cores,
> correlate the divergence with the combination of different factors such as occupancy, and
> predicts the cache miss rate before execution. Because prediction needs no target trace, timing,
> or counters, PASCAL supports design-space exploration at scales where cycle-accurate simulation
> is impractical, and its policy-independent bound states how much traffic no replacement policy
> can avoid. A MAPE of 13.84% is achieved in a 60-configuration dataset with various software
> pipeline depths, occupancies, and memory access data paths on an NVIDIA GB10 GPU, against 44.79%
> for physical-wave TileSight and 54.16% for exact symbolic SDCM.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

