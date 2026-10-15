# Consistency review brief (concept ↔ requirements)

Give this to a fresh reviewer sub-agent with the paths of the concept (`concept/NN-<slug>.md`), the `decisions/` folder and the requirements (`requirements/NN-<slug>.md`). The reviewer reads all three fully, reports in the developer's language, edits nothing, and returns at most 25 rows `type | where (concept § / requirement ID) | what is inconsistent | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. SCOPE_GAP: first-version scope in the concept (scope section, capabilities, main scenario) that no requirement covers.
2. SCOPE_LEAK: a requirement covering something the concept puts out of v1 or marks as later.
3. CONTRADICTION: a requirement, number or priority that contradicts the concept or a non-superseded decision (sizes, limits, defaults, who approves what, models, deployment).
4. STALE: a requirement relying on a superseded decision.
5. RISK_UNMAPPED: a concept risk, open question or success criterion that is neither covered by a requirement nor listed as a precondition or conflict.
6. DEFERRED_DROPPED: a concept «Deferred to design → requirements» item that the requirements neither answer nor mention.
7. UNSOURCED: a «known»/«assumed» tag the concept contradicts or doesn't support.
8. DESIGN_LEAK: a requirement prescribing a mechanism instead of observable behaviour, outside Constraints.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
