---
title: W37 stands as computed — its committer-date clock was checked against push times
date: 2026-09-24
status: staged
tags: [decision, status/staged, agreement/4.2, ledger/2026-W37]
provenance: >
  Drafted by Claude (Claude Code, session
  https://claude.ai/code/session_01MryxwgCr2J8ddTFbKc5Qtd) at a member's
  request, from ledger/windows/2026-W37/CLOCK-CHECK.md and the files beside it.
  Staged until a member reviews it and promotes it to status/accepted
  (vault/MAP.md, "Staged lessons"); until then it records a proposal, not a
  decision.
---

## Context

W37 (2026-08-31 … 2026-09-07) was computed on a clock the Agreement does not
recognise. Its own record says so —

> "clock": "committer dates; push-time gating is the admissible clock per 4.2 (v1 limitation)"
> — `ledger/windows/2026-W37/evidence.json`

— against Agreement 4.2:

> Only the Repository Record counts. Server-side timestamps govern. Dates embedded in commits are not evidence of time.
> — `agreements/consortium-agreement.md`, 4.2

W37 ratifies by silence at 2026-09-27T21:37:45Z (Agreement 4.4), after which
it reopens only by Amendment (4.5). Letting it ratify without looking would
ratify a figure on an inadmissible clock without knowing whether the clock
mattered.

## Decision

No member objects to W37 under Agreement 4.3. It stands as committed, because
on the clock 4.2 names it comes out the same:

> RESULT: W37 is the same on either clock
> — `python3 ledger/windows/2026-W37/clock-check/check.py`, exit 0

The same 18 commits fall in the window on committer and on push time; every
one reached GitHub within 12 minutes of its committer time, on the same UTC
day. The tool version that produced W37 reproduces it exactly, the push-clock
run matches it, and a negative control that moves one commit out of the
window does not — so the push dates really reach the computation. Merges and
reviews were already on server time.

## What this does not decide

- **The clock for W38 onward.** Windows are still computed on committer dates.
  Choosing among building the push clock, amending 4.2, narrowing 4.2 to
  disputes, or windowing between anchors remains open. What W37 adds: here,
  committer and push time agree to within minutes, so the gap is not producing
  wrong figures today. The case for the push clock is that a committer date is
  set by whoever commits and can be anything; a push time is set by GitHub.
- **Time zones.** `attribution.py` reads dates in each committer's own time
  zone (`git log --date=short`), so windows mix +10:00 and UTC days. It changes
  nothing in W37; on a week boundary it would. It is inherited from
  syndicate-genesis and is fixed there first.

## Consequences

- The push record behind this check lives in `ledger/windows/2026-W37/clock-check/`.
  GitHub's live feed keeps at most 300 events, so it will stop covering W37
  within about 40 days; the committed copy is the lasting one.
- A later window can be checked the same way while its push events are still
  in the feed. After that, only a copy taken in time can answer the question.
