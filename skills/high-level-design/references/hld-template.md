# High-level design template

Aim for roughly 3,000-4,500 words. Tables over prose. Use these sections in this order; drop one only if irrelevant and say so in one line. Name products only where the choice *is* the decision (see the boundary in SKILL.md). No data schemas, field-level API shapes, languages, databases, brokers, versions — those are `design-details`. No C4 levels — that is `final design`.

```markdown
# <Name> — High-level design

> **Links:** [concept](concept.md) · [requirements](requirements.md) · [decisions](decisions.md)
> **Status:** draft / agreed (agreed only when the clarity gate passes, see SKILL.md step 6) · **Date:** <date> · **Based on:** [requirements.md](requirements.md) (<requirements' own date>)
> **Counts:** <n> B · <n> I · <n> S · <n> decisions (the checker compares these with the tables, so keep the `<n> B`, `<n> I`, `<n> S` form)

## 1. Summary
The architecture in ≤5 sentences: the chosen style, the 4-8 parts in one line, the decision that shapes everything else, the biggest remaining risk.

## 2. Drivers
What the structure must serve. Not the whole requirements list — the architecturally significant ones.
| Driver | Requirements | Why it shapes the structure |
|---|---|---|
| e.g. External actions only with approval | NFR-9, FR-17 | Needs one enforcement point that no agent can bypass |

Quality ranking (top 3-5, in order; the order resolves trade-offs later) and the constraints and load figures the design is sized against (link to requirements §6 and §7).

## 3. Key decisions
One row per fork that is expensive to reverse; the full record is `D-<n>` in decisions.md (options, why, date).
| Decision | Chosen | Main alternative | Why (one line) | Serves |
|---|---|---|---|---|
| D-<n> | … | … | … | NFR-…, FR-… |

## 4. Parts
| ID | Part | Responsibility (one sentence) | Owns (state/data, in words) | Build / adopt / buy | Serves |
|---|---|---|---|---|---|
| B-1 | … | … | … | build | FR-…, NFR-… |

Rules: one reason to change per part; every piece of state has exactly one owner; no part is named after a technology.

## 5. Structure diagram
One Mermaid flowchart: parts as nodes (`B1["B-1 Name"]`), arrows labelled with the interface id (`I-1`). Draft level; C4 is built from it later at final design.

## 6. Interfaces and draft API
| ID | From → to | What passes and why | Style (sync / async / event) | Serves |
|---|---|---|---|---|
| I-1 | B-… → B-… | … | async | FR-… |

Draft API: per interface, the operations as verb + object, inputs and outputs named in words, delivery semantics where a requirement demands them (idempotent, at-most-once, ordered). Also the externally visible operations (owner-facing, third-party). Field-level contracts come in `design-details`.
| Interface | Operation | Inputs → outputs (in words) | Semantics | Serves |
|---|---|---|---|---|

## 7. Key scenarios
3-5 walk-throughs, step by step through parts and interfaces. At least one is the main flow and two are failure or hard-requirement flows (restart in the middle of an external action, quota exhausted, a hostile input, a part down).
| ID | Scenario | Steps (B-/I- ids) | Outcome against requirements | Gaps found |
|---|---|---|---|---|
| S-1 | … | B-1 →I-1→ B-2 … | NFR-12 holds because … | none / fixed in B-… |

## 8. Cross-cutting concerns
Security and secrets, reliability and recovery, observability, cost control, data isolation, deployment shape (managed, self-hosted, single or multi-tenant) — one short paragraph each, each pointing to the parts and requirements that carry it. Skipped ones listed with the reason.

## 9. Traceability
| Requirement | Covered by |
|---|---|
| FR-1 | B-…, I-…, D-… |
Every Must requirement appears, but group them: one row per theme with ranges (`FR-13…FR-15`) rather than one row per requirement - long one-per-line tables are what push the document past its length target. Should/Could may be grouped further. Requirements with no covering part are listed as **uncovered** with the reason (deliberately later, or a gap); parts that serve no requirement are listed as **orphans** and justified or cut.

## 10. Risks, assumptions and open questions
Ranked. Architectural assumptions that carry a Must requirement each get the cheapest way to validate (a spike or measurement; it becomes a task at the roadmap stage), issues found in the requirements or the concept, forks not yet decided.

## 11. Deferred to design-details
One line per detail that came up, tagged with the target stage (`→ design-details: …`, `→ final design: …`, `→ detailed specs: …`).

## 12. Consistency check
Date; `check_hld.py` result (errors / warnings left and why); verdict of the independent reviewer against the requirements; what was fixed; what stays open.

## Sources
Numbered URLs; delegated findings link to `[R-n]` reports with their confidence.
```
