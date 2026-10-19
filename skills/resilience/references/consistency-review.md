# Consistency review brief (earlier steps ↔ resilience)

Give this to a fresh reviewer sub-agent with the paths of the project's `concept.md`, `requirements.md`, `resource-math.md`, `contracts.md` with `contracts/`, `data.md`, `architecture.md`, `mechanics.md` with `mechanics/`, `decisions.md`, `resilience.md` and `resilience/model.py`. The reviewer reads them fully, edits nothing, reports in the developer's language, and returns at most 25 rows `type | where (F-/T-/O-/DR-/RA-/RL- id or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. MISSING_CASE: a failure or threat that is obvious for this system and absent (single point of failure, loss of the only copy, silent dependency, credential leak or expiry, clock or certificate expiry, operator error, poisoned input, escape from isolation, insider or tenant-to-tenant access).
2. SILENT_FAILURE: a row with no real detection (a signal that cannot fire for this failure, an alert nobody receives, a threshold that is never reached), or a detection that depends on the failing part itself.
3. RESPONSE_WEAK: a response that does not contain the damage or restore the promise (retry loops against a dead dependency, failover with no data, a kill switch no one can reach, a restore that reintroduces deleted personal data).
4. NUMBERS_BROKEN: availability, RPO or RTO arithmetic that is wrong, a failure rate or recovery time that contradicts research or the architecture, a worst case that is not worst, a limit not tied to the requirement it claims, a drill criterion that disagrees with the model.
5. DRILL_HOLLOW: a drill that cannot fail, tests a weaker thing than the row claims, or has no success criterion; a high-severity row proven only by reasoning.
6. SECURITY_GAP: a trust boundary, secret, role or data class that the register ignores; a blast radius larger than the requirements allow; residual risk accepted by no one.
7. COVERAGE: a part, interface, boundary or entity covered only nominally (one row that names it but does not address it) or listed as not applicable without a sound reason.
8. CONTRADICTION: the resilience design contradicts a requirement, the architecture, the mechanics (recoveries that conflict with idempotency or ordering), the data lifecycle (backups vs. deletion), a contract, or a non-superseded decision.
9. OVERBUILT: redundancy or controls disproportionate to the stated budget and promises, or a mitigation for a case the register itself rates L with no requirement behind it.
10. LEAK: code, dashboards in detail, tasks or estimates (roadmap), or changes to the architecture or mechanics not recorded as a decision.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
