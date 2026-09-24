#!/usr/bin/env python3
"""Are the claims in ledger/claims/ what they say they are?

A claim is a safety assertion bound to evidence: one sentence, the artifacts
it rests on, and an append-only history of decisions about it. Its state is
the state of its last history entry. Nothing stores it, so nothing can store
it wrong.

This tool computes whether each claim's declaration holds - its evidence is
committed in this repository and hashes to what the claim recorded, the
people it names are members allowed to do what it says they did, and its
history only ever grew. It reads the working tree and local git, never the
network, and writes nothing.

WHAT OFFLINE CANNOT SEE
  A reviewer named in a file is a declaration, not a review. So every
  reviewer and every human-gate approver stops at WARN here, never ok.
  tools/confirm_approvals.py asks GitHub whether that person approved the
  pull request that recorded the decision, and it runs in CI. Do not report
  a WARN from this tool as verified.

  The `at:` date on a history entry is also the author's claim (Agreement
  4.2). The anchor that first covers the entry is the evidence of time.

Output mirrors tools/doctor.py - the same statuses, the same --json shape,
the same exit codes - so one parser reads both.

STATUSES
  ok      the declaration holds, as far as offline can see
  DECIDE  this syndicate has not started a claims ledger. Not a fault.
  WARN    consistent, but only an online check can confirm it
  BLOCK   wrong now - a claim cites what is not there, names someone who
          may not act, or rewrote its own record

EXIT
  0  no BLOCK
  1  at least one BLOCK

CHECKS
  CLM001  ledger/claims/ exists          CLM009  ledger/sections/ exists
  CLM002  parses, has a valid history    CLM010  sections cite only verified claims
  CLM003  id matches filename            CLM011  a draft names what it waits on
  CLM004  evidence resolves              CLM012  a rejection names its reason
  CLM005  everyone named is on a roster  CLM013  history only grows (vs --base)
  CLM006  reviewer is not the author     CLM014  a rejected claim stays rejected
  CLM007  a decision names a reviewer    CLM015  a provisional member is not the
  CLM008  the human gate                         sole approver (Agreement 2.3)
                                         CLM016  an agent-authored claim records
                                                 its model and prompt
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as M                                          # noqa: E402

try:
    import yaml
except ImportError:                                           # pragma: no cover
    print("doctor_claims needs PyYAML: pip install -r tools/requirements.txt", file=sys.stderr)
    sys.exit(1)

OK, DECIDE, WARN, BLOCK = "ok", "DECIDE", "WARN", "BLOCK"
STATES = ("draft", "verified", "rejected")
DECISIONS = ("verified", "rejected")
EVIDENCE_KINDS = ("eval_run", "prior_model", "report", "dataset", "external")
# Once a claim has been decided, these are what was decided about. Changing
# one afterwards rewrites the thing a reviewer approved (vault/MAP.md law 4).
FROZEN_ONCE_DECIDED = ("text", "section", "author", "authored_by_model",
                       "evidence", "human_gate")


class Check:
    """One computed finding. `fix` is a command or an act, never an opinion."""

    def __init__(self, key, status, headline, detail="", fix=""):
        self.key, self.status = key, status
        self.headline, self.detail, self.fix = headline, detail, fix

    def as_dict(self):
        return {"check": self.key, "status": self.status, "headline": self.headline,
                "detail": self.detail, "fix": self.fix}


def git(repo, *args):
    """Stdout, or None. Never raises."""
    try:
        r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def load(text):
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


def handle(value):
    """GitHub logins are case-insensitive; compare them that way."""
    return str(value).strip().lower() if value else None


class Roster:
    """Who may be named, and as what. Built from syndicate.yaml only.

    everyone  member rows, by GitHub login: anyone who may author a claim.
              A member who has left still authored what they authored.
    active    members who have not left (Agreement 10.2: roles end), keyed
              the same way: only they may review or approve.
    agents    rows of a top-level `agents:` list, by name. Agents are not
              members and not parties to the Agreement: they may author a
              claim, never review or approve one. The list does not exist
              until the syndicate adds it through the agreements gate.
    """

    def __init__(self, cfg):
        self.everyone, self.active, self.agents = {}, {}, {}
        for row in cfg.get("members") or []:
            if isinstance(row, dict) and handle(row.get("github")):
                self.everyone[handle(row["github"])] = row
                if not row.get("left"):
                    self.active[handle(row["github"])] = row
        for row in cfg.get("agents") or []:
            if isinstance(row, dict) and handle(row.get("name")):
                self.agents[handle(row["name"])] = row

    def provisional(self, who):
        return (self.active.get(handle(who)) or {}).get("trust_tier") == "provisional"


def tracked_files(repo):
    out = git(repo, "ls-files", "-z")
    return None if out is None else set(p for p in out.split("\0") if p)


def check_evidence(repo, cid, entry, tracked, checks):
    if not isinstance(entry, dict):
        checks.append(Check("CLM004", BLOCK, "%s: an evidence entry is not a mapping" % cid,
                            fix="each entry is {kind, ref, sha256}"))
        return False
    kind, ref, recorded = entry.get("kind"), entry.get("ref"), entry.get("sha256")
    if kind not in EVIDENCE_KINDS:
        checks.append(Check("CLM004", BLOCK, "%s: evidence kind %r is not one this ledger knows"
                            % (cid, kind), "known kinds: " + ", ".join(EVIDENCE_KINDS),
                            "use a known kind"))
        return False
    if not ref:
        checks.append(Check("CLM004", BLOCK, "%s: an evidence entry has no ref" % cid,
                            fix="add ref: the path of the artifact, or its URL if external"))
        return False
    if kind == "external":
        if not recorded:
            checks.append(Check("CLM004", BLOCK, "%s: external evidence %r records no sha256"
                                % (cid, ref), fix="record the artifact's digest, or commit it"))
            return False
        checks.append(Check("CLM004", WARN, "%s: external evidence %r is not checkable offline"
                            % (cid, ref), "a digest is recorded; nothing here has the bytes"))
        return True

    # The bytes must be in this repository: not reached through .. or an
    # absolute path, not a symlink out of it, and committed, not merely
    # present on this disk - CI checks out only what was committed.
    root = repo.resolve()
    path = (root / str(ref)).resolve()
    if Path(str(ref)).is_absolute() or not path.is_relative_to(root):
        checks.append(Check("CLM004", BLOCK, "%s: evidence %r is outside this repository"
                            % (cid, ref), "a claim's evidence is bytes this repo holds",
                            "commit the artifact under this repository and cite that path"))
        return False
    if not path.is_file():
        checks.append(Check("CLM004", BLOCK, "%s: evidence %r does not exist" % (cid, ref),
                            fix="commit the artifact at %s, or fix the ref" % ref))
        return False
    rel = path.relative_to(root).as_posix()
    if tracked is not None and rel not in tracked:
        checks.append(Check("CLM004", BLOCK, "%s: evidence %r is not committed" % (cid, ref),
                            "it exists on this disk, so it would pass here and fail in CI",
                            "git add %s" % rel))
        return False
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if recorded != actual:
        checks.append(Check("CLM004", BLOCK, "%s: evidence %r does not hash to what the claim "
                            "recorded" % (cid, ref),
                            "recorded %s, actual %s" % (str(recorded)[:16], actual[:16]),
                            "restore the artifact the claim was made about; if the artifact "
                            "really changed, that is a new claim"))
        return False
    checks.append(Check("CLM004", OK, "%s: evidence %r is committed and hashes as recorded"
                        % (cid, ref)))
    return True


def check_history(cid, raw, roster, checks):
    """Validate every entry. Returns the list, or None if it is unusable."""
    history = raw.get("history")
    if not isinstance(history, list) or not history:
        checks.append(Check("CLM002", BLOCK, "%s: no history, so it has no state" % cid,
                            fix="append a history entry with state: draft"))
        return None
    for i, e in enumerate(history):
        if not isinstance(e, dict) or e.get("state") not in STATES:
            checks.append(Check("CLM002", BLOCK, "%s: history[%d] has no valid state" % (cid, i),
                                "states: " + ", ".join(STATES), "fix that entry"))
            return None
        if handle(e.get("by")) not in roster.everyone and handle(e.get("by")) not in roster.agents:
            checks.append(Check("CLM005", BLOCK, "%s: history[%d] is by %r, who is on no roster"
                                % (cid, i, e.get("by")), fix="name a member or an agent row"))
    for i, e in enumerate(history[:-1]):
        if e["state"] == "rejected":
            checks.append(Check("CLM014", BLOCK, "%s: history continues after it was rejected "
                                "(entry %d)" % (cid, i),
                                "a rejection is final; reviving the claim would reintroduce it",
                                "state the corrected claim as a new claim id"))
    return history


def check_decision(cid, raw, entry, i, roster, checks):
    """A verified or rejected entry: who reviewed it, who cleared the gate."""
    author = handle(raw.get("author"))
    reviewer = handle(entry.get("reviewer"))
    where = "%s: history[%d] (%s)" % (cid, i, entry["state"])
    if not reviewer:
        checks.append(Check("CLM007", BLOCK, "%s names no reviewer" % where,
                            fix="a decision names the member who reviewed it"))
    elif reviewer == author:
        checks.append(Check("CLM006", BLOCK, "%s: the reviewer is the author" % where,
                            "self-review is not a gate", "request review from another member"))
    elif reviewer in roster.agents:
        checks.append(Check("CLM005", BLOCK, "%s: reviewer %r is an agent" % (where, reviewer),
                            "agents may author claims, never review them", "name a member"))
    elif reviewer not in roster.active:
        checks.append(Check("CLM005", BLOCK, "%s: reviewer %r is not a current member"
                            % (where, reviewer), fix="name a member who has not left"))
    else:
        checks.append(Check("CLM006", WARN, "%s: reviewer %r is declared, not yet confirmed"
                            % (where, reviewer),
                            "tools/confirm_approvals.py confirms it in CI, against the PR "
                            "that recorded this entry"))

    approvers = [reviewer] if reviewer in roster.active else []
    if raw.get("human_gate") == "required" and entry["state"] == "verified":
        by = handle(entry.get("approved_by"))
        if not by:
            checks.append(Check("CLM008", BLOCK, "%s: the claim is human-gated and no member "
                                "approved it" % where, fix="add approved_by: <member>"))
        elif by in roster.agents:
            checks.append(Check("CLM008", BLOCK, "%s: approved_by %r is an agent" % (where, by),
                                "an agent does not clear a human gate", "name a member"))
        elif by == author:
            checks.append(Check("CLM008", BLOCK, "%s: the author approved their own claim"
                                % where, fix="name another member"))
        elif by not in roster.active:
            checks.append(Check("CLM008", BLOCK, "%s: approved_by %r is not a current member"
                                % (where, by), fix="name a member who has not left"))
        else:
            approvers.append(by)
            checks.append(Check("CLM008", WARN, "%s: human gate cleared by %r is declared, "
                                "not yet confirmed" % (where, by),
                                "tools/confirm_approvals.py confirms it in CI"))
    if approvers and all(roster.provisional(a) for a in approvers):
        checks.append(Check("CLM015", BLOCK, "%s: every approver is provisional" % where,
                            "Agreement 2.3: a provisional member may not be the sole approver "
                            "of changes to ledger/**", "add a verified or standard member"))


def check_against_base(repo, base, rel, raw, checks):
    """CLM013: the claim as committed at `base` must be a prefix of it now."""
    cid = Path(rel).stem
    old_text = git(repo, "show", "%s:%s" % (base, rel))
    if old_text is None:
        return                                    # new in this change
    old = load(old_text)
    if not isinstance(old, dict):
        return
    if raw is None:
        checks.append(Check("CLM013", BLOCK, "%s: deleted, but it was in the record at %s"
                            % (cid, base[:12]), "a claim is never removed; it is rejected",
                            "restore it, and append a rejected entry if it is wrong"))
        return
    old_h, new_h = old.get("history") or [], raw.get("history") or []
    if new_h[:len(old_h)] != old_h:
        checks.append(Check("CLM013", BLOCK, "%s: its history was edited, not appended to"
                            % cid, "the first %d entries must be unchanged since %s"
                            % (len(old_h), base[:12]),
                            "restore the earlier entries; record the change as a new one"))
    if any(isinstance(e, dict) and e.get("state") in DECISIONS for e in old_h):
        changed = [f for f in FROZEN_ONCE_DECIDED if old.get(f) != raw.get(f)]
        if changed:
            checks.append(Check("CLM013", BLOCK, "%s: %s changed after the claim was decided"
                                % (cid, ", ".join(changed)),
                                "a reviewer decided about the claim as it was",
                                "restore it; a different claim is a new claim id"))


def check_claims(repo, roster, tracked, base, checks):
    claims = {}
    cdir = repo / "ledger" / "claims"
    if not cdir.is_dir():
        checks.append(Check("CLM001", DECIDE, "this syndicate has no claims ledger yet",
                            "ledger/claims/ does not exist",
                            "mkdir -p ledger/claims, and start from "
                            "ledger/claims/_TEMPLATE.yaml"))
        return claims
    for path in sorted(cdir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        raw = load(path.read_text())
        rel = path.relative_to(repo).as_posix()
        if base and isinstance(raw, dict):
            check_against_base(repo, base, rel, raw, checks)
        if not isinstance(raw, dict):
            checks.append(Check("CLM002", BLOCK, "%s does not parse as a YAML mapping" % path.name,
                                fix="check its indentation"))
            continue
        cid = raw.get("id")
        if cid != path.stem:
            checks.append(Check("CLM003", BLOCK, "%s: id %r does not match the filename"
                                % (path.name, cid), fix="rename it %s.yaml, or fix the id" % cid))
            continue
        author = handle(raw.get("author"))
        if author in roster.agents:
            model = raw.get("authored_by_model") or {}
            if not (model.get("model") and model.get("prompt_sha256")):
                checks.append(Check("CLM016", BLOCK, "%s: authored by agent %r with no model "
                                    "and prompt hash" % (cid, author),
                                    "an agent-authored claim must be reproducible",
                                    "add authored_by_model: {model, prompt_sha256}"))
        elif author not in roster.everyone:
            checks.append(Check("CLM005", BLOCK, "%s: author %r is on no roster" % (cid, author),
                                fix="name a member, or an agent row"))

        evidence = raw.get("evidence") or []
        evidence_ok = bool(evidence)
        if not evidence:
            checks.append(Check("CLM004", BLOCK, "%s: cites no evidence" % cid,
                                fix="every claim cites at least one committed artifact"))
        for entry in evidence:
            evidence_ok = check_evidence(repo, cid, entry, tracked, checks) and evidence_ok

        history = check_history(cid, raw, roster, checks)
        if history is None:
            continue
        for i, e in enumerate(history):
            if e["state"] in DECISIONS:
                check_decision(cid, raw, e, i, roster, checks)
        last = history[-1]
        if last["state"] == "draft" and not last.get("blocked_by"):
            checks.append(Check("CLM011", WARN, "%s: a draft that does not say what it waits on"
                                % cid, "a deferred claim names its reason",
                                "add blocked_by to the last history entry"))
        if last["state"] == "rejected" and not last.get("reason"):
            checks.append(Check("CLM012", BLOCK, "%s: rejected with no reason" % cid,
                                fix="add reason to the rejecting entry"))
        claims[cid] = {"state": last["state"], "evidence_ok": evidence_ok}

    if base:
        # A claim deleted since base has no file left to find above.
        old = git(repo, "ls-tree", "-r", "--name-only", base, "--", "ledger/claims/")
        for rel in (old or "").splitlines():
            if rel.endswith(".yaml") and not Path(rel).name.startswith("_") \
                    and not (repo / rel).exists():
                check_against_base(repo, base, rel, None, checks)
    return claims


def check_sections(repo, claims, checks):
    sdir = repo / "ledger" / "sections"
    if not sdir.is_dir():
        checks.append(Check("CLM009", DECIDE, "this syndicate has no sections yet",
                            "ledger/sections/ does not exist",
                            "mkdir -p ledger/sections, and start from "
                            "ledger/sections/_TEMPLATE.yaml"))
        return
    for path in sorted(sdir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        raw = load(path.read_text())
        if not isinstance(raw, dict):
            checks.append(Check("CLM010", BLOCK, "%s does not parse as a YAML mapping" % path.name))
            continue
        sid = raw.get("id")
        if sid != path.stem:
            checks.append(Check("CLM010", BLOCK, "%s: id %r does not match the filename"
                                % (path.name, sid), fix="rename it, or fix the id"))
            continue
        cited = raw.get("claims") or []
        if not cited:
            checks.append(Check("CLM010", BLOCK, "%s cites no claims" % sid,
                                "a section is composed of claims, not prose",
                                "cite at least one verified claim"))
            continue
        bad = 0
        for cid in cited:
            c = claims.get(cid)
            why = ("does not exist" if c is None else
                   "was rejected" if c["state"] == "rejected" else
                   "is not verified (it is %s)" % c["state"] if c["state"] != "verified" else
                   "has evidence that does not resolve" if not c["evidence_ok"] else None)
            if why:
                bad += 1
                checks.append(Check("CLM010", BLOCK, "%s cites %s, which %s" % (sid, cid, why),
                                    fix="drop the citation, or fix %s first" % cid))
        if not bad:
            checks.append(Check("CLM010", OK, "%s: all %d cited claim(s) are verified"
                                % (sid, len(cited))))


def run(repo, base=None):
    """(checks, is_mold). Computes; prints nothing."""
    checks = []
    cfg = load((repo / "syndicate.yaml").read_text()) if (repo / "syndicate.yaml").is_file() else None
    if not isinstance(cfg, dict):
        return [Check("CLM000", BLOCK, "syndicate.yaml is missing or does not parse",
                      fix="python3 tools/doctor.py")], False
    # A mold has no members to name, so it has no claims (operator rule #10).
    if M.is_unprovisioned_template(cfg):
        return checks, True
    if base and git(repo, "rev-parse", "--verify", "--quiet", base + "^{commit}") is None:
        checks.append(Check("CLM013", BLOCK, "--base %s is not a commit in this repository"
                            % base, "history cannot be compared against it",
                            "fetch it (git fetch origin), or pass a commit that exists"))
        base = None
    roster = Roster(cfg)
    for name in sorted(set(roster.agents) & set(roster.everyone)):
        checks.append(Check("CLM005", BLOCK, "%r is both a member and an agent" % name,
                            "every name must mean one party", "rename the agent row"))
    tracked = tracked_files(repo)
    if tracked is None:
        checks.append(Check("CLM004", WARN, "not a git repository: evidence was found on disk, "
                            "not confirmed committed"))
    claims = check_claims(repo, roster, tracked, base, checks)
    check_sections(repo, claims, checks)
    return checks, False


def report(checks, is_mold):
    blocked = [c for c in checks if c.status == BLOCK]
    return {
        "is_template": is_mold,
        "blocked": len(blocked),
        "decisions_owed": len([c for c in checks if c.status == DECIDE]),
        "next": blocked[0].as_dict() if blocked else None,
        "checks": [c.as_dict() for c in checks],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".", help="repository root (default: here)")
    ap.add_argument("--base", help="commit to compare claim history against (CI passes the "
                                   "PR's base); without it, CLM013 is not checked")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable, in tools/doctor.py's shape")
    a = ap.parse_args(argv)
    checks, is_mold = run(Path(a.repo).resolve(), a.base)
    out = report(checks, is_mold)
    if a.json:
        print(json.dumps(out, indent=2))
    elif is_mold:
        print("  This is the template itself: it has no members, so it has no claims "
              "(operator rule #10).")
    else:
        for c in checks:
            print("  %-6s %s  %s" % (c.status, c.key, c.headline))
            if c.detail:
                print("                 " + c.detail)
            if c.fix and c.status != OK:
                print("                 next: " + c.fix)
        if not a.base:
            print("\n  History was not compared against a base (no --base): CLM013 not checked.")
        print("\n  %d blocked, %d decision(s) owed, %d warning(s), %d ok."
              % (out["blocked"], out["decisions_owed"],
                 len([c for c in checks if c.status == WARN]),
                 len([c for c in checks if c.status == OK])))
    return 1 if out["blocked"] else 0


if __name__ == "__main__":
    sys.exit(main())
