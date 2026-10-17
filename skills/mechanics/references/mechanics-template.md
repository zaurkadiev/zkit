# Mechanics template

Aim for roughly 2,500-4,500 words plus the executable models. Tables over prose. Sections in this order; drop one only if irrelevant and say so in one line. No production code, no failure-handling policy (resilience), no tasks (roadmap).

````markdown
# <Name> — Mechanics

> **Links:** [concept](concept.md) · [requirements](requirements.md) · [resource-math](resource-math.md) · [contracts](contracts.md) · [data](data.md) · [architecture](architecture.md) · [decisions](decisions.md)
> **Status:** draft / agreed (agreed only when the clarity gate passes, SKILL.md step 6) · **Date:** <date> · **Based on:** requirements.md (<date>), resource-math.md (<date>), contracts.md (<date>), architecture.md (<date>)
> **Counts:** <n> MC   (the checker compares this with the mechanism table)

## 1. Summary
The mechanics in ≤5 sentences: how many mechanisms, which are high risk, what the executable models found, the biggest remaining risk.

## 2. Mechanisms
| ID | Part | Mechanism | Kind | Serves | Verified by | Risk |
|---|---|---|---|---|---|---|
| MC-1 | B-3 | Quota reservation before a model call | algorithm | NFR-1, L-7 | mechanics/model_quota.py | H |
| MC-2 | B-3 | Task lifecycle | state machine | FR-8, NFR-12 | review | M |

`Kind`: state machine / algorithm / protocol / concurrency / timing / memory / format. `Verified by`: an executable model path, `review` (the independent reviewer) or a test idea for the roadmap. `Risk`: H (a violated invariant breaks money, isolation, exactly-once or a deadline) / M / L.

### MC-1 Quota reservation (B-3)
Purpose and the requirement it serves; the rule in pseudocode or formulas (short); **invariants** (`reserved + spent ≤ quota at every instant`); the interleavings and failures that threaten it; limits from resource-math it must respect; what it needs from interfaces.

### MC-2 Task lifecycle (B-3)
| State | Event | Guard | Next state | Effects |
|---|---|---|---|---|
| queued (initial) | start | quota reserved | running | emit action key |
| running | step done | — | running | persist step |
| running | timeout | no progress for T | failed | release reserve |
| running | crash / restart | — | queued | resume from last persisted step |
| running | cancel | — | cancelled | release reserve |
| failed (final) | — | — | — | — |
| cancelled (final) | — | — | — | — |

First row is the initial state; terminal states are marked `(final)`; include timeout, crash/restart, duplicate delivery and cancel events where they apply.

## 3. Trivial parts
One line per part with no mechanism of its own, saying why: `B-1: a form over the owner API, no state.`

## 4. Internal contracts
Interfaces that cross a process or trust boundary or carry a requirement, specified in `contracts/` with boundary id `I-n` and `x-direction: internal` (skeletons in the `contracts` skill):
| Interface | Spec | What the format must guarantee |
|---|---|---|
| I-17 | contracts/i-17-signed-context.yaml | signed, expiring, carries account, organization, role, plan status |

## 5. Timing, memory and concurrency rules
Cross-mechanism rules that no single section owns: lock order, who owns which timeout, priorities and interrupt levels, buffer and pool sizes against the resource-math limits, clock assumptions. Each rule names its owner and the limit it serves.

## 6. Executable checks
For each model in `mechanics/`: what it enumerates (actors, interleavings, crash points), the invariants it asserts, what the `broken` variant switches off, and what it found (including violations fixed in the design).

## 7. Reconciliation with earlier steps
What the mechanics changed or found in earlier documents (architecture parts or interfaces moved, contracts revised, resource-math assumptions adjusted, requirements questioned) with the decision or the pending question.

## 8. Risks, assumptions and open questions
Ranked; every assumed mechanism has the cheapest way to validate it (a model, a spike, a measurement; it becomes a roadmap task).

## 9. Deferred
One line per detail that came up, tagged with the target stage (`→ resilience: …`, `→ roadmap: spike …`).

## 10. Consistency check
Date; `check_mechanics.py` result (errors / warnings left and why, models run and their outcome); verdict of the independent reviewer; what was fixed; what stays open.

## Sources
Numbered URLs; delegated findings link to `[R-n]` reports with their confidence.
````
