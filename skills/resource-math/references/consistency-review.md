# Consistency review brief (requirements ↔ resource math)

Give this to a fresh reviewer sub-agent with the paths of `concept.md`, `requirements.md`, `decisions.md`, `resource-math.md` and `resource_model.py` of the project. The reviewer reads all fully, may run `python3 resource_model.py`-style checks only by reading the code (no edits), reports in the developer's language, edits nothing, and returns at most 25 rows `type | where (A-/L-/NFR- id or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. UNTESTED: a numeric requirement, budget or constraint (cost, latency, throughput, memory, quota, battery, frame time) that the math could test but no limit does, and is not listed as not resource-bound.
2. FORMULA_WRONG: a formula that does not compute what its label claims (units mixed, a missing factor, a per-unit figure used as a total, double counting, a resource that scales with workload treated as constant).
3. OPTIMISTIC: an expected value that is really a best case; a range that is too narrow for an assumed input; a source that does not support the number (a price from another product or tier, a benchmark from another workload); a worst case that is not worst.
4. WORKLOAD_GAP: the workload model leaves out a unit, a burst, a retry or a background load that a requirement or the concept implies, so every result is understated.
5. BINDING_MISSED: a resource that can obviously bind this kind of system but is absent from section 3 without a reason (quota, storage growth, egress, human time, startup time).
6. VERDICT_MISMATCH: the summary, verdict line or consequences contradict the generated results (says "fits" where a limit fails in expected or worst; hides a failing worst case).
7. CONTRADICTION: the math contradicts a requirement, constraint, concept boundary or non-superseded decision, or relies on a superseded one.
8. DESIGN_LEAK: a decision smuggled in as an assumption (a named provider or product as a choice, a part structure, a data format); products only as sources of numbers.
9. STALE: assumptions or limits that disagree with the current requirements text (a changed target, a renumbered requirement).

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
