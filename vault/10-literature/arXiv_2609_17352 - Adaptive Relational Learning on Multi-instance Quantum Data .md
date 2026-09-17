---
aliases: ["Adaptive Relational Learning on Multi-instance Quantum Data with Photonic Processors"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.17352"
url: "http://arxiv.org/abs/2609.17352v1"
published: "2026-09-15T15:50:47Z"
ingested: "2026-09-17T00:46:22Z"
authors:
  - "Marcin Jastrzebski"
  - "Shang Yu"
  - "Raj B. Patel"
  - "Oleksandr Kyriienko"
---

# Adaptive Relational Learning on Multi-instance Quantum Data with Photonic Processors

## Abstract

> Loading multiple quantum states in parallel into a quantum machine learning (QML) model can
> unlock learning tasks where key information resides in the \emph{relations} between states
> rather than in individual states. We introduce an adaptive relational learning framework for
> such multi-instance quantum data that accesses pairwise and higher-order relations. Our model
> combines global measurements via SWAP or CYCLE tests for evaluating an $n$-state Bargmann
> invariant with shallow trainable transformations applied locally to each input state. We
> demonstrate the approach for continuous-variable (CV) photonic systems, which naturally provide
> access to quantum data and necessary computing operations. We solve tasks involving hidden
> relationship detection, geometric phase classification, and sensing in the presence of an
> unknown shared nuisance interaction. We benchmark the adaptive model against a non-adaptive
> ``measure-first'' approach based on continuous-variable classical shadows, and show that the
> cost of shadow estimation grows rapidly with $n$, while our model avoids this dependence.
> Already for $n=2$, we achieve perfect test accuracy $A=1.0$ with $500$ inference shots,
> improving average test accuracy over the shadow-based method by $ΔA=0.15$ while using $100$
> times fewer shots per data point. Our work opens routes to sensing and quantum-data applications
> where adaptive photonic QML can access relational features that are costly to recover with non-
> adaptive, measure-first models.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

