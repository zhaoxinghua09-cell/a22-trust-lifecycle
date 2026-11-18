

.. _chapter13:

Annex B. A case set for composition rules, folded in rather than filed separately
=================================================================================

The lifecycle in section 3 composes stages; composition is where rules interact, and interactions are
where a rule set can be satisfiable in each clause and contradictory in combination. A case set was
written for that question and is carried here as an annex rather than as a separate contribution, because
its subject is the composition rules this document already proposes.

The set contains eight rules, twenty-three cases and ten mutants. Each case names the rule whose
mis-reading it is designed to catch, so a green result is evidence that the harness is not lying rather
than evidence that the implementation is correct. Three exit codes distinguish pass, contradiction and
malformed input, because collapsing contradiction into malformed input hides the case the set exists to find.

Re-run on 2026-11-17: ten of ten mutants killed, zero cases without a named mutant, exit code 0. The
command and its output are reproducible; the result is a self-test of the case set, not a conformance
result for any implementation.
