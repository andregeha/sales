---
name: rfp-response
description: Answer an RFP, tender, vendor due-diligence questionnaire or security questionnaire about Gaia. Use whenever a client sends a structured list of requirements or questions to be answered in writing.
---

# RFP / questionnaire response

## Run it
1. **Parse** the document into a numbered requirement list. Do not summarize it away — every line
   gets an answer or an explicit "not applicable".
2. Delegate to **`ofs-solution-engineer`** for the verdict on each requirement.
3. Delegate to **`ofs-writer`** for the prose once the verdicts are settled.

## The answer table
| # | Requirement | Verdict | Answer | Source | Owner |

Verdicts: **Yes** · **Yes, roadmap** (with the timeline, never implied as available) ·
**Partial** (say exactly what is and is not covered) · **Configuration/project** (possible, but it
is work) · **No** · **Unconfirmed** (goes to R&D via `memory/open-questions.md`).

## Writing the answers
- Answer the question that was asked, first sentence. Then how. Then evidence.
- Ground every claim in `knowledge/`. No source, no claim.
- **Never over-claim to win a box-tick.** A "yes" we cannot deliver becomes a delivery failure and
  a lost reference. "Partial" with a clear explanation wins more than a bare "yes".

## Security questionnaires specifically
Answer from the **posture** in `knowledge/product/gaia-new.md` and the current product's controls —
Windows/SQL authentication, rights by operator and group, client-name encryption, full audit
including login attempts; and for the New Gaia: BFF (tokens never reach the browser), two-factor
via a standard identity provider, HTTPS end-to-end, deny-by-default authorization decided in the
database, field-level masking, audit on every request and denial, retention and purge.
⚠ **Never disclose specific gaps, findings, versions of internal components, server names,
endpoints or credentials.** Hardening is described as a planned workstream, positively.

## Before it goes out
- Every **Unconfirmed** resolved or explicitly flagged to Andre.
- Every commercial item — price, dates, scope, SLAs, contractual terms — flagged
  `[COMMERCIAL — ANDRE TO CONFIRM]`.
- No internal references anywhere in the document.
- **Andre approves before anything is sent.**
