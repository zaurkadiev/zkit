# Concept template

Keep the whole document to roughly 1,500-2,500 words: conceptual level, no schemas, exact product configs or precise estimates (those belong to later stages; see the concept-vs-design boundary in SKILL.md). Use these sections in this order. Drop a section only if it is truly irrelevant, and say so in one line rather than leaving it silently out.

```markdown
# <Name> — Concept

> **Status:** draft · **Date:** <date> · **Verdict:** <Build / Build smaller / Validate first / Buy or reuse / Don't build> — <one-sentence reason>

> **Next:** [requirements](../requirements/NN-<slug>.md) · [decisions](../decisions/index.md) · [index](../index.md)

## 1. Summary
What the system is (in a sentence or two), for whom, the recommended approach, and the verdict, in ≤5 sentences.

## 2. Intent & Questions
Developer's intent and success criteria in their own terms. Then a table: Question | Answer | Status (answered / assumed / open). Include every question asked during the interview and any that surfaced later.

## 3. Problem
Problem statement, who has it, current workarounds, pain/frequency. Evidence tags: [known] [assumed] [unknown].

## 4. Users
Primary / secondary / explicitly not targeted. Jobs-to-be-done for the primary user.

## 5. Landscape
Table: Alternative | What it does | Strengths | Weaknesses | Source. Include DIY/status quo and dead or failed attempts. Then: where is the gap, if any?

## 6. Evaluation
- Strengths: what is genuinely good about the idea, with evidence
- Weaknesses / case against building it
- Difficulty: hardest parts to build and to run, for this developer
- Downsides and costs of the idea itself
- Pre-mortem: top 3 failure reasons
- Verdict and what evidence would change it

## 7. Scope
First version: in / out. Core capabilities, what matters most (scale, privacy, cost, speed) in order-of-magnitude terms only; precise targets are set in `requirements`. Constraints.

## 8. Approaches
For each option (2-4): description, patterns/styles used and why, pros, cons/costs, wrong-when.
Comparison table on the criteria that matter here. **Recommended approach** + rationale, and the conditions under which you'd switch to another option.

## 9. System concept (the system we would build)
Written as if the system exists. This section must stand alone:
- **What it is:** one paragraph — purpose and essence.
- **Main scenario:** a short walk-through of how a primary user uses it, start to finish.
- **Capabilities:** the core things it does (first version vs. later).
- **Structure:** the few main parts in plain words and what each is responsible for; the architectural style chosen.
- **How it works:** in a few sentences, what flows through the system from input to result; the main things it deals with (not a data model).
- **Boundaries:** external systems and dependencies; what it deliberately does NOT do.
- **What matters most:** the two or three qualities that shape the system (e.g. reliability over speed), without numbers or SLOs.
No diagrams (C4 and data models come in later stages), no file layouts, no APIs. Describe the picture in plain words.

## 10. Risks and open questions
Ranked list. For each: why it matters, how to resolve it cheaply (experiment, interview, spike).

## 11. Next steps (hand-off to `requirements`)
The 3-5 cheapest actions to validate or kill the idea, then hand-off to planning if the verdict is positive.

## 12. Deferred to design
One line per implementation-level idea that came up but belongs to later stages, tagged with the target stage (`→ requirements`, `→ high-level-design`, `→ design-details`). Keeps the concept clean without losing the idea.

## Sources
Numbered URLs referenced above. Mark findings that came from delegated research sub-agents and note their confidence.
```
