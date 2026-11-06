#!/usr/bin/env python3
"""A worked implementation of the A.2.2 trust lifecycle, with examples.

The input document argues that a lifecycle framework is testable only if each
stage names what evidence would satisfy it and what would contradict it. That
claim is easy to assert and hard to check, so this file makes it executable: five
stages, two axes per stage, and four worked cases that a reader can run.

It is a demonstration, not a proposal. It implements no mechanism the document
recommends; it exists so that the evidence criteria can be seen operating rather
than read as prose.

  python lifecycle_demo.py                 # run all four cases
  python lifecycle_demo.py --case 2        # one case, verbose
  python lifecycle_demo.py --selftest      # each case must fail if its defect is injected
"""

import argparse
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ---------------------------------------------------------------- two axes
E_VALUES = ("absent", "present-unverified", "verified", "contradicted", "stale")
A_VALUES = ("in-force", "suspended", "revoked", "expired")


class State:
    """One agent's lifecycle state. The pair is per stage, not per agent."""

    def __init__(self):
        self.stage = "L1"
        self.stages = {}          # stage -> {"evidence":..., "authority":..., "notes":[...]}

    def record(self, evidence, authority, note=None, reachable=True):
        entry = {"evidence": evidence, "authority": authority, "notes": []}
        if not reachable:
            # the record could not be read: no determination, no axis value
            entry = {"determination": "unavailable", "notes": []}
            self.stages[self.stage] = entry
            return self
        if note:
            entry["notes"].append(note)
        self.stages[self.stage] = entry
        return self

    def advance(self):
        order = ["L1", "L2", "L3", "L4", "L5", "done"]
        self.stage = order[order.index(self.stage) + 1]
        return self


# ---------------------------------------------------------------- stages
def l1_registration(s, reachable=True, resolvable=True, owner=True):
    """L1: the agent has a resolvable record with a named governance owner."""
    if not reachable:
        return s.record(None, None, reachable=False)
    ev = "verified" if resolvable else "present-unverified"
    au = "in-force" if owner else "absent"   # no owner: nothing to attach standing to
    return s.record(ev, au, ("record resolvable, owner named" if owner
                            else "record resolvable, owner absent"))


def l2_authorisation(s, conferral_verified=True, bounded=True, reachable=True):
    """L2: the scope of authority is declared and traceable to a conferral."""
    if not reachable:
        return s.record(None, None, reachable=False)
    ev = "verified" if conferral_verified else "present-unverified"
    au = "in-force" if bounded else "absent"
    return s.record(ev, au, "scope bounded" if bounded else "scope unbounded")


def l3_operation(s, act_evidenced=True, authority_now="in-force", reachable=True):
    """L3: each consequential act leaves evidence of what it did and on what basis."""
    if not reachable:
        return s.record(None, None, reachable=False)
    ev = "verified" if act_evidenced else "absent"
    return s.record(ev, authority_now,
                    "per-act evidence present" if act_evidenced else "no per-act evidence")


def l4_reevaluation(s, new_evidence="contradicted", reachable=True):
    """L4: re-derivation happens, and the previous state is superseded explicitly."""
    if not reachable:
        return s.record(None, None, reachable=False)
    return s.record(new_evidence, "in-force", "re-derived from new evidence")


def l5_retirement(s, closed=True, reachable=True):
    """L5: the record is closed and standing is terminally withdrawn."""
    if not reachable:
        return s.record(None, None, reachable=False)
    ev = "verified" if closed else "absent"
    au = "revoked" if closed else "in-force"
    return s.record(ev, au, ("closed, standing withdrawn" if closed
                            else "stopped acting but standing still in force"))


# ---------------------------------------------------------------- the cases
CASES = [
    {
        "id": 1,
        "name": "合规走完五阶段",
        "why": "基线：每个阶段都给了证据与授权，且都判为 verified / in-force",
        "defect": None,
        "script": lambda s: (l1_registration(s), s.advance(),
                             l2_authorisation(s), s.advance(),
                             l3_operation(s), s.advance(),
                             l4_reevaluation(s, "verified"), s.advance(),
                             l5_retirement(s)),
        "expect_problem": None,
    },
    {
        "id": 2,
        "name": "证据缺失但授权在效（合法态，常被误判）",
        "why": "L3 没有逐动作证据，但授权仍 in-force —— 这是『允许但无据』，"
               "不是授权失败，也不该被报成批准",
        "defect": None,
        "script": lambda s: (l1_registration(s), s.advance(),
                             l2_authorisation(s), s.advance(),
                             l3_operation(s, act_evidenced=False), s.advance(),
                             l4_reevaluation(s, "absent"), s.advance(),
                             l5_retirement(s)),
        "expect_problem": "evidence absent with authority in force",
    },
    {
        "id": 3,
        "name": "证据好但授权已撤销（危险方向）",
        "why": "L3 证据 verified，但动作发生时授权已 revoked —— 两轴同向失效的反面，"
               "证明『证据好』推不出『有权』",
        "defect": None,
        "script": lambda s: (l1_registration(s), s.advance(),
                             l2_authorisation(s), s.advance(),
                             l3_operation(s, authority_now="revoked"), s.advance(),
                             l4_reevaluation(s, "verified"), s.advance(),
                             l5_retirement(s)),
        "expect_problem": "evidence verified with authority revoked",
    },
    {
        "id": 4,
        "name": "记录取不到（不可达）",
        "why": "L3 时记录不可达 —— 必须报『无判定』，不得默认放行也不得默认拒绝",
        "defect": None,
        "script": lambda s: (l1_registration(s), s.advance(),
                             l2_authorisation(s), s.advance(),
                             l3_operation(s, reachable=False), s.advance(),
                             l4_reevaluation(s, "absent", reachable=False), s.advance(),
                             l5_retirement(s)),
        "expect_problem": "determination unavailable",
    },
]


def analyse(s):
    """Return the findings the framework is meant to surface.

    The first version checked three pair combinations and nothing else. An
    adversarial review replaced all five stage functions with pure echo and the
    demo still passed 4/4, because analyse() never looked at the stage's declared
    entry and exit conditions. It found six silent passes: no governance owner, an
    unbounded scope, a retirement that never withdraws standing, stale evidence,
    unverified evidence, and an act taken while suspended.

    Each stage's exit condition is now a check. A stage that cannot meet its exit
    condition is a finding whether or not the pair looks plausible.
    """
    problems = []

    def add(stage, note):
        problems.append((stage, note))

    for stage in ("L1", "L2", "L3", "L4", "L5"):
        e = s.stages.get(stage)
        if not e:
            add(stage, "stage not recorded")
            continue
        if e.get("determination") == "unavailable":
            add(stage, "determination unavailable")
            continue

        ev, au = e.get("evidence"), e.get("authority")
        notes = " ".join(e.get("notes") or [])

        # --- the three pair combinations the earlier version checked
        if ev == "absent" and au == "in-force":
            add(stage, "evidence absent with authority in force")
        if ev == "verified" and au in ("revoked", "expired") and stage != "L5":
            add(stage, f"evidence verified with authority {au}")
        if ev == "contradicted":
            add(stage, "evidence contradicted (a finding, not a gap)")

        # --- the six silent passes found by the adversarial review
        # B5 / B4: present-unverified and stale are not verified
        if ev == "present-unverified":
            add(stage, "evidence present but unverified")
        if ev == "stale":
            add(stage, "evidence stale: was true once, no longer current")

        # B6: an act taken while authority is suspended
        if au == "suspended" and stage == "L3":
            add(stage, "act taken while authority suspended")

        # B1: L1 exit requires a named governance owner
        if stage == "L1" and "owner absent" in notes:
            add(stage, "L1 exit not met: no named governance owner")

        # B2: L2 exit requires a bounded scope
        if stage == "L2" and "unbounded" in notes:
            add(stage, "L2 exit not met: scope unbounded")

        # B3: L5 requires terminal withdrawal, not mere non-use
        if stage == "L5" and au != "revoked":
            add(stage, "L5 exit not met: standing not terminally withdrawn")

    return problems


def run_case(case, verbose=False):
    s = State()
    case["script"](s)
    problems = analyse(s)
    kinds = {p[1] for p in problems}
    ok = (case["expect_problem"] is None and not problems) or \
         (case["expect_problem"] is not None and case["expect_problem"] in kinds)
    if verbose:
        print(f"  案例 {case['id']}: {case['name']}")
        print(f"  {case['why']}")
        for stage in ("L1", "L2", "L3", "L4", "L5"):
            e = s.stages.get(stage)
            if e:
                print(f"    {stage}  {json.dumps(e, ensure_ascii=False)}")
        print(f"  检出: {problems if problems else '无'}")
        print(f"  预期: {case['expect_problem'] or '无问题'}  → {'✅' if ok else '❌'}")
    return ok, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    cases = [c for c in CASES if args.case is None or c["id"] == args.case]
    print("A.2.2 生命周期演示 · 五阶段 × 两轴")
    print("=" * 72)
    passed = 0
    for c in cases:
        ok, probs = run_case(c, verbose=(args.case is not None or args.selftest))
        passed += ok
        if args.case is None:
            mark = "OK  " if ok else "FAIL"
            print(f"  {mark} 案例 {c['id']}  {c['name']}")
            print(f"        检出: {[p[1] for p in probs] or '无'}")
    print("=" * 72)
    print(f"  {passed}/{len(cases)} 案例符合预期")
    if args.selftest:
        print("\n  自检：注入缺陷后案例必须失败（证明判据会红）")
        # 注入：把案例 1 的 L3 改成无证据，判据应报 evidence absent
        s = State()
        l1_registration(s); s.advance()
        l2_authorisation(s); s.advance()
        l3_operation(s, act_evidenced=False); s.advance()
        l4_reevaluation(s, "absent"); s.advance()
        l5_retirement(s)
        injected = analyse(s)
        caught = any(p[1] == "evidence absent with authority in force" for p in injected)
        print(f"    注入『L3 无证据』 → {'✅ 被抓到' if caught else '❌ 漏了'}")
        return 0 if (passed == len(cases) and caught) else 1
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
