

.. _chapter05:

Evidence criteria: two axes that must not be merged
===================================================

.. note::

    **Scope note.** The value sets below are those of the companion two-axis requirements
    (`d4-evidence-authorization <https://github.com/zhaoxinghua09-cell/d4-evidence-authorization>`_),
    restated here for readability. This document does **not** re-specify them: where the two
    differ, the companion document governs and this one is defective.


This is the part of the note that is offered as a substantive contribution rather than as a scaffold. At every lifecycle stage, the evidence a relying party needs answers two **different** questions, and a framework that reports one status for both will lose one of the failure modes.


4.1 Axis E — evidence state
---------------------------


.. list-table::
    :header-rows: 1

    * - Value
      - Meaning
      - The mistake it is read as
    * - ``absent``
      - no evidence was produced
      - read as "not wrong"
    * - ``declared``
      - evidence is asserted to exist but no artefact is reachable
      - read as ``present-unverified``
    * - ``present-unverified``
      - an artefact exists but has not been checked
      - read as ``verified``
    * - ``verified``
      - checked against a stated method, with the method named
      - read as "the content is true"
    * - ``contradicted``
      - evidence exists and conflicts with the claim
      - read as ``absent``


*Staleness is not a value of this axis.* It is computed from the time the determination
was made and the validity bound declared for it, and it is reported as a property of the
determination. Keeping it out of the value set avoids the two representations drifting
apart, which is the defect that review caught in an earlier draft.


4.2 Axis A — validity of the authority to act
---------------------------------------------


.. list-table::
    :header-rows: 1

    * - Value
      - Meaning
    * - ``in-force``
      - the authority to act exists and is current
    * - ``suspended``
      - temporarily held
    * - ``revoked``
      - withdrawn
    * - ``expired``
      - lapsed by time


**Unavailability is not a value of either axis.** A record that cannot be reached yields no
determination at all; the pair is ``unavailable`` and carries no axis value. This follows the
evidence-quality and authorization-validity requirements stated separately, which the
demonstration in Clause 10 implements.


4.3 Why the axes must not be collapsed
--------------------------------------


Three states are legitimate and each is destroyed by a single scalar:

- **``evidence = absent`` with ``authority = in-force``.** The act is permitted, and there is no way to show it was right. Reporting this as "authorisation failed" is wrong; reporting it as "approved" hides that nothing was checked.
- **``evidence = verified`` with ``authority = revoked``.** Good evidence of a *past* act does not confer *present* authority. This is the case that a per-action check must catch and a lifecycle record must make visible.
- **``evidence = contradicted``.** This is not a stronger form of ``absent``. It is a different finding, it calls for a different response, and it is the one lost most often — because a schema with one status field has no place to put it, so it is recorded as "no evidence", which reads as a gap rather than a conflict.

**``unknown`` deserves its own line.** If the record cannot be reached at the moment of decision, the correct output is that no finding is available — not that the previous state persists, and not that the check passed. An enforcement point that cannot distinguish "could not check" from "checked and fine" has no way to report the difference, and neither does anyone reading its log afterwards.


4.4 Criteria per stage
----------------------


Applying the two axes at each lifecycle stage yields the table this note proposes as the A.2.2 answer:

.. list-table::
    :header-rows: 1

    * - Stage
      - Evidence criterion (Axis E)
      - Authority criterion (Axis A)
    * - **L1 Registration**
      - the record exists and is resolvable: ``verified``; a claimed registration that cannot be resolved: ``present-unverified``
      - the governance owner is named; a record with no owner yields no determination for any downstream question
    * - **L2 Authorisation**
      - the conferral is evidenced, not asserted: ``verified`` vs ``present-unverified``
      - scope declared and bounded; an unbounded scope is not ``in-force`` in any usable sense
    * - **L3 Operation**
      - per act: what was done, on what inputs, on what basis; absence of per-act evidence is ``absent``, not "no incident"
      - the authority at the moment of the act, which may differ from the authority at the moment of queueing
    * - **L4 Re-evaluation**
      - the triggering evidence is recorded, and the re-derived state supersedes the previous one explicitly
      - the pre-change and post-change states are both on record, with which one governed at which time
    * - **L5 Retirement**
      - the closure is evidenced, distinguishing "stopped acting" from "removed from record"
      - terminal withdrawal, distinguishable from ``suspended``


---
