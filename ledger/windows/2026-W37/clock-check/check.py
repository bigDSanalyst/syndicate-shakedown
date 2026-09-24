#!/usr/bin/env python3
"""Would 2026-W37 differ if it were computed on the clock Agreement 4.2 names?

W37's evidence.json records its own clock: "committer dates; push-time gating
is the admissible clock per 4.2 (v1 limitation)". Agreement 4.2 says "Server-
side timestamps govern. Dates embedded in commits are not evidence of time."
This script recomputes the window on push times - when each commit first
reached GitHub, from the repository's server-side event log - and compares.

Run from the repository root, in a full (not shallow) clone, with network
access to the GitHub API (merges and reviews are read from it, as
attribution.py always does):

    python3 ledger/windows/2026-W37/clock-check/check.py           # check
    python3 ledger/windows/2026-W37/clock-check/check.py --write   # and refresh outputs

1. Reads events-page-*.json: the GitHub events API as fetched (see
   ../CLOCK-CHECK.md for when). GitHub keeps at most 300 events or 90 days,
   so these files are the only lasting copy of the push record.
2. Gives each commit the time of the first push that delivered it. Pushes
   are replayed oldest first; a push delivers the commits between its
   `before` and `head` that no earlier push delivered. A commit reachable
   from a push's `before` but never itself delivered was already on the
   server: it gets that push's time as an upper bound.
3. Clones this repository at the window's head, with tools/attribution.py as
   it was at TOOL_REV - the version that produced W37 - and runs the window
   three times, sharing one GitHub API response cache:
     committer  unchanged; must reproduce the recorded attribution.csv
     push       commit dates replaced by push dates; the question asked
     control    push dates, with one member commit moved out of the window;
                must NOT reproduce the record - if it did, the substitution
                would not be reaching the tool and "push" would prove nothing

EXIT
  0  committer reproduces the record, push matches it, control differs
  1  any of those does not hold
"""
import argparse, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOW_DIR = HERE.parent
LABEL, START, END = "2026-W37", "2026-08-31", "2026-09-07"
WINDOW_HEAD = "326bd1c2784f2779b8326c4de925de4b0a8a30b8"   # evidence.json window_head
TOOL_REV = "e42de24f9ba1448d68f383412943ace2f581c4f2"      # last change to attribution.py; committed W37
CONTROL = "5be58a027dca241149b305cb1bcc9d12adf593bc"       # a bigDSanalyst commit inside the window
ORIGIN = "https://github.com/bigDSanalyst/syndicate-shakedown"
KEYS = ("window", "members", "weights_used", "raw", "survivor_weight")


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.split()


def push_times(repo):
    events = []
    for page in sorted(HERE.glob("events-page-*.json")):
        events += json.loads(page.read_text())
    pushes = sorted((e for e in events if e["type"] == "PushEvent"),
                    key=lambda e: (e["created_at"], int(e["id"])))
    seen = {}
    for e in pushes:
        before, head, t = e["payload"]["before"], e["payload"]["head"], e["created_at"]
        if set(before) == {"0"}:                       # a new branch: whatever was not already there
            delivered = git(repo, "rev-list", head, "--not", *seen) if seen else git(repo, "rev-list", head)
        else:
            delivered = git(repo, "rev-list", "%s..%s" % (before, head))
            for sha in git(repo, "rev-list", before):
                seen.setdefault(sha, {"at": t, "upper_bound": True})
        for sha in delivered:
            seen.setdefault(sha, {"at": t, "upper_bound": False})
    return events, seen


def run_window(repo, clock):
    """{mode: (csv text, evidence dict)} for committer, push and control runs."""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        w = Path(tmp) / "w"
        subprocess.run(["git", "clone", "-q", str(repo), str(w)], check=True)
        subprocess.run(["git", "checkout", "-q", WINDOW_HEAD], cwd=w, check=True)
        subprocess.run(["git", "remote", "set-url", "origin", ORIGIN], cwd=w, check=True)
        (w / "tools" / "attribution.py").write_text(subprocess.run(
            ["git", "show", TOOL_REV + ":tools/attribution.py"], cwd=repo, check=True,
            capture_output=True, text=True).stdout)
        spec = importlib.util.spec_from_file_location("attribution_w37", w / "tools" / "attribution.py")
        A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
        real_sh, real_api, cache = A.sh, A.api_get, {}

        def api_get(url):
            if url not in cache:
                cache[url] = real_api(url)
            return cache[url]

        def dated(dates):
            def sh(*args, cwd):
                text = real_sh(*args, cwd=cwd)
                if "--pretty=format:%H|%an|%ae|%cd" not in args:
                    return text
                lines = []
                for ln in text.splitlines():
                    f = ln.split("|")
                    if len(f) == 4 and len(f[0]) == 40:
                        f[3] = dates[f[0]]             # KeyError: a commit with no push time
                        ln = "|".join(f)
                    lines.append(ln)
                return "\n".join(lines)
            return sh

        pushed = {sha: v["at"][:10] for sha, v in clock.items()}
        control = dict(pushed, **{CONTROL: "2026-09-09"})
        A.api_get = api_get
        for mode, sh in (("committer", real_sh), ("push", dated(pushed)), ("control", dated(control))):
            A.sh = sh
            sys.argv = ["attribution.py", "--repo", str(w), "--since", START, "--until", END,
                        "--label", LABEL]
            try:
                A.main()
            except SystemExit as e:
                if e.code not in (None, 0):
                    raise
            d = w / "ledger" / "windows" / LABEL
            out[mode] = ((d / "attribution.csv").read_text(),
                         json.loads((d / "evidence.json").read_text()))
            shutil.rmtree(d)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="refresh the output files beside this script")
    a = ap.parse_args()
    repo = Path(git(".", "rev-parse", "--show-toplevel")[0])

    events, clock = push_times(repo)
    log = subprocess.run(["git", "log", "--pretty=format:%H|%cd|%ae", "--date=short", WINDOW_HEAD],
                         cwd=repo, check=True, capture_output=True, text=True).stdout.splitlines()
    moved = []
    for ln in log:
        sha, cd, _ = ln.split("|")
        pd = clock[sha]["at"][:10]
        if (START <= cd <= END) != (START <= pd <= END):
            moved.append(sha[:7])
    print("events: %d (oldest %s); commits up to the window head: %d, every one with a push time"
          % (len(events), min(e["created_at"] for e in events), len(log)))
    print("commits whose W37 membership depends on the clock: %s" % (", ".join(moved) or "none"))

    runs = run_window(repo, clock)
    recorded_csv = (WINDOW_DIR / "attribution.csv").read_text()
    recorded_ev = json.loads((WINDOW_DIR / "evidence.json").read_text())
    same = {m: (csv == recorded_csv and all(ev[k] == recorded_ev[k] for k in KEYS))
            for m, (csv, ev) in runs.items()}
    ok = same["committer"] and same["push"] and not same["control"]
    print("committer run reproduces the recorded window: %s" % same["committer"])
    print("push-clock run matches the recorded window:   %s" % same["push"])
    print("control run differs from it (as it must):     %s" % (not same["control"]))
    print("RESULT: %s" % ("W37 is the same on either clock" if ok else "NOT established - see above"))

    if a.write:
        (HERE / "push-times.json").write_text(json.dumps(clock, indent=2, sort_keys=True) + "\n")
        for m, (csv, _) in runs.items():
            (HERE / ("%s.csv" % m)).write_text(csv)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
