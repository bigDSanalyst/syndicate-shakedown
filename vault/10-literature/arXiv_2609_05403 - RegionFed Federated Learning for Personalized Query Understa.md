---
aliases: ["RegionFed: Federated Learning for Personalized Query Understanding in Heterogeneous Retail Environments"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.05403"
url: "http://arxiv.org/abs/2609.05403v1"
published: "2026-09-04T17:50:10Z"
ingested: "2026-09-07T11:32:19Z"
authors:
  - "Quoc H. Nguyen"
  - "Ali Lafzi"
  - "Abhijeet Phatak"
  - "Siddharth Pratap Singh"
  - "Rohit Upadhyay"
  - "Yogananda Domlur Seetharama"
  - "Chittaranjan Tripathy"
---

# RegionFed: Federated Learning for Personalized Query Understanding in Heterogeneous Retail Environments

## Abstract

> Retail search systems serve diverse geographic regions with distinct query patterns,
> vocabularies, and product preferences, creating significant data heterogeneity that challenges
> both privacy-preserving training and model personalization. Federated learning offers a natural
> solution for privacy, but standard FL methods produce global models that sacrifice regional
> performance, while existing personalized FL approaches operate at the parameter level and
> catastrophically collapse on modern transformers (below 10\% accuracy on T5) due to tied
> embeddings and LayerNorm interactions. We introduce RegionFed, an \textit{architecture-robust}
> federated learning framework that sidesteps this failure by operating entirely at the gradient
> level. RegionFed uses the $\ell_2$ conflict between regional and global gradients as a unified
> signal that (i) diagnoses heterogeneity, (ii) routes each region to the cheapest sufficient
> personalization strategy, and (iii) adaptively controls personalization strength. Because it
> treats models as differentiable black boxes, RegionFed deploys on T5-Small, T5-3B, RoBERTa, and
> CNN with zero code changes, providing large gains on transformers (where parameter-level methods
> collapse) and consistent improvements on CNNs. Across three public datasets (Amazon ESCI, Amazon
> Reviews, LEAF-FEMNIST) and four architectures, RegionFed-Meta achieves 92.27\%, closing the gap
> to the privacy-violating centralized upper bound (Centralized + Regional Weighting: 92.04\%,
> $Δ$=0.23pp, within 1$σ$) while providing $(ε{\approx}0.60)$-differential privacy and
> $\mathcal{O}(1/\sqrt{T})$ convergence.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

