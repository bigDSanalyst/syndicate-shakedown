---
aliases: ["Towards Surrogate Based Dequantization of Quantum Reinforcement Learning"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.16266"
url: "http://arxiv.org/abs/2609.16266v1"
published: "2026-09-14T19:26:35Z"
ingested: "2026-09-17T00:46:22Z"
authors:
  - "Pablo Rodriguez-Grasa"
  - "Sofiene Jerbi"
  - "Mikel Sanz"
  - "Ryan Sweke"
---

# Towards Surrogate Based Dequantization of Quantum Reinforcement Learning

## Abstract

> In recent years, the utility of parameterized quantum circuits as function approximators has
> been widely studied. In the context of reinforcement learning, this approach has led to
> variational quantum algorithms such as quantum Q-learning. While these methods show promising
> empirical results, and can provide provable advantages for artificial problems, it remains
> unclear whether they can provide a provable quantum advantage over classical approaches for
> problems of practical relevance. A natural way to investigate this question is through the lens
> of dequantization: The construction of efficient classical algorithms capable of matching the
> performance of quantum variational methods. Building on recent kernel-based dequantization
> results for supervised learning, we take steps towards extending this surrogate-based
> dequantization program to reinforcement learning. Specifically, we study the simplified setting
> of reinforcement learning with a uniform generative model in which uniformly random state-action
> samples are available, which models the regime of sampling from a large experience replay buffer
> after sufficient exploration. Within this setting, we provide finite sample guarantees for
> classical kernelized Fitted Q-Iteration, with classical kernels designed to match the inductive
> bias of particular parameterized quantum circuits. Using these results, we then provide a set of
> sufficient conditions, on the data-encoding strategy of a parameterized quantum circuit, the
> corresponding classical kernel, and the problem structure, under which kernelized Fitted
> Q-Iteration provides a meaningful dequantization of quantum Q-learning, in this simplified
> setting. Apart from providing rigorous dequantization guarantees when these conditions are met,
> these results also motivate the use of kernelized fitted Q-iteration as a dequantization
> heuristic when these sufficient conditions cannot be verified.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

