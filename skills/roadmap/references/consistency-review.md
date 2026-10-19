# Consistency review brief (whole chain ↔ roadmap)

Give this to a fresh reviewer sub-agent with the paths of the project's `concept.md`, `requirements.md`, `resource-math.md`, `contracts.md`, `data.md`, `architecture.md`, `mechanics.md`, `resilience.md`, `decisions.md`, `roadmap.md` and the `roadmap/epics/` folder. The reviewer reads them fully, edits nothing, reports in the developer's language, and returns at most 25 rows `type | where (PH-/G-/TK-/EP- id or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. PROOF_WORK_MISSING: a spike, measurement, drill, validation or `→ roadmap` item from an earlier document (including assumptions with a named validation, failing limits and accepted residual risks) that no task or epic plans, or that is scheduled after the work that depends on its answer.
2. RISK_LAST: the plan builds expensive things before the cheap proofs that could change them; a gate that does not actually stop or change anything; criteria that cannot be measured or do not match the requirements and limits.
3. UNCOVERED: a Must requirement or v1-scope capability with no task or epic, or served only on paper (the task's acceptance does not test it).
4. ESTIMATE_BROKEN: ranges that are too narrow for the uncertainty, estimates that contradict earlier hour figures (resource-math builder hours, mechanics/resilience effort), tasks outside 4-16 hours, epics hiding unknown scope, a missing external wait.
5. DEPENDENCY_WRONG: a missing or impossible dependency, a task that needs something produced later, a critical path hidden by parallel assumptions that one developer cannot meet.
6. CAPACITY_UNREAL: hours per week or deadline that contradict the requirements, constraints or what the developer stated; a schedule that quietly assumes full-time work; no slack for the drills and re-planning.
7. ACCEPTANCE_WEAK: a task whose acceptance cannot fail or cannot be checked by someone else; a gate rule that gives no decision.
8. CONTRADICTION: the roadmap contradicts a requirement, architecture decision, mechanics model, resilience gate (e.g. a pilot before the drill that must precede strangers) or a non-superseded decision.
9. STALE: tasks based on superseded decisions or old versions of earlier documents.
10. CUTS_DISHONEST: cuts that remove a Must requirement, hide cost elsewhere, or are not tied to hours saved.
11. TASK_BOUNDARY: two tasks (or epics) that overlap or own the same work; a task whose file does not say what to do in enough detail to start, whose boundaries (in / out) are vague, or that cannot be done or checked alone; a split by layers of effort (design / code / test) instead of logical seams; a task file that disagrees with its table row (epic, phase, hours, dependencies, acceptance). Also give the paths of `roadmap/epics/`.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
