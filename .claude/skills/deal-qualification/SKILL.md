---
name: deal-qualification
description: Assess honestly whether a deal is real, what stage it is actually at, what is blocking it, and what the next action should be. Use for a single deal or a full pipeline review.
---

# Deal qualification

## Run it
1. Load `accounts/<slug>/`, `pipeline/pipeline.md`, `playbooks/qualification.md`.
2. Work the qualification table. For each dimension: **what we know**, **how we know it**, and
   **what we are assuming**. Assumptions are gaps, and gaps are risks.
3. Delegate to **`ofs-deal-strategist`** for the assessment.

## Produce
1. **Actual stage**, with the evidence — not the stage we would like it to be.
2. **Decision map**, naming who we have not met.
3. **Gaps** — every dimension we cannot answer.
4. **Risks**, ranked, each with a mitigation and an owner.
5. **Recommendation** — advance, hold, or disqualify.
6. **Next action** — one person, one verb, one date.

## Persist
Update `pipeline/pipeline.md` and `accounts/<slug>/engagement.md`; route questions for Andre to
`memory/open-questions.md`.

## Rules
- **Evidence over optimism.** Long-standing is not the same as late-stage.
- **Never invent** a value, probability or close date. Those come from Andre; write "unknown".
- Always ask **"what happens if they do nothing?"**
- **Recommend disqualification when that is the truth.** Cheap early beats expensive late.
