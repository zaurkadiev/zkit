# Requirements template

Keep the document to roughly 2,000-3,500 words. Tables over prose. Use these sections in this order; drop one only if irrelevant, and say so in one line. No diagrams, data models, API shapes or technology choices (see the boundary in SKILL.md).

```markdown
# <Name> — Requirements

> **Links:** [concept](concept.md) · [decisions](decisions.md)
> **Status:** draft / agreed (agreed only when the clarity gate passes, see SKILL.md step 3) · **Date:** <date> · **Based on:** [concept.md](concept.md) (<concept's own date>), verdict: <verdict>
> **Counts:** <n> FR · <n> NFR · <n> C — Must <n> / Should <n> / Could <n> / Won't (v1) <n> (the checker compares these with the tables, so keep the `<n> FR`, `Must <n>` form)

## 1. Summary
What the system is in one sentence, what v1 covers, the main open item. ≤5 sentences.

## 2. Preconditions and scope
- **Preconditions** (only if the verdict is Validate first or similar): gates from the concept that must pass before these requirements are acted on, and the validations that assumed targets point to (`assumed → P-n`). One item each: `- **P-n.** <gate or validation>. Criterion: <what passes>.`; a dropped one stays as `- **P-n (withdrawn).** …`.
- **In v1:** capabilities covered.
- **Out of v1 (Won't):** deliberately postponed or excluded, one line each with a reason.

## 3. Actors
Who or what interacts with the system from outside (user roles, admins, external systems), one line each. Not a user-persona essay — the concept has that.

## 4. Functional requirements
| ID | Requirement | Priority | Acceptance criterion | Source | Basis |
|---|---|---|---|---|---|
| FR-1 | The system shall <observable behaviour>. | Must | <how to check, with a number or evidence> | concept §9, D-3 | known / derived / assumed |

Group by capability with a subheading when there are more than ~12.

## 5. Non-functional requirements
| ID | Category | Requirement (with number) | Acceptance / how measured | Source | Basis |
|---|---|---|---|---|---|
| NFR-1 | Performance | <measurable statement> | <measurement method> | | assumed → P-1 / confirmed by developer |

Categories walked: performance, availability/reliability, security and privacy, cost, scalability, operability, usability, compliance/legal, data retention, portability. List the skipped ones in one line with the reason.

## 6. Constraints
Imposed from outside the requirements work (budget, team, deadline, mandated or banned technology, legal). Technology names appear only here, each with its source.
| ID | Constraint | Source |
|---|---|---|

## 7. Load profile and assumptions
Users, volume, growth, peaks and data sizes, in order-of-magnitude terms, each with its basis and how it will be validated. Design sizes against these.

## 8. Interview log
| Question | Answer | My recommendation | Status (answered / assumed / open) |
|---|---|---|---|

## 9. Traceability
| Concept item (success criterion / capability / risk) | Covered by |
|---|---|
List concept items with no requirement as **uncovered** and explain (deliberately out, or a gap). List requirements with no concept source as **orphans** and justify or cut them.

## 10. Conflicts, risks and open questions
Ranked. Conflicting requirements and trade-offs awaiting a decision, assumed targets that could break the design if wrong, issues found in the concept. For each: why it matters and the cheapest way to resolve it. One numbered item each: `1. **Q-n.** <title>. …` (Latin Q; later documents cite them as `Q-n`).

## 11. Deferred to design
One line per implementation-level idea that came up, tagged with the target stage (`→ architecture`, `→ contracts`).

## 12. Consistency check
Date; result of `scripts/check_requirements.py` (errors / warnings left and why); verdict of the independent reviewer against the concept; what was fixed; what stays open and where it is recorded.

## Sources
Numbered URLs; mark findings from delegated research with their confidence.
```
