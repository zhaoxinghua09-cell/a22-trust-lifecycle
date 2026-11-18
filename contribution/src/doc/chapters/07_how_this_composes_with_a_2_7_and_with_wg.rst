

.. _chapter07:

How this composes with A.2.7 and with WG2
=========================================

This note deliberately does not propose a control-plane architecture (A.2.7), a per-action verdict model (WG2), or a record format. The division of labour the note assumes:

.. list-table::
    :header-rows: 1

    * - Question
      - Where it belongs
    * - What are the lifecycle stages and the evidence criteria at each?
      - **this note (A.2.2)**
    * - How is trust state established, distributed and changed across an estate?
      - A.2.7 (control plane), as proposed by its own proposer
    * - What decision does an enforcement point return for one action, and what does it record?
      - WG2
    * - What must a record contain for a party who was not present?
      - the record-requirements work (themes#1)


Two interfaces this note asks for, stated as **requirements rather than as architecture**, so that the owner of each can accept, rewrite or reject them:

#. **Each decision records the version or recency of the record it consulted.** Without it, a later reader cannot distinguish a decision taken against current standing from one taken against superseded standing. This is indifferent to mechanism: where changes are pushed it is how *delivered* is told from *in force*; where standing is consulted at the act it is how a regulator establishes that no act was decided on superseded standing.
#. **"No record found" and "record found, standing revoked" are distinguishable outcomes.** If both present as the same denial, nothing downstream can tell a refused act from a broken check.

Both requirements are consequences of the lifecycle framework's own claim: that trust is time-bound. A framework that says trust is time-bound, and does not require the time to be recorded, has not said anything a relying party can use.

---
