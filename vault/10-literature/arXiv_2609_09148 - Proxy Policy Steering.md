---
aliases: ["Proxy Policy Steering"]
tags: [literature/arxiv, status/triage]
arxiv_id: "2609.09148"
url: "http://arxiv.org/abs/2609.09148v1"
published: "2026-09-08T17:59:03Z"
ingested: "2026-09-09T10:44:02Z"
authors:
  - "Chuanruo Ning"
  - "Tianrui Wang"
  - "Wei-Chiu Ma"
  - "Kuan Fang"
---

# Proxy Policy Steering

## Abstract

> Generalist robot policies carry broad manipulation priors from large-scale data, but
> specializing them to a new task remains the deployment bottleneck. This requires eliciting task-
> specific behavior from limited demonstrations without degrading their broad capabilities. We
> introduce Proxy Policy Steering (PPS), an inference-time adaptation method that resolves this
> challenge by training two lightweight proxy policies whose calibrated velocity-space difference
> steers the frozen base sampler. A reference proxy models the frozen base's behavior on target-
> task observations, and a task proxy, initialized from the reference, captures how this behavior
> changes under task supervision. Their difference forms a calibrated velocity-space residual that
> steers the frozen base sampler at every denoising step. We identify the conditions under which
> this residual isolates the change induced by task supervision, and validate them empirically.
> Because the base is never directly modified, its broad capabilities remain available at
> inference, including behaviors such as recovery from failure that the demonstrations themselves
> do not exercise. Adaptation requires only forward velocity predictions from the base, making PPS
> lightweight to train and applicable even without access to the base's parameters. On 8 real-
> world and 4 simulation manipulation tasks, PPS lifts the state-of-the-art pi 0.5 base policy by
> 53% absolute success rate on average, with zero-to-one gains on tasks the base never solves,
> while preserving the base's broad capabilities. PPS outperforms LoRA fine-tuning, from-scratch
> specialists, residual policies, and prior inference-time steering methods.

---
## Reading Notes
*Annotations below. Update the status tag as you triage; the arxiv_id frontmatter must survive edits - it is the dedup key.*

