# AUDIT-001 — external cold audit, tool-executing

**Auditor:** Claude Opus 5, Claude Code session, no prior context.
**Date:** 2026-09-16.
**Method:** executed the tooling against live state — ran `attribution.py` and
`anchor.py verify`, queried the GitHub REST API directly, parsed real `.ots`
files with the `ots` CLI, compiled the regexes against real bot names, and
cross-checked every cited arXiv ID against the vault. No finding below is
read-off-the-source inference unless explicitly labelled as such.

**Scope, pass 1 (cold):** `syndicate-shakedown` only. The auditor did not know
`syndicate-genesis`, `FINDINGS.md`, `ROADMAP.md` or the oracle layer existed.
**Scope, pass 2 (corrected):** `syndicate-genesis` @ `c599ca5` (v1.2) added
after the operator identified the single-repo blind spot. Pass 2 exists because
pass 1's scope error was itself diagnostic — see finding 37.

> **The structural lesson, recorded first because it governs the rest:**
> a single-repo audit of a multi-repo protocol verifies a projection, not the
> system. Pass 1 attributed template bugs to the instance and instance drift to
> the template, in both directions. The recheckability principle applies to
> auditing itself.

---

## Part A — template-level, verified present in `syndicate-genesis` @ c599ca5

These ship in the mold. The shakedown inherited them; every future generated
repo inherits them until v1.3. Verified byte-identical in both repos.

| # | Finding | Evidence | Fix status |
|---|---|---|---|
| 27 | `fetch_papers` has no retry, backoff or `Retry-After` handling; one arXiv 429 exits 1 | ingest red 3 consecutive days (runs 19/20/21); CI log: `❌ request failed: HTTP Error 429` | open |
| 30 | Bitcoin block heights parsed and discarded — regex is `height\s+(\d+)`, `ots` emits `BitcoinBlockHeaderAttestation(965532)` | every `height` in `log.jsonl` is `null`; `verify` prints `block ?` | **fixed + verified** |
| 31 | `merged_by` is absent from the list-PRs endpoint, so merge credit is permanently zero | list: `merged_by_present=False`; `GET /pulls/5`: `True → bigDSanalyst` | **fixed + verified** |
| 32 | Windows are cumulative, not periodic: `min/max` over all commit dates, then labelled with an ISO week | run produced `2026-W38` covering `09-04 → 09-15` | **fixed + verified** |
| 33 | `'\\[bot\\]$'` compiles to a regex for a *literal backslash* — YAML single quotes do not process escapes | matched `False` against `syndicate-anchor[bot]`, `dependabot[bot]`, both bot emails | **fixed + verified** |
| 34 | API failure prints a WARNING, zeroes review credit, exits 0 — unauthenticated (60/hr), unpaginated, 1+N requests | `attribution.py:39`; operator rule #8 violated by the ledger tool itself | **fixed + verified** |

### Verification of the fixes (run against real data, not fixtures)

```
#30  0001-2026-09-04: confirmed=True  height=965528   ← min(965532, 965554, 965528)
     0007-2026-09-15: confirmed=False height=None     ← pending, correctly unconfirmed
#33  syndicate-anchor[bot] excluded=True   dependabot[bot] excluded=True
     github-actions[bot]   excluded=True   Nicholas Maino  excluded=False
#31/32/34  window AUDIT-TEST 2026-09-08 -> 2026-09-15
     bigDSanalyst,...,reviews=1,merges=1,share=1.0     ← merges was permanently 0
```

---

## Part B — the v1.2 release regression (new, highest severity)

| # | Finding | Evidence |
|---|---|---|
| 38 | **`join.py` cannot parse its own template. The adopter entry path has never been run.** Its anchor string is `'members:    # # ONE ROW PER MEMBER, EDIT AT GENESIS'` (4 spaces, doubled hash); the manifest contains `'members:   # ONE ROW PER MEMBER, EDIT AT GENESIS'` (3 spaces, single hash). Every adopter gets `ERROR: manifest members anchor not found — file changed shape?` on an unmodified template. | executed against unmodified `syndicate-genesis`; exact failure reproduced |
| 39 | `join.py` writes the adopter's PAT into `.git/config` in plaintext via `remote set-url`, and never reverts it. The token persists on disk after the script exits. `sh()` also prints raw git stderr, which carries the remote URL. | reproduced: `url = https://ghp_FAKE...@github.com/...` left in config. Contradicts SECURITY.md threat #2 |
| 40 | `join.py` runs every git call through `subprocess.run(..., shell=True)` with `--handle` and `--token` interpolated into the command string | `join.py:26-30`, `:86-89` (pre-fix) |

**Why 38 matters beyond the bug.** The `# #` artifact appears in exactly five
places, all of them v1.2-era files (`queries.yaml:9`, `join.py:36,65,71,76`),
and in **zero** shakedown files. The doubled hash is the paste-proof converter
of finding #21 — and the fix for #21 regressed the tool shipped in the same
release. Finding #21 was recorded as closed. It was not: it changed shape and
moved into string literals, where a comment-marker fix becomes a logic bug.
Two of the five leaked into strings that are *data*, not comments: `:71` breaks
the match, `:65` writes a malformed comment into every new member's YAML row.

Track 1 step 1.4 reads *"Hand-hold: you run join.py with them."* It would have
failed in front of the first design partner.

All three are **fixed + verified**: anchor now matches on the `members:` key via
regex rather than a drifting comment; PAT goes to a one-shot push URL and is
redacted from all output; `sh()` takes an argv list.

---

## Part C — instance-level, `syndicate-shakedown` only

| # | Finding | Note |
|---|---|---|
| 28 | The shakedown's `queries.yaml` still carries the comment-poisoned queries. v1.2 fixed this in the template; the shakedown generated before the fix. | **Correction to pass 1:** the operator *knew*. `vault/20-notes/invariant-question.md` labels its own corpus "a byproduct of finding #13". Pass 1 reported this as unnoticed; it was noticed, documented, and left deployed. The finding is not the bug — it is 37. |
| 29 | `satsolverv124` commits as `maiknown@gmail.com`, not the manifest noreply address. All of that member's code work scores zero. | Finding #17 predicted this. Quantified here: `0.7619 / 0.2381`, with `churn=0.0, files=0` for the affected member. |
| 35 | `invariant-question.md` mis-cites 4 of 10 evidence IDs — `04195`, `04186`, `04176`, `04165` all name papers other than the ones at those IDs; `04198` (Clean Engineering) is discussed but never cited. | Already Bitcoin-anchored. `vault/MAP.md` law: *"Do not invent citations."* Correct by appended entry, never rewrite (MAP.md law 4). |
| 36 | No real ledger window has ever been produced. The only artifact under `ledger/windows/` is a template placeholder — `github-handle`, all zeros, dated `2026-09-02/03`, generated before the syndicate existed — and it is committed **and anchored**. No workflow runs `attribution.py`. | Agreement §4 has not executed in 12 days of operation. |

---

## Part D — architectural, surfaced by the scope error

| # | Finding | Why it is structural |
|---|---|---|
| 37 | **Generated repos are frozen at their generation-time template version. No template→instance propagation path exists.** | Every Part A fix must now be hand-carried into every live syndicate. The shakedown proves the failure mode at n=1; it does not scale to n=3 design partners, and it silently widens with each release. This gap was invisible until an auditor mistook a stale instance for current system state. |
| 41 | **`FINDINGS.md` contains rows 1–22. Rows 23–26 are referenced in planning as established ledger rows and do not exist in the record.** | Verified: `grep -oE '^\| *[0-9]+'` returns `1..22`, and no other findings file exists in either repo. Agreement §1.2: *"Work done outside it and not committed does not count for any purpose under this Agreement."* The ledger of findings is the one artifact that cannot afford uncommitted rows, and it has four. Numbering below resumes at 27 to preserve existing references; the gap is left open deliberately rather than silently closed. |
| 42 | Neither repo has tests or CI for the Python tools. ~700 lines across four tools, zero coverage — and these are the tools the Agreement's IP, money and priority clauses execute through. | Findings 30–34 and 38–40 are all unit-testable. Every one survived to production. |

---

## What pass 1 got wrong

Recorded because an audit that does not audit itself is the thing it warns about:

1. **Scope.** Reported instance state as system state. Half of Part A was
   presented as "your repo" when it is "the mold". Corrected in pass 2.
2. **Finding 28.** Reported the poisoned queries as an oversight. The vault note
   shows the operator diagnosed it and chose to leave it. The real finding was
   the missing propagation path (37), which pass 1 could not see.
3. **Missed entirely in pass 1:** `join.py` (38–40) — it does not exist in the
   shakedown. The most severe finding in this audit was outside pass 1's scope,
   which is the strongest available argument for 37 and for AUDIT-002.

## Recommended next audit

**AUDIT-002: full corpus, cold, tool-executing** — template + shakedown + kernel
together, same method, complete scope. The contrast is diagnostic: whatever
still fails in 002 is system-level truth; whatever disappears was instance drift.
