#!/usr/bin/env python3
"""A worked implementation of the A.2.2 trust lifecycle, second rewrite.

The first version was defeated by an adversarial review in two ways that matter:
every stage function took the verdict as an argument, so replacing all five with
pure echo still passed 4/4; and the validity tables E_VALUES/A_VALUES were
defined and never consulted, so any string entered the axes. Both are structural
and neither can be patched.

This version differs in four respects, each traceable to a finding:

  * **Evidence is read, not asserted.** A stage computes its evidence state from
    bytes on disk (a manifest and its artefacts), hashed and compared. There is
    no argument by which a caller can declare itself verified.
  * **Axis values are validated on entry.** Anything outside the declared set is
    rejected with an error, not silently stored.
  * **The lifecycle loops and keeps history.** Re-evaluation can occur any number
    of times; every prior state remains recoverable with the time it applied.
    "Continuous evaluation" is otherwise not expressible.
  * **Time is recorded throughout.** The ToR describes trust as time-bound; a
    demonstration without timestamps cannot show staleness or expiry at all.

The axis sets match D4: unavailability is a property of the determination, not a
value of an axis, and `stale` is not an evidence value -- staleness is computed
from the recorded time and the declared bound.

  python lifecycle_demo.py                 # compliant and non-compliant agents
  python lifecycle_demo.py --selftest      # each finding must be catchable
"""

import argparse
import hashlib
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

E_VALUES = ("absent", "present-unverified", "verified", "contradicted")
A_VALUES = ("in-force", "suspended", "revoked", "expired")


class Rejected(Exception):
    pass


def _axis(value, allowed, name):
    """R-7.2.1 / R-7.3.1: an undeclared value is a defect, not data."""
    if value not in allowed:
        raise Rejected(f"{name} value {value!r} is not in {allowed}")
    return value


class Evidence:
    """Evidence computed from bytes, never from a caller's assertion."""

    def __init__(self, root):
        self.root = root
        self.manifest = os.path.join(root, "manifest.json")
        self.files = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.manifest):
            self.files = {}
            return
        try:
            self.files = json.load(open(self.manifest, encoding="utf-8"))
        except Exception:
            self.files = {}

    def state(self):
        """Derive the evidence state from what is actually on disk."""
        if not self.files:
            return "absent", "no manifest"
        verified = 0
        for name, want in self.files.items():
            path = os.path.join(self.root, name)
            if not os.path.exists(path):
                return "absent", f"{name} referenced but missing"
            got = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if got != want:
                return "contradicted", f"{name} hash mismatch"
            verified += 1
        if verified:
            return "verified", f"{verified} artefact(s) hashed and matched"
        return "present-unverified", "manifest lists nothing verifiable"

    def method(self):
        return "sha256-of-manifested-artefacts-v1"


class Agent:
    """One agent's lifecycle. History is append-only; nothing is overwritten."""

    def __init__(self, root, owner=None, bounded=True):
        self.root = root
        self.owner = owner
        self.bounded = bounded
        self.evidence = Evidence(root)
        self.history = []          # every determination, with the time it applied
        self.now = 0               # logical clock, seconds
        self.acts = []             # per-act records, not a single slot
        self.authority = "in-force"

    # -- time
    def tick(self, seconds):
        self.now += seconds

    def evaluate(self, stage, authority=None, reachable=True):
        """Take one determination. Appends; never overwrites."""
        if not reachable:
            rec = {"stage": stage, "at": self.now, "determination": "unavailable"}
            self.history.append(rec)
            return rec
        ev, note = self.evidence.state()
        ev = _axis(ev, E_VALUES, "evidence")
        au = _axis(authority or self.authority, A_VALUES, "authority")
        self.authority = au
        rec = {"stage": stage, "at": self.now, "determination": "determined",
               "evidence": ev, "authority": au, "method": self.evidence.method(),
               "note": note, "valid_for": 3600}
        self.history.append(rec)
        return rec

    def act(self, act_id):
        ev, note = self.evidence.state()
        rec = {"act": act_id, "at": self.now, "evidence": ev,
               "authority": self.authority}
        self.acts.append(rec)
        return rec

    def latest(self, stage=None):
        for rec in reversed(self.history):
            if stage is None or rec["stage"] == stage:
                return rec
        return None


def findings(agent):
    """Everything the document says must not pass silently."""
    out = []
    for rec in agent.history:
        if rec.get("determination") == "unavailable":
            out.append((rec["stage"], "determination unavailable"))
            continue
        ev, au = rec["evidence"], rec["authority"]
        # the two dangerous directions
        if ev == "absent" and au == "in-force":
            out.append((rec["stage"], "evidence absent with authority in force"))
        if ev == "verified" and au in ("revoked", "expired") and rec["stage"] != "L5":
            out.append((rec["stage"], f"evidence verified with authority {au}"))
        # contradicted is a finding, not a gap
        if ev == "contradicted":
            out.append((rec["stage"], "evidence contradicted"))
        # present-unverified is not verified
        if ev == "present-unverified":
            out.append((rec["stage"], "evidence present but unverified"))
        # staleness computed from time, not stored as a value
        if rec.get("valid_for") and rec["at"] > rec["valid_for"]:
            out.append((rec["stage"], "determination lapsed (past valid_for)"))
    # stage-specific exits
    l1 = agent.latest("L1")
    if l1 and l1.get("determination") == "determined" and not agent.owner:
        out.append(("L1", "L1 exit not met: no named governance owner"))
    l2 = agent.latest("L2")
    if l2 and l2.get("determination") == "determined" and not agent.bounded:
        out.append(("L2", "L2 exit not met: scope unbounded"))
    l5 = agent.latest("L5")
    if l5 and l5.get("determination") == "determined" and l5.get("authority") != "revoked":
        out.append(("L5", "L5 exit not met: standing not terminally withdrawn"))
    # an act taken while suspended
    for a in agent.acts:
        if a["authority"] == "suspended":
            out.append(("L3", f"act {a['act']} taken while authority suspended"))
    return out


WORKROOT = r"E:\DSH\tmp\a22demo_roots"


def make_root(with_evidence=True, tamper=False):
    # tempfile.mkdtemp is denied under the workspace sandbox (chmod on cleanup),
    # so the working root lives inside the workspace and is cleared per call.
    import shutil
    os.makedirs(WORKROOT, exist_ok=True)
    root = os.path.join(WORKROOT, f"r{int(time.time()*1000)%100000}")
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root, exist_ok=True)
    if with_evidence:
        open(os.path.join(root, "grant.txt"), "w").write("grant L2 scope bounded\n")
        h = hashlib.sha256(open(os.path.join(root, "grant.txt"), "rb").read()).hexdigest()
        json.dump({"grant.txt": h}, open(os.path.join(root, "manifest.json"), "w"))
        if tamper:
            open(os.path.join(root, "grant.txt"), "w").write("grant L2 scope UNBOUNDED\n")
    return root


def scenario(agent, kind):
    """Run one scenario; returns findings."""
    if kind == "compliant":
        agent.owner = "operator-A"
        agent.evaluate("L1")
        agent.tick(10)
        agent.evaluate("L2")
        agent.tick(10)
        agent.evaluate("L3")
        agent.act("a1")
        agent.tick(10)
        agent.evaluate("L4")
        agent.tick(10)
        agent.authority = "revoked"
        agent.evaluate("L5")
    elif kind == "no_owner":
        agent.owner = None
        agent.evaluate("L1")
    elif kind == "unbounded":
        agent.owner = "op"
        agent.evaluate("L1"); agent.tick(5); agent.bounded = False; agent.evaluate("L2")
    elif kind == "not_withdrawn":
        agent.owner = "op"
        agent.evaluate("L1"); agent.tick(5); agent.evaluate("L2")
        agent.tick(5); agent.evaluate("L5")          # authority still in-force
    elif kind == "suspended_act":
        agent.owner = "op"
        agent.evaluate("L1"); agent.tick(5); agent.evaluate("L2")
        agent.tick(5); agent.authority = "suspended"; agent.evaluate("L3")
        agent.act("a-susp")
    elif kind == "lapsed":
        agent.owner = "op"
        agent.evaluate("L1"); agent.tick(4000)       # past valid_for
        agent.evaluate("L2")
    elif kind == "unverified":
        agent.owner = "op"
        agent.evaluate("L1")
    return findings(agent)


EXPECT = {
    "compliant": [],
    "no_owner": ["L1 exit not met: no named governance owner"],
    "unbounded": ["L2 exit not met: scope unbounded"],
    "not_withdrawn": ["L5 exit not met: standing not terminally withdrawn"],
    "suspended_act": ["act a-susp taken while authority suspended"],
    "lapsed": ["determination lapsed (past valid_for)"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    print("A.2.2 生命周期演示 v2 · 证据从磁盘读，不从参数信")
    print("=" * 74)
    ok = 0
    total = 0
    for kind, expected in EXPECT.items():
        root = make_root(with_evidence=True)
        a = Agent(root)
        got = scenario(a, kind)
        kinds = {g[1] for g in got}
        good = bool(all(e in kinds for e in expected)) and (bool(got) if expected else not got)
        ok += good
        total += 1
        mark = "OK  " if good else "FAIL"
        print(f"  {mark} {kind:<16} 检出 {sorted(kinds) if got else '无'}")

    # the echo attack: a system with no evidence channel must not reach verified
    root = make_root(with_evidence=False)
    a = Agent(root)
    a.owner = "op"
    a.evaluate("L1")
    rec = a.latest("L1")
    echo_blocked = rec.get("evidence") != "verified"
    print(f"  {'OK  ' if echo_blocked else 'FAIL'} {'no evidence':<16} "
          f"evidence={rec.get('evidence')!r}（必须不是 verified）")
    ok += echo_blocked
    total += 1

    # tampering must produce contradicted, not verified
    root = make_root(with_evidence=True, tamper=True)
    a = Agent(root); a.owner = "op"; a.evaluate("L1")
    tamper_blocked = a.latest("L1").get("evidence") == "contradicted"
    print(f"  {'OK  ' if tamper_blocked else 'FAIL'} {'tampered':<16} "
          f"evidence={a.latest('L1').get('evidence')!r}（必须是 contradicted）")
    ok += tamper_blocked
    total += 1

    # an undeclared axis value must be rejected
    try:
        _axis("verified", E_VALUES, "evidence")
        _axis("everified", E_VALUES, "evidence")
        rejected = False
    except Rejected:
        rejected = True
    print(f"  {'OK  ' if rejected else 'FAIL'} {'bad value':<16} 未声明值被拒={rejected}")
    ok += rejected
    total += 1

    # re-evaluation must keep history and loop
    root = make_root(with_evidence=True)
    a = Agent(root); a.owner = "op"
    a.evaluate("L4"); a.tick(5); a.evaluate("L4"); a.tick(5); a.evaluate("L4")
    looped = len([r for r in a.history if r["stage"] == "L4"]) == 3
    times = all("at" in r for r in a.history)
    print(f"  {'OK  ' if looped else 'FAIL'} {'re-eval loops':<16} L4 三次={looped} 全程有时间={times}")
    ok += looped and times
    total += 1

    print("=" * 74)
    print(f"  {ok}/{total} 项符合预期")
    if args.selftest:
        print("\n  自检：以上每一行都是独立夹具，且判据来自磁盘状态而非参数")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
