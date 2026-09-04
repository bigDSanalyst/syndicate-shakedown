---
aliases: ["Seeing Before Synthesizing: VLM-Guided Transition Event Discovery for Weakly-Supervised Dense Video Captioning"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.04183"
url: "http://arxiv.org/abs/2609.04183v1"
published: "2026-09-03T17:58:02Z"
ingested: "2026-09-04T20:49:54Z"
authors:
  - "Ye-Chan Kim"
  - "Seunghee Choi"
  - "SeungJu Cha"
  - "Si-Woo Kim"
  - "Hwiseon Kim"
  - "Hyungee Kim"
  - "Dong-Jin Kim"
---

# Seeing Before Synthesizing: VLM-Guided Transition Event Discovery for Weakly-Supervised Dense Video Captioning

## Abstract

> Weakly-Supervised Dense Video Captioning aims to localize and describe multiple events in
> untrimmed videos given only an ordered set of event-level captions per video. Recent work
> synthesizes auxiliary transition captions via LLM to provide additional vision-language
> alignment, but these captions lack visual grounding and are rigidly assigned to every inter-
> event gap at a fixed location and duration. To address these, we propose Seeing Before
> Synthesizing (SBS), a framework that adaptively provides visually grounded linguistic guidance
> only where warranted. Leveraging a VLM, we generate frame-level narratives for the inter-event
> gaps and detect transitions from the semantic variation across them. For identified transitions,
> we then refine inter-event temporal masks by blending the temporal midpoint with the semantic
> change point and selecting the width that maximizes vision-language alignment. Experiments on
> ActivityNet Captions and YouCook2 demonstrate state-of-the-art performance in both captioning
> and localization.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

