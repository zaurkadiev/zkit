# Architecture template

Aim for roughly 3,000-4,500 words. Tables over prose. Use these sections in this order; drop one only if irrelevant and say so in one line. Products only for expensive-to-reverse choices (section 3 and the technology table). No algorithms, field-level schemas, machine-readable internal contracts, libraries — those are `mechanics`.

````markdown
# <Name> — Architecture

> **Links:** [concept](concept.md) · [requirements](requirements.md) · [resource-math](resource-math.md) · [contracts](contracts.md) · [data](data.md) · [decisions](decisions.md)
> **Status:** draft / agreed (agreed only when the clarity gate passes, see SKILL.md step 7) · **Date:** <date> · **Based on:** requirements.md (<date>), resource-math.md (<date>), contracts.md (<date>), data.md (<date>)
> **Counts:** <n> B · <n> I · <n> S · <n> decisions (the checker compares these with the tables, so keep the `<n> B`, `<n> I`, `<n> S` form)

## 1. Summary
The architecture in ≤5 sentences: the chosen style, the 4-8 parts in one line, the decision that shapes everything else, the biggest remaining risk.

## 2. Drivers
What the structure must serve: the architecturally significant requirements, binding resource-math limits, boundaries and entities that need a guardian.
| Driver | Source | Why it shapes the structure |
|---|---|---|
| e.g. External actions only with approval | NFR-9, X-3 | Needs one enforcement point that no agent can bypass |

Quality ranking (top 3-5, in order; the order resolves trade-offs later) and the constraints and load figures the design is sized against.

## 3. Key decisions
One row per fork that is expensive to reverse; the full record is `D-<n>` in decisions.md (options, evidence, why, date).
| Decision | Chosen | Main alternative | Why (one line) | Serves |
|---|---|---|---|---|
| D-<n> | … | … | … | NFR-…, L-… |

Technology under the parts (only choices that are expensive to reverse):
| Concern | Choice | Decision | Price check (resource-math) |
|---|---|---|---|
| e.g. database engine | … | D-<n> | fits L-4 at 120 EUR/month [R-n](research/R-n-slug.md) |

## 4. Parts
| ID | Part | Responsibility (one sentence) | Owns (E-n, in-process state) | Faces (X-n) | Limits (L-n) | Build / adopt / buy | Serves |
|---|---|---|---|---|---|---|---|
| B-1 | … | … | E-1, E-4 | X-1 | L-2 | build | FR-…, NFR-… |

Rules: one reason to change per part; every entity E-n has exactly one owner; every boundary X-n is faced by some part; no part is named after a technology.

## 5. C4 diagrams
Mermaid flowcharts in the style of C4. The checker reads the heading to tell the levels apart; keep the words `Level 1`, `Level 2`, `Level 3`.

### Level 1 — System context
People and external systems around the system; external systems carry the contract ids (`X-1`).

### Level 2 — Containers
Parts as nodes (`B1["B-1 Name"]`), databases/queues/other infrastructure as extra nodes, arrows labelled with the interface id (`I-1`), external systems with their `X-n`.

### Level 3 — Components of B-n
For the one or two parts whose inner structure carries a requirement (isolation, approval, money accounting). Say in one line why this part.

## 6. Interfaces
| ID | From → to | What passes and why | Style (sync / async / event) | Delivery semantics | Serves |
|---|---|---|---|---|---|
| I-1 | B-… → B-… | … | async | idempotent by action key | FR-… |

Operations in words (verb + object, inputs and outputs named in words) where the interface is not obvious. Externally visible operations are in `contracts/` — cite `X-n`, don't repeat. Exact formats come in `mechanics`.

## 7. Key scenarios
3-6 walk-throughs, step by step through parts and interfaces. At least one is the main flow and two are failure or hard-requirement flows (restart in the middle of an external action, quota exhausted, a hostile input, a part down, a deletion request reaching every copy).
| ID | Scenario | Steps (B-/I- ids) | Outcome against requirements | Gaps found |
|---|---|---|---|---|
| S-1 | … | B-1 →I-1→ B-2 … | NFR-12 holds because … | none / fixed in B-… |

## 8. Cross-cutting concerns
Security and secrets, reliability and recovery, observability, cost control, data isolation, deployment shape — one short paragraph each, pointing to the parts and requirements that carry it; the depth comes in `resilience`. Skipped ones listed with the reason.

## 9. Traceability
| Requirement | Covered by |
|---|---|
| FR-1 | B-…, I-…, D-… |
Every Must requirement appears, grouped by theme with ranges (`FR-13…FR-15`) rather than one row each. Requirements with no covering part are listed as **uncovered** with the reason; parts that serve no requirement as **orphans**, justified or cut.

## 10. Reconciliation with earlier steps
What the architecture changed or found in earlier documents: contracts revised, resource-math assumptions or limits adjusted, data entities moved, requirements questioned — each with the decision or the pending question.

## 11. Risks, assumptions and open questions
Ranked. Architectural assumptions that carry a Must requirement each get the cheapest way to validate (a spike or measurement; it becomes a task at the roadmap stage), forks not yet decided.

## 12. Deferred
One line per detail that came up, tagged with the target stage (`→ mechanics: …`, `→ resilience: …`, `→ roadmap: …`).

## 13. Consistency check
Date; `check_architecture.py` result (errors / warnings left and why); verdict of the independent reviewer; what was fixed; what stays open.

## Sources
Numbered URLs; delegated findings link to `[R-n]` reports with their confidence.
````
