#!/usr/bin/env python3
"""Did the people a claim names as its reviewers actually approve it?

tools/doctor_claims.py stops at WARN for every reviewer and every human-gate
approver, because a name written in a file is a declaration. This tool asks
GitHub. For each decision entry (verified or rejected) that a pull request
appends to a claim's history, the entry's reviewer - and its approved_by,
when the claim is human-gated - must hold an APPROVED review on that pull
request, of its head commit. An approval of an earlier commit does not cover
what was pushed after it, and a later dismissal or change request undoes it.

Only entries the pull request adds are checked. A decision merged earlier was
confirmed by this same check on the pull request that made it.

Nothing read from a claim file reaches a shell or a query language: names
are compared to review authors as data.

    python3 tools/confirm_approvals.py --repo . --pr 12 --base <sha> --head <sha>

GitHub is asked with GH_TOKEN (read access to pull requests is enough) at
GITHUB_API_URL, for the repository GITHUB_REPOSITORY - the variables Actions
sets.

EXIT
  0  every decision this pull request adds is backed by an approval
  1  a named reviewer or approver has not approved the head commit, or the
     pull request rewrote a claim's history (doctor_claims.py says which)
  2  GitHub could not be asked - network, rate limit, 5xx. Try again later.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:                                           # pragma: no cover
    print("confirm_approvals needs PyYAML: pip install -r tools/requirements.txt",
          file=sys.stderr)
    sys.exit(1)

DECISIONS = ("verified", "rejected")
# Review states that change whether someone approves. COMMENTED does not.
EFFECTIVE = ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")


class Transient(Exception):
    """GitHub did not answer; the question is still open."""


def git(repo, *args):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def login(value):
    return str(value).strip().lower() if value else None


def claim_at(repo, rev, rel):
    text = git(repo, "show", "%s:%s" % (rev, rel))
    data = yaml.safe_load(text) if text is not None else None
    return data if isinstance(data, dict) else None


def required_approvals(repo, base, head):
    """[(claim id, entry index, role, login)] for decisions added since base,
    plus a list of claims whose history was rewritten rather than appended."""
    fork = (git(repo, "merge-base", base, head) or "").strip()
    if not fork:
        raise SystemExit("cannot find a merge base of %s and %s - fetch full history "
                         "(actions/checkout with fetch-depth: 0)" % (base, head))
    changed = git(repo, "diff", "--name-only", "--diff-filter=AM", fork, head,
                  "--", "ledger/claims/") or ""
    needed, rewritten = [], []
    for rel in changed.splitlines():
        if not rel.endswith(".yaml") or Path(rel).name.startswith("_"):
            continue
        new = claim_at(repo, head, rel)
        if new is None:
            continue                                   # doctor_claims blocks this
        old = claim_at(repo, fork, rel) or {}
        old_h, new_h = old.get("history") or [], new.get("history") or []
        if new_h[:len(old_h)] != old_h:
            rewritten.append(Path(rel).stem)
            continue
        for i in range(len(old_h), len(new_h)):
            e = new_h[i]
            if not isinstance(e, dict) or e.get("state") not in DECISIONS:
                continue
            cid = Path(rel).stem
            needed.append((cid, i, "reviewer", login(e.get("reviewer"))))
            if new.get("human_gate") == "required" and e.get("state") == "verified":
                needed.append((cid, i, "approved_by", login(e.get("approved_by"))))
    return needed, rewritten


def fetch_reviews(repo_slug, pr):
    """Every review on the pull request, oldest first, as GitHub returns them."""
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    reviews, page = [], 1
    while True:
        url = "%s/repos/%s/pulls/%d/reviews?per_page=100&page=%d" % (api, repo_slug, pr, page)
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                   "X-GitHub-Api-Version": "2022-11-28"})
        if token:
            req.add_header("Authorization", "Bearer " + token)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                batch = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code >= 500 or e.code == 429 or \
                    (e.code == 403 and e.headers.get("x-ratelimit-remaining") == "0"):
                raise Transient("GitHub answered %d for %s" % (e.code, url))
            raise SystemExit("GitHub refused %s with %d - check the repository, the pull "
                             "request number and the token's permissions" % (url, e.code))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise Transient("could not reach GitHub: %s" % e)
        if not isinstance(batch, list):
            raise Transient("GitHub returned something that is not a list of reviews")
        reviews.extend(batch)
        if len(batch) < 100:
            return reviews
        page += 1


def approved_at(reviews, head):
    """{login: True} for everyone whose effective review approves `head`."""
    latest = {}
    for r in reviews:
        who = login((r.get("user") or {}).get("login"))
        if who and r.get("state") in EFFECTIVE:
            latest[who] = r
    return {who for who, r in latest.items()
            if r.get("state") == "APPROVED" and r.get("commit_id") == head}


def confirm(repo, repo_slug, pr, base, head, fetch=None):
    needed, rewritten = required_approvals(repo, base, head)
    lines, ok = [], True
    for cid in rewritten:
        ok = False
        lines.append("BLOCK  %s: history was rewritten, not appended - no approval can "
                     "cover that (run tools/doctor_claims.py --base %s)" % (cid, base))
    if not needed:
        lines.append("ok     no claim decision in this pull request needs an approval")
        return ok, lines
    have = approved_at((fetch or fetch_reviews)(repo_slug, pr), head)
    for cid, i, role, who in needed:
        if not who:
            ok = False
            lines.append("BLOCK  %s history[%d]: no %s named" % (cid, i, role))
        elif who in have:
            lines.append("ok     %s history[%d]: %s %s approved %s" % (cid, i, role, who, head[:12]))
        else:
            ok = False
            lines.append("BLOCK  %s history[%d]: %s %s has no approving review of %s"
                         % (cid, i, role, who, head[:12]))
    return ok, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"),
                    help="owner/name (default: $GITHUB_REPOSITORY)")
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--base", required=True, help="the pull request's base commit")
    ap.add_argument("--head", required=True, help="the pull request's head commit")
    a = ap.parse_args(argv)
    if not a.repository:
        raise SystemExit("--repository owner/name is required outside GitHub Actions")
    try:
        ok, lines = confirm(Path(a.repo).resolve(), a.repository, a.pr, a.base, a.head)
    except Transient as e:
        print("transient: %s - try again later" % e, file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
