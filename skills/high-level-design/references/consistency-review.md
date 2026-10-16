# Consistency review brief (requirements ↔ high-level design)

Give this to a fresh reviewer sub-agent with the paths of `concept.md`, `requirements.md`, `decisions.md` and `high-level-design.md` of the project. The reviewer reads all four fully, reports in the developer's language, edits nothing, and returns at most 25 rows `type | where (B-/I-/S-/D- id or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. UNCOVERED: a Must requirement (or a v1-scope capability in the concept) that no part, interface or decision actually delivers — including ones the traceability table claims but the part's responsibility does not support.
2. NFR_NOT_MET: a scenario walk-through, or the structure itself, that fails a numeric NFR (restart loses state, a bypass of the approval point, one part owning state that two others write, a cost the structure cannot keep under the budget).
3. OVERBUILT: a part, interface or decision that serves no requirement and no stated driver, or a structure far heavier than the load profile needs.
4. CONTRADICTION: the design contradicts a requirement, constraint, concept boundary or non-superseded decision (limits, who approves what, deployment, size of the organisation).
5. STALE: the design relies on a superseded decision or on an old version of a requirement.
6. STATE_OWNERSHIP: a piece of state with no owner or with two writers; an interface whose delivery semantics (idempotent, at-most-once, ordered) are missing where a requirement needs them.
7. DESIGN_LEAK: content that belongs to a later stage (a language, database, broker, version, field-level schema, C4 levels), or a product named where it is not itself the decision.
8. DIAGRAM_DRIFT: the diagram, the parts table, the interfaces table and the scenarios disagree about which parts exist or how they connect.
9. FORK_UNRESOLVED: a decision the document depends on that is still open, hidden behind "to be decided", or taken without alternatives or evidence.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
