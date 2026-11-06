# A.2.2 — Trust lifecycle framework, with a runnable demo

Input document for ITU-T FG-TIDA work item **A.2.2** (a trust lifecycle framework
for agentic AI), with an executable demonstration of its evidence criteria.

**Status:** material for discussion, not settled positions. Not submitted.

## Contents

| File | What it is |
|---|---|
| `A22.md` | the input document: five lifecycle stages, two axes, per-stage evidence criteria |
| `lifecycle_demo.py` | a worked implementation of the five stages with four cases |
| `state-space.html` | the two-axis state space, self-contained |

## Run the demo

No dependencies, Python 3.8+, offline.

```bash
python lifecycle_demo.py              # four cases
python lifecycle_demo.py --case 2 -v  # one case, verbose
python lifecycle_demo.py --selftest    # prove the criteria can fail
```

Expected: `4/4 案例符合预期`, and in `--selftest`, the injected defect is caught.

## What the four cases show

1. a compliant walk through all five stages, which produces no findings
2. evidence absent while authority is in force — a legitimate state that a
   single-status system reports as either "approved" or "unauthorised", both wrong
3. verified evidence with revoked authority — the dangerous direction, where good
   evidence of a past act is mistaken for present authority
4. an unreachable record — which must yield *no determination*, not a default permit

## Honest limits

The demo implements no mechanism the document recommends. It exists so that the
evidence criteria can be seen operating rather than read as prose. It has four
cases, which is enough to show the distinction and not enough to establish the
framework.

## Provenance

Individual capacity, no organisation represented. Offered as material for
discussion, not settled positions.
