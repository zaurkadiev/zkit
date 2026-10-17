# Consistency review brief (requirements + resource math ↔ ux)

Give this to a fresh reviewer sub-agent with the paths of `concept.md`, `requirements.md`, `resource-math.md`, `decisions.md` and `ux.md`. The reviewer reads all fully, edits nothing, reports in the developer's language, and returns at most 25 rows `type | where (U-/J- id or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. MISSING_JOURNEY: a person-actor, scenario or Must requirement with no journey; a first-run, recovery, cancel or undo path that the requirements imply and nothing covers.
2. MISSING_STATE: a surface with no empty, error, unavailable or denied state where one can occur; an error that does not say what the person can do next; a destructive action without the confirmation rule.
3. BUDGET_WRONG: a feedback budget with no number, one that disagrees with resource-math limits or with a usability NFR, one the described journey cannot meet (a result "instantly" that depends on a slow provider).
4. SURFACE_MISMATCH: a surface that serves no journey; a journey that needs a platform or input device the surface list lacks; one task split across surfaces with no reason.
5. ACCESSIBILITY_LANGUAGE: an accessibility, language or platform requirement not reflected in the surfaces or cross-cutting section.
6. CONTRADICTION: the ux document contradicts a requirement, constraint, concept boundary or non-superseded decision.
7. DESIGN_LEAK: framework or product choice without a requirement or decision, colours, fonts, pixel sizes, payload fields or operation specs that belong to contracts or to visual design.
8. HANDOFF_GAP: an operation a surface needs from the system that is not handed to contracts as a `→ contracts` line; a user-visible failure not handed to resilience.
9. UNVALIDATED_ASSUMPTION: a claim about how people behave stated as fact, without a validation.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
