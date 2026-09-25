"""A window's days are UTC days (syndicate-genesis FINDINGS row 75).

`git log --date=short` prints a commit's date in the zone its committer set,
so a window mixed +10:00 and UTC calendars: the same instant could count for
one member and be dropped for the other, and a +10:00 commit could open the
default window on its local day and fall outside it on the real one. These
drive this repository's own tools/attribution.py over a throwaway history.
"""
import os, shutil, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MEMBERS = {"a": "51167247+bigDSanalyst@users.noreply.github.com",
           "b": "205302507+satsolverv124@users.noreply.github.com"}


def attribution():
    import importlib.util
    spec = importlib.util.spec_from_file_location("attribution_under_test",
                                                  ROOT / "tools" / "attribution.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def git(repo, *args, env=None):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def window(tmp_path, monkeypatch, commits, bounds=()):
    """Run a window over `commits` = [(member key, filename, ISO time with zone)]."""
    repo = tmp_path / "r"
    (repo / "ledger" / "windows").mkdir(parents=True)
    shutil.copy(ROOT / "syndicate.yaml", repo / "syndicate.yaml")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=Setup", "-c", "user.email=setup@example.invalid",
        "commit", "-q", "-m", "setup")
    for who, name, stamp in commits:
        (repo / name).write_text("x" * 40, encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "-c", "user.name=M", "-c", "user.email=" + MEMBERS[who], "commit", "-q",
            "-m", "work " + name,
            env=dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp))
    git(repo, "remote", "add", "origin", "https://github.com/example/syn.git")
    mod = attribution()
    monkeypatch.setattr(mod, "api_get", lambda url: ([], ""))
    monkeypatch.setattr(mod, "api_paged", lambda url: [])
    monkeypatch.setattr(sys, "argv", ["attribution.py", "--repo", str(repo), *bounds])
    mod.main()
    csv, = (repo / "ledger" / "windows").rglob("attribution.csv")
    return {ln.split(",")[0]: ln.split(",")[-1]
            for ln in csv.read_text(encoding="utf-8").splitlines()[1:]}


def test_the_same_instant_counts_the_same_from_any_time_zone(tmp_path, monkeypatch):
    shares = window(tmp_path, monkeypatch, [
        ("a", "a.md", "2026-09-08T06:00:00+10:00"),          # 20:00 UTC on the 7th
        ("b", "b.md", "2026-09-07T20:00:00+00:00")],
        ("--since", "2026-09-01", "--until", "2026-09-07"))
    assert shares["bigDSanalyst"] == shares["satsolverv124"] != "0.0000", shares


def test_the_earliest_commit_falls_inside_its_own_default_window(tmp_path, monkeypatch):
    shares = window(tmp_path, monkeypatch, [("a", "a.md", "2026-09-08T06:00:00+10:00")])
    assert shares["bigDSanalyst"] == "1.0000", shares
