"""The claims ledger's two tools, against throwaway repositories.

Every guard here was broken on purpose and watched to fail (CLAUDE.md: the
standard for trusting a guard is mutation testing).
"""
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import confirm_approvals as CA                                # noqa: E402
import doctor_claims as DC                                    # noqa: E402

EVIDENCE = b'{"uplift": 0.12}\n'
SHA = hashlib.sha256(EVIDENCE).hexdigest()
MEMBERS = [
    {"name": "A", "github": "Alice", "email": "a@x.org", "trust_tier": "verified"},
    {"name": "B", "github": "bob", "email": "b@x.org", "trust_tier": "verified"},
    {"name": "C", "github": "carol", "email": "c@x.org", "trust_tier": "provisional"},
    {"name": "D", "github": "dave", "email": "d@x.org", "trust_tier": "verified",
     "left": "2026-09-01"},
    {"name": "E", "github": "erin", "email": "e@x.org", "trust_tier": "verified"},
]


def claim(cid="C-0001", **kw):
    c = {"id": cid, "text": "The uplift eval measured 0.12.", "section": "cyber",
         "author": "alice",
         "evidence": [{"kind": "eval_run", "ref": "evals/run.json", "sha256": SHA}],
         "history": [{"at": "2026-09-24", "state": "draft", "by": "alice", "blocked_by": "eval"},
                     {"at": "2026-09-25", "state": "verified", "by": "alice", "reviewer": "bob"}]}
    c.update(kw)
    return c


class Repo:
    def __init__(self, path, members=MEMBERS, **cfg):
        self.path = path
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@x.org"); self.git("config", "user.name", "t")
        self.write("syndicate.yaml", {"members": members,
                                      "governance": {"formation": "multi"}, **cfg})
        self.write("evals/run.json", EVIDENCE)
        (path / "ledger" / "claims").mkdir(parents=True)
        (path / "ledger" / "sections").mkdir(parents=True)
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.path, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, rel, data):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            p.write_bytes(data)
        else:
            p.write_text(data if isinstance(data, str) else yaml.safe_dump(data, sort_keys=False))

    def claim(self, c=None, **kw):
        c = c or claim(**kw)
        self.write("ledger/claims/%s.yaml" % c["id"], c)
        return c

    def commit(self, msg="x"):
        self.git("add", "-A"); self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def doctor(self, base=None, commit=True):
        if commit:
            self.commit()
        checks, mold = DC.run(self.path, base)
        return DC.report(checks, mold)


def status(rep, key):
    return [c["status"] for c in rep["checks"] if c["check"] == key]


@pytest.fixture
def repo(tmp_path):
    return Repo(tmp_path)


# --- the ledger as a whole ----------------------------------------------------

def test_no_ledger_is_a_decision_not_a_fault(tmp_path):
    r = Repo(tmp_path)
    shutil.rmtree(tmp_path / "ledger")
    rep = r.doctor()
    assert status(rep, "CLM001") == ["DECIDE"] and status(rep, "CLM009") == ["DECIDE"]
    assert rep["blocked"] == 0


def test_the_mold_has_no_claims(tmp_path):
    r = Repo(tmp_path, members=[{"name": "x", "github": "github-handle", "email": "x@x"}])
    r.claim(author="nobody")
    rep = r.doctor()
    assert rep["is_template"] is True and rep["checks"] == []


def test_a_verified_claim_passes_and_its_reviewer_stays_a_warning(repo):
    repo.claim()
    rep = repo.doctor()
    assert rep["blocked"] == 0
    assert status(rep, "CLM004") == ["ok"]
    assert status(rep, "CLM006") == ["WARN"]          # never ok offline


def test_the_template_is_a_claim_this_checker_accepts(repo):
    t = yaml.safe_load((ROOT / "ledger/claims/_TEMPLATE.yaml").read_text())
    t["author"] = "alice"; t["history"][0]["by"] = "alice"
    t["evidence"][0].update(ref="evals/run.json", sha256=SHA)
    repo.claim(t)
    t = dict(t, history=t["history"] + [{"at": "2026-09-25", "state": "verified", "by": "alice",
                                         "reviewer": "bob", "approved_by": "erin"}])
    repo.claim(t)
    s = yaml.safe_load((ROOT / "ledger/sections/_TEMPLATE.yaml").read_text())
    repo.write("ledger/sections/%s.yaml" % s["id"], s)
    rep = repo.doctor()
    assert rep["blocked"] == 0, rep["next"]
    assert status(rep, "CLM010") == ["ok"]


# --- evidence ------------------------------------------------------------------

def _outside(repo):
    (repo.path.parent / "secret.json").write_bytes(EVIDENCE)
    return "../secret.json"

def _symlink_out(repo):
    (repo.path.parent / "secret.json").write_bytes(EVIDENCE)
    os.symlink(repo.path.parent / "secret.json", repo.path / "evals/link.json")
    return "evals/link.json"

def _untracked(repo):
    repo.write("evals/local.json", EVIDENCE)
    repo.git("rm", "-q", "--cached", "--ignore-unmatch", "evals/local.json")
    (repo.path / ".git/info/exclude").write_text("evals/local.json\n")
    return "evals/local.json"

@pytest.mark.parametrize("make_ref, sha", [
    (lambda r: "evals/missing.json", SHA),
    (lambda r: "evals/run.json", "0" * 64),
    (lambda r: "evals/run.json", "pending"),
    (_outside, SHA),
    (lambda r: str(r.path / "evals/run.json"), SHA),        # absolute
    (_symlink_out, SHA),
    (_untracked, SHA),
], ids=["missing", "wrong-hash", "pending", "dotdot", "absolute", "symlink-out", "untracked"])
def test_evidence_that_is_not_committed_bytes_blocks(repo, make_ref, sha):
    repo.claim(evidence=[{"kind": "eval_run", "ref": make_ref(repo), "sha256": sha}])
    rep = repo.doctor()
    assert "BLOCK" in status(rep, "CLM004")


@pytest.mark.parametrize("evidence", [
    [], [{"kind": "vibes", "ref": "evals/run.json", "sha256": SHA}],
    [{"kind": "eval_run", "sha256": SHA}], [{"kind": "external", "ref": "https://x"}],
    ["evals/run.json"],
], ids=["none", "unknown-kind", "no-ref", "external-no-digest", "not-a-mapping"])
def test_malformed_evidence_blocks(repo, evidence):
    repo.claim(evidence=evidence)
    assert "BLOCK" in status(repo.doctor(), "CLM004")


def test_outside_git_a_missing_file_still_blocks_and_says_why(repo):
    repo.claim(evidence=[{"kind": "eval_run", "ref": "evals/missing.json", "sha256": SHA}])
    repo.commit()
    shutil.rmtree(repo.path / ".git")                  # e.g. a notebook's unpacked copy
    rep = DC.report(*DC.run(repo.path))
    assert "BLOCK" in status(rep, "CLM004")
    assert any("not a git repository" in c["headline"] for c in rep["checks"])


def test_external_evidence_with_a_digest_is_only_a_warning(repo):
    repo.claim(evidence=[{"kind": "external", "ref": "https://x", "sha256": SHA}])
    rep = repo.doctor()
    assert status(rep, "CLM004") == ["WARN"] and rep["blocked"] == 0


# --- who is named ----------------------------------------------------------------

def decided(reviewer="bob", state="verified", **extra):
    h = claim()["history"][:1]
    return h + [dict({"at": "2026-09-25", "state": state, "by": "alice", "reviewer": reviewer,
                      "reason": "r"}, **extra)]

@pytest.mark.parametrize("kw, key", [
    ({"author": "mallory"}, "CLM005"),
    ({"history": decided(reviewer=None)}, "CLM007"),
    ({"history": decided(reviewer="ALICE")}, "CLM006"),           # case does not hide it
    ({"history": decided(reviewer="dave")}, "CLM005"),            # left: roles end (10.2)
    ({"history": decided(reviewer="mallory")}, "CLM005"),
    ({"history": decided(reviewer="carol")}, "CLM015"),           # provisional, sole (2.3)
    ({"history": claim()["history"][:1] + [{"state": "draft", "by": "mallory"}]}, "CLM005"),
])
def test_someone_who_may_not_act_blocks(repo, kw, key):
    repo.claim(**kw)
    assert "BLOCK" in status(repo.doctor(), key)


def test_a_departed_author_still_authored_it(repo):
    repo.claim(author="dave")
    assert repo.doctor()["blocked"] == 0


def test_a_provisional_reviewer_with_a_verified_approver_is_not_sole(repo):
    repo.claim(human_gate="required", history=decided(reviewer="carol", approved_by="erin"))
    rep = repo.doctor()
    assert status(rep, "CLM015") == [] and rep["blocked"] == 0


@pytest.mark.parametrize("approved_by", [None, "alice", "dave", "mallory", "bot"])
def test_the_human_gate_needs_a_current_member_other_than_the_author(tmp_path, approved_by):
    r = Repo(tmp_path, agents=[{"name": "bot"}])
    r.claim(human_gate="required", history=decided(approved_by=approved_by))
    assert "BLOCK" in status(r.doctor(), "CLM008")


def test_a_cleared_human_gate_is_still_only_a_warning(repo):
    repo.claim(human_gate="required", history=decided(approved_by="erin"))
    rep = repo.doctor()
    assert status(rep, "CLM008") == ["WARN"] and rep["blocked"] == 0


def test_agents_may_author_but_not_review(tmp_path):
    r = Repo(tmp_path, agents=[{"name": "agent-verifier"}])
    r.claim(history=decided(reviewer="agent-verifier"))
    rep = r.doctor()
    assert "BLOCK" in status(rep, "CLM005")
    assert any("is an agent" in c["headline"] for c in rep["checks"])


def test_an_agent_authored_claim_records_its_model(tmp_path):
    r = Repo(tmp_path, agents=[{"name": "agent-writer"}])
    r.claim(author="agent-writer")
    assert "BLOCK" in status(r.doctor(), "CLM016")
    r.claim(author="agent-writer", authored_by_model={"model": "m", "prompt_sha256": SHA})
    assert r.doctor()["blocked"] == 0


def test_an_agent_cannot_share_a_members_name(tmp_path):
    r = Repo(tmp_path, agents=[{"name": "Bob"}])
    assert "BLOCK" in status(r.doctor(), "CLM005")


# --- history -----------------------------------------------------------------------

@pytest.mark.parametrize("kw, key, level", [
    ({"history": []}, "CLM002", "BLOCK"),
    ({"history": [{"state": "maybe", "by": "alice"}]}, "CLM002", "BLOCK"),
    ({"history": [{"state": "draft", "by": "alice"}]}, "CLM011", "WARN"),
    ({"history": decided(state="rejected", reason=None)}, "CLM012", "BLOCK"),
    ({"history": decided(state="rejected") + [{"state": "verified", "by": "alice",
                                                "reviewer": "bob"}]}, "CLM014", "BLOCK"),
    ({"id": "C-9999"}, "CLM003", "BLOCK"),
])
def test_history_rules(repo, kw, key, level):
    c = claim(**kw); c_path = "ledger/claims/C-0001.yaml"
    repo.write(c_path, c)
    assert level in status(repo.doctor(), key)


def test_an_unparseable_claim_blocks(repo):
    repo.write("ledger/claims/C-0001.yaml", "id: [unclosed\n")
    assert "BLOCK" in status(repo.doctor(), "CLM002")


# --- append-only, against a base -------------------------------------------------------

@pytest.fixture
def based(repo):
    repo.claim()
    return repo, repo.commit("base")


def test_appending_a_decision_is_allowed(based):
    repo, base = based
    c = claim(); c["history"].append({"at": "2026-09-26", "state": "rejected", "by": "alice",
                                      "reviewer": "bob", "reason": "methodology"})
    repo.claim(c)
    rep = repo.doctor(base)
    assert status(rep, "CLM013") == [] and rep["blocked"] == 0


def _edit_entry(c): c["history"][1]["reviewer"] = "erin"
def _edit_text(c): c["text"] = "The uplift eval measured 0.02."
def _rehash(c): c["evidence"][0]["sha256"] = "1" * 64
def _drop_entry(c): c["history"].pop()

@pytest.mark.parametrize("change", [_edit_entry, _edit_text, _rehash, _drop_entry])
def test_rewriting_the_record_blocks(based, change):
    repo, base = based
    c = claim(); change(c); repo.claim(c)
    assert "BLOCK" in status(repo.doctor(base), "CLM013")


def test_a_draft_may_still_be_edited(repo):
    repo.claim(history=claim()["history"][:1])
    base = repo.commit("base")
    repo.claim(history=claim()["history"][:1], text="Sharper wording.")
    assert status(repo.doctor(base), "CLM013") == []


def test_deleting_a_claim_blocks(based):
    repo, base = based
    (repo.path / "ledger/claims/C-0001.yaml").unlink()
    assert "BLOCK" in status(repo.doctor(base), "CLM013")


def test_an_unknown_base_blocks_rather_than_skipping(repo):
    assert "BLOCK" in status(repo.doctor("f" * 40), "CLM013")


# --- sections --------------------------------------------------------------------------

@pytest.mark.parametrize("setup, cited", [
    (lambda r: None, ["C-0404"]),
    (lambda r: r.claim(history=claim()["history"][:1]), ["C-0001"]),
    (lambda r: r.claim(history=decided(state="rejected")), ["C-0001"]),
    (lambda r: r.claim(evidence=[{"kind": "eval_run", "ref": "evals/run.json",
                                  "sha256": "0" * 64}]), ["C-0001"]),
    (lambda r: r.claim(), []),
], ids=["unknown", "draft", "rejected", "broken-evidence", "empty"])
def test_a_section_cites_only_verified_claims(repo, setup, cited):
    setup(repo)
    repo.write("ledger/sections/cyber.yaml", {"id": "cyber", "claims": cited})
    assert "BLOCK" in status(repo.doctor(), "CLM010")


def test_a_section_id_must_match_its_file(repo):
    repo.claim()
    repo.write("ledger/sections/cyber.yaml", {"id": "bio", "claims": ["C-0001"]})
    assert "BLOCK" in status(repo.doctor(), "CLM010")


# --- one parser reads both doctors -------------------------------------------------------

def test_the_json_shape_is_doctors(repo):
    repo.claim(author="mallory")
    repo.commit()
    real = subprocess.run([sys.executable, str(ROOT / "tools/doctor.py"), "--json",
                           "--repo", str(repo.path)], capture_output=True, text=True)
    mine = subprocess.run([sys.executable, str(ROOT / "tools/doctor_claims.py"), "--json",
                           "--repo", str(repo.path)], capture_output=True, text=True)
    d, c = json.loads(real.stdout), json.loads(mine.stdout)
    assert list(d) == list(c)
    assert list(d["checks"][0]) == list(c["checks"][0])
    assert c["next"] == next(x for x in c["checks"] if x["status"] == "BLOCK")
    assert mine.returncode == 1


# --- confirm_approvals ---------------------------------------------------------------------

@pytest.fixture
def pr(repo):
    """A base with a draft claim; a head that verifies it, human-gated."""
    repo.claim(human_gate="required", history=claim()["history"][:1])
    base = repo.commit("base")
    repo.claim(human_gate="required", history=decided(approved_by="erin"))
    head = repo.commit("verify")
    return repo, base, head


def review(who, state, commit):
    return {"user": {"login": who}, "state": state, "commit_id": commit}


def confirm(repo, base, head, reviews):
    calls = []
    def fetch(slug, n):
        calls.append(n); return reviews
    ok, lines = CA.confirm(repo.path, "o/r", 7, base, head, fetch=fetch)
    return ok, lines, calls


def test_both_named_approvers_approved_the_head(pr):
    repo, base, head = pr
    ok, lines, _ = confirm(repo, base, head, [review("BOB", "APPROVED", head),
                                              review("erin", "APPROVED", head)])
    assert ok, lines


@pytest.mark.parametrize("reviews", [
    lambda h: [review("erin", "APPROVED", h)],                                  # bob silent
    lambda h: [review("bob", "APPROVED", "0" * 40), review("erin", "APPROVED", h)],  # stale
    lambda h: [review("bob", "APPROVED", h), review("bob", "DISMISSED", h),
               review("erin", "APPROVED", h)],
    lambda h: [review("bob", "APPROVED", h), review("bob", "CHANGES_REQUESTED", h),
               review("erin", "APPROVED", h)],
    lambda h: [review("bob", "APPROVED", h), review("mallory", "APPROVED", h)],   # wrong person
], ids=["reviewer-silent", "stale-commit", "dismissed", "changes-requested", "gate-unapproved"])
def test_a_missing_approval_blocks(pr, reviews):
    repo, base, head = pr
    ok, lines, _ = confirm(repo, base, head, reviews(head))
    assert not ok, lines


def test_a_later_comment_does_not_undo_an_approval(pr):
    repo, base, head = pr
    ok, _, _ = confirm(repo, base, head, [review("bob", "APPROVED", head),
                                          review("bob", "COMMENTED", head),
                                          review("erin", "APPROVED", head)])
    assert ok


def test_a_name_is_compared_as_data(repo):
    repo.claim(history=claim()["history"][:1])
    base = repo.commit("base")
    repo.claim(history=decided(reviewer='x" or true or "'))
    head = repo.commit()
    ok, _, _ = confirm(repo, base, head, [review("bob", "APPROVED", head)])
    assert not ok


def test_nothing_to_confirm_asks_github_nothing(repo):
    repo.claim()                                   # decided, and already in the base
    base = repo.commit("base")
    repo.write("evals/other.json", b"{}")
    head = repo.commit()
    ok, _, calls = confirm(repo, base, head, [])
    assert ok and calls == []


def test_only_decisions_this_pr_adds_need_its_approvals(based):
    repo, base = based                             # verified by bob, already merged
    c = claim(); c["history"].append({"at": "2026-09-26", "state": "rejected", "by": "alice",
                                      "reviewer": "erin", "reason": "methodology"})
    repo.claim(c)
    head = repo.commit()
    ok, lines, _ = confirm(repo, base, head, [review("erin", "APPROVED", head)])
    assert ok, lines


def test_a_new_claim_file_is_checked_too(repo):
    base = repo.commit("base")
    repo.claim()                                   # arrives already verified by bob
    head = repo.commit()
    ok, _, _ = confirm(repo, base, head, [])
    assert not ok


def test_a_rewritten_history_cannot_be_approved(based):
    repo, base = based
    c = claim(); c["history"][1]["reviewer"] = "erin"; repo.claim(c)
    head = repo.commit()
    ok, _, _ = confirm(repo, base, head, [review("erin", "APPROVED", head)])
    assert not ok


def test_github_unreachable_is_transient(pr, monkeypatch):
    repo, base, head = pr
    def down(slug, n): raise CA.Transient("503")
    monkeypatch.setattr(CA, "fetch_reviews", down)
    assert CA.main(["--repo", str(repo.path), "--repository", "o/r", "--pr", "7",
                    "--base", base, "--head", head]) == 2


# --- the workflow cannot hide a failure ------------------------------------------------------

def test_the_workflow_cannot_mask_an_exit_code():
    wf = yaml.safe_load((ROOT / ".github/workflows/verify-claims.yml").read_text())
    on = wf[True]
    assert "paths" not in (on.get("pull_request") or {}), "evidence can live outside ledger/"
    assert "pull_request_review" in on, "approvals arrive after the push they approve"
    for job in wf["jobs"].values():
        for step in job["steps"]:
            run = step.get("run", "")
            if "tools/" in run:
                assert "|" not in run, "a pipe hides the tool's exit status: %r" % run


def test_claude_md_states_these_tools_exit_codes():
    table = (ROOT / "CLAUDE.md").read_text()
    for tool, codes in (("doctor_claims.py", "0 ok · 1 blocked"),
                        ("confirm_approvals.py", "0 · 1 human · 2 transient")):
        row = next(l for l in table.splitlines() if l.startswith("| `tools/%s`" % tool))
        assert row.rstrip(" |").endswith(codes), row
        doc = (ROOT / "tools" / tool).read_text().split("EXIT", 1)[1].split("\n\n")[0]
        assert re.findall(r"^\s+(\d)\s", doc, re.M) == re.findall(r"\d", codes), tool
