

.. _chapter04:

The lifecycle
=============

Five stages, each with an entry condition and an exit condition. The stage boundaries are drawn where the *evidence required* changes, not where organisational responsibility changes.

.. list-table::
    :header-rows: 1

    * - #
      - Stage
      - Entry condition
      - Exit condition
      - What can go wrong silently
    * - **L1**
      - **Registration**
      - an operator asserts an agent exists
      - the agent has a resolvable record with a named governance owner
      - registered for inventory purposes and reported as governed
    * - **L2**
      - **Authorisation**
      - the agent is registered
      - the scope of authority it may act under is declared and bounded
      - authority asserted but not traceable to a conferral
    * - **L3**
      - **Operation**
      - the agent acts
      - each consequential act leaves evidence of what it did and on what basis
      - acts executed with evidence produced after the fact
    * - **L4**
      - **Re-evaluation**
      - new evidence, or a change to the reference the act was judged against
      - the trust state is re-derived and the previous state is superseded explicitly
      - the previous state persists because nobody re-derived it
    * - **L5**
      - **Retirement**
      - the agent stops acting
      - the record is closed and the standing is terminally withdrawn, not merely unused
      - decommissioned in practice, still "active" on record


Two design notes on the shape:

- **L4 is a stage, not an exception path.** Frameworks usually draw re-evaluation as an arrow returning to L2. Making it a stage with its own entry and exit conditions forces the question "what evidence triggers re-derivation, and who is accountable when it is not triggered".
- **L5 exists in the framework because it is the stage most often missing and most often consequential.** An agent that has stopped acting but remains on record as active is a standing that can still be relied upon by someone who was not there.

---
