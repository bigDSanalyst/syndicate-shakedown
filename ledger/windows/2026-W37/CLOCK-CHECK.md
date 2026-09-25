## Clock check — 2026-09-24

W37 was computed on committer dates, and its own `evidence.json` says so:

> "clock": "committer dates; push-time gating is the admissible clock per 4.2 (v1 limitation)"

Agreement 4.2 names a different clock:

> Only the Repository Record counts. Server-side timestamps govern. Dates embedded in commits are not evidence of time.

This check recomputes W37 on push times — when each commit first reached
GitHub, from the repository's server-side event log — before W37 ratifies by
silence at 2026-09-27T21:37:45Z (Agreement 4.4).

### Result: W37 is the same on either clock

| run | what it is | outcome |
|---|---|---|
| committer | `tools/attribution.py` as of `e42de24` (the version that produced W37), at the window head `326bd1c`, unchanged | reproduces the recorded `attribution.csv` and `evidence.json` exactly |
| push | the same, with each commit's date replaced by its push date | identical to the record |
| control | push dates, with one member commit (`5be58a0`) moved out of the window | differs (churn 1664.0 → 1650.0, shares 0.6462 / 0.3538 → 0.6461 / 0.3539), so the substitution really reaches the tool |

- The same 18 commits fall in 2026-08-31 … 2026-09-07 on both clocks
  (`a5499ec` … `d4e5f45`). Every one reached GitHub within 12 minutes of its
  committer time, on the same UTC day, and no member commit sits near either
  edge of the window.
- Merges and reviews were already on server time: `attribution.py` windows
  them by the API's `merged_at` and review submission time. Only commit
  selection — churn and breadth — used the committer clock.

### Evidence, in `clock-check/`

| file | what |
|---|---|
| `events-page-1.json` … `-3.json` | GitHub's events API for this repository, as returned, fetched 2026-09-24T23:50:04Z. sha256: `391d9e77…3008e`, `f52e4c5a…54f7`, `2ba33ca0…1d6d` |
| `push-times.json` | each commit's first push, derived from those pages and this repository's history |
| `check.py` | reproduces everything above: `python3 ledger/windows/2026-W37/clock-check/check.py` (exit 0 when the result holds) |
| `committer.csv`, `push.csv`, `control.csv` | the three runs' output |

### Limits

- The event log covers the repository from its creation: 104 events, the
  oldest at 2026-09-04T20:05:32Z, five seconds after the repository was
  created; the third page is empty. GitHub serves at most 300 events, and this
  repository produces about five a day, so the live feed stops covering W37
  within about 40 days. These files are the lasting copy, and the anchor chain
  will stamp them with the rest of `ledger/`.
- The initial commit `a5499ec` arrived with the repository, not by a push. Its
  time is an upper bound — the first push that builds on it,
  2026-09-04T20:14:17Z — and falls inside the window either way.
- `check.py` re-reads merges and reviews from the GitHub API, so a rerun
  reflects their state when it is run.
- This establishes W37 only. W38 onward are computed on the same clock until
  the Agreement 4.2 question is decided.

### A second clock problem, found on the way

`attribution.py` reads commit dates with `git log --date=short`, which prints
each date in its committer's own time zone. W37 therefore mixes +10:00 and UTC
dates: the initial commit counts as 2026-09-05 though it was made at
2026-09-04T20:05:31Z. No W37 commit is near an edge, so it changes nothing
here. On a week boundary it would: a Monday-morning commit at +10:00 is Sunday
in UTC. The tool is inherited from syndicate-genesis, so the fix lands there
first and this instance follows.
