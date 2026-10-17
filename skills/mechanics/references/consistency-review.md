# Consistency review brief (earlier steps ↔ mechanics)

Give this to a fresh reviewer sub-agent with the paths of the project's `concept.md`, `requirements.md`, `resource-math.md` (with `resource_model.py`), `contracts.md` and `contracts/`, `data.md`, `architecture.md`, `decisions.md`, `mechanics.md` and the `mechanics/` folder. The reviewer reads them fully, edits nothing, reports in the developer's language, and returns at most 25 rows `type | where (MC-/B-/I- id or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. MISSING_MECHANISM: a requirement, scenario or architecture risk that depends on exact behaviour (once, in order, within a deadline, under a lock, bounded memory) with no mechanism; a part wrongly declared trivial.
2. INVARIANT_WEAK: an invariant that does not imply the requirement it claims to serve, or that holds only in the absence of concurrency, crash, duplicate delivery or late messages.
3. RACE_OR_REPLAY: an interleaving, crash point or duplicate/late delivery the mechanism or its model does not cover and that breaks an invariant (check-then-act without a lock, a retry with a new key, a restart that repeats an external effect, an ack before persist).
4. STATE_MACHINE: undeclared, unreachable or dead-end states, a missing timeout/crash/cancel/duplicate transition, an effect that is not undone on a failure path, a state that two actors write.
5. MODEL_HOLLOW: an executable model that checks a weaker thing than the mechanism (a single order, no crash points, invariants asserted on a copy of the logic that diverges from the described algorithm), or whose `broken` variant does not switch off the real protection.
6. NUMBERS_BROKEN: a timeout, rate, buffer size, pool size or retry budget that contradicts resource-math limits, contract quotas or data volumes; arithmetic that does not add up.
7. FORMAT_GAP: an internal interface format missing for something that crosses a trust or process boundary, ambiguous (units, time, ids, ordering), or inconsistent with the architecture's delivery semantics or the contracts' error model.
8. CONTRADICTION: the mechanics contradict a requirement, constraint, contract, architecture decision or non-superseded decision, or rely on a superseded one.
9. DESIGN_LEAK: production code, failure-handling policy (resilience), tasks or estimates (roadmap), or changes to the architecture that were not recorded as a decision.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
