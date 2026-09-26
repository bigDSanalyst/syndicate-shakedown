"""tools/anchor.py must not exit 0 when it could not reach the calendars.

Ported from syndicate-genesis rows 62, 73, 74 and 76. These drive this
repository's own anchor.py with a fake `ots`, so they never touch the network.
"""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANCHOR = ROOT / "tools" / "anchor.py"


def repo_with(tmp_path, status, with_ots):
    repo = tmp_path / "r"
    log = repo / "ledger" / "anchors"
    log.mkdir(parents=True)
    (log / "0001-x.json").write_text('{"a":1}', encoding="utf-8")
    if with_ots:
        (log / "0001-x.json.ots").write_text("stub", encoding="utf-8")
    (log / "log.jsonl").write_text(json.dumps({
        "seq": 1, "anchor_id": "0001-x", "manifest": "ledger/anchors/0001-x.json",
        "manifest_sha256": "0" * 64, "status": status,
        "created": "2099-01-01T00:00:00Z"}) + "\n", encoding="utf-8")
    return repo


def upgrade(repo, bindir, only=False):
    path = str(bindir) if only else str(bindir) + os.pathsep + os.environ["PATH"]
    env = {"PATH": path, "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")} if only \
        else dict(os.environ, PATH=path)
    r = subprocess.run([sys.executable, str(ANCHOR), "upgrade", "--repo", str(repo)],
                       text=True, capture_output=True, env=env)
    return r.returncode, r.stdout + r.stderr


def shim(tmp_path, body, name="bin"):
    d = tmp_path / name
    d.mkdir()
    (d / "ots").write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
    (d / "ots").chmod(0o755)
    return d


UNREACHABLE = ('echo "Calendar https://alice.btc.calendar.opentimestamps.org: '
               'Tunnel connection failed: 403 Forbidden" >&2\nexit 1')


def test_an_unreachable_calendar_is_transient_not_pending(tmp_path):
    code, out = upgrade(repo_with(tmp_path, "pending", True), shim(tmp_path, UNREACHABLE))
    assert code == 2, out
    assert "not yet in a Bitcoin block" not in out, out


def test_an_anchor_that_could_not_be_submitted_is_transient(tmp_path):
    code, out = upgrade(repo_with(tmp_path, "unsubmitted", False), shim(tmp_path, UNREACHABLE))
    assert code == 2, "an anchor nobody could submit exited %d:\n%s" % (code, out)


def test_a_broken_install_needs_a_human(tmp_path):
    dead = tmp_path / "dead"
    dead.mkdir()
    (dead / "ots").write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
    (dead / "ots").chmod(0o755)
    # Only the dead shim on PATH: execvp would otherwise fall through to a real ots.
    code, out = upgrade(repo_with(tmp_path, "unsubmitted", False), dead, only=True)
    assert code == 1, "a broken ots install exited %d:\n%s" % (code, out)
    # Exit 1 alone is not enough: an unhandled traceback also exits 1, and the
    # pre-port anchor.py passed this test exactly that way.
    assert "Traceback" not in out and "will not run" in out, out
