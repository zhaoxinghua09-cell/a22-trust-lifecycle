

.. _chapter02:

What A.2.2 asks for, and what this note answers
===============================================

The Terms of Reference describe A.2.2 as:


.. note::

    *"A study and specification of trust as a dynamic and time-bound property, covering initial trust establishment, continuous trust evaluation, trust degradation and revocation, including the conditions and evidence criteria required at each lifecycle stage for both agent-to-agent and human-to-agent interaction contexts."*


That description contains three requirements, and the third is the one most easily left implicit:

.. list-table::
    :header-rows: 1

    * - A.2.2 requirement
      - What this note provides
    * - trust as a **dynamic and time-bound** property
      - §3: a lifecycle with named stages, each with an entry and an exit condition
    * - **initial establishment, continuous evaluation, degradation and revocation**
      - §3 and §4: the mechanisms by which trust is gained, re-evaluated, weakened and withdrawn
    * - **conditions and evidence criteria at each lifecycle stage**
      - §4: an explicit evidence vocabulary applied per stage, separated into two axes that fail independently


The claim this note makes is narrow: **a lifecycle framework is only testable if each stage names what evidence would satisfy it and what would contradict it.** A framework that lists stages without evidence criteria is a diagram, and a framework that names evidence without distinguishing its failure modes cannot tell "no evidence" from "evidence found wrong". The two are different findings with different responses, and the second is the one usually lost.

---
