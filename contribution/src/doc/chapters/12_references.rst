

.. _chapter12:

Bibliography
============

All links were fetched on 2026-11-07. Where a standard is named in the body but its
full text is not publicly available, the entry says so rather than linking to a
secondary page as though it were the standard.

**Primary, publicly available**

- ITU-T FG-TIDA Terms of Reference, Annex A (A.2.1, A.2.2, A.2.5, A.2.7):
  `itu.int/en/ITU-T/focusgroups/tida/Pages/ToR.aspx <https://www.itu.int/en/ITU-T/focusgroups/tida/Pages/ToR.aspx>`_
- REGULATION (EU) 2017/745 (Medical Device Regulation), consolidated text:
  `eur-lex.europa.eu/eli/reg/2017/745 <https://eur-lex.europa.eu/eli/reg/2017/745>`_
  — Annex IX (conformity assessment) and Article 83 (post-market surveillance) are the
  provisions the lifecycle claim relies on.
- **ISO 13485:2016** *Medical devices — Quality management systems — Requirements for
  regulatory purposes* and **ISO 14971:2019** *Medical devices — Application of risk
  management to medical devices*: **named, not linked.** ISO returns HTTP 403 to
  automated requests, so a link here could not be verified from this document, and an
  unverifiable link in a contribution is worse than a name. Both are paywalled in any
  case; this document quotes neither.

**This contribution's own material**

- The executable demonstration of the five stages described in Clause 3, with four
  worked cases and a self-test that injects a defect and requires it to be caught:
  `github.com/zhaoxinghua09-cell/a22-trust-lifecycle <https://github.com/zhaoxinghua09-cell/a22-trust-lifecycle>`_
- The two-axis requirements this lifecycle reuses, stated separately:
  `github.com/zhaoxinghua09-cell/d4-evidence-authorization <https://github.com/zhaoxinghua09-cell/d4-evidence-authorization>`_

**Named in the body, not linked**

The body refers to NIST AI RMF and to ISO/IEC 42001 as alignment references. They are
named as context and no claim in this document depends on their text, so they are not
linked here. If a later revision relies on them, they must be added with a verified
citation at that point rather than carried as names.

**A note on what remains unverified.** The device lifecycle is referred to here as a template
and no longer as an isomorphism. Even so, the claim that the five stages correspond to a
regulated sequence was checked against the consolidated EU MDR text and against the catalogue
scope statements of ISO 13485 and ISO 14971, **not against the ISO standards themselves**, which
are not publicly readable and which reject automated retrieval. A reviewer with access to those
standards should treat the correspondence table as **partially verified**; the three gaps stated
in Clause 3 are derived from the documents that were readable, not from the ISO text.
