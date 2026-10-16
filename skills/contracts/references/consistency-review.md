# Consistency review brief (requirements + resource math ↔ contracts)

Give this to a fresh reviewer sub-agent with the paths of `concept.md`, `requirements.md`, `resource-math.md` (if any), `decisions.md`, `contracts.md` and the `contracts/` folder of the project. The reviewer reads all fully, edits nothing, reports in the developer's language, and returns at most 25 rows `type | where (X- id, operation or section) | what is wrong | suggested fix`, most serious first, then a one-paragraph verdict (consistent / minor issues / serious issues). Categories:

1. UNCOVERED: a requirement, actor or integration of the requirements/concept that crosses the system boundary and has no contract (or only one direction of a two-way boundary).
2. UNSUPPORTED_RELIANCE: a consumed contract relies on a field, unit, behaviour or guarantee that the counterparty's documentation (cited in research) does not give, or that is only assumed while serving a Must requirement.
3. LIMIT_MISMATCH: a quota, rate, size, latency or price in a contract that disagrees with the resource-math limits or model assumptions, or a counterparty limit no `L-n` tests.
4. NFR_UNREACHABLE: the contract itself makes a requirement impossible (a synchronous call where the requirement is a latency budget the counterparty cannot meet, no idempotency where a requirement forbids duplicates, no way to cancel).
5. ERROR_MODEL: missing or inconsistent errors, retries, timeouts, idempotency, ordering or delivery guarantees; a mutating operation whose retry is unsafe.
6. SECURITY_TRUST: who may call is unclear; credentials or personal data cross a boundary without a stated protection; a trust assumption on the counterparty that the requirements forbid.
7. DESIGN_LEAK: internal parts, storage formats or product choices inside a contract; a counterparty product chosen without a decision.
8. EXAMPLE_DRIFT: examples, schemas, index and prose disagree (a field in the example not in the schema, an operation in the index not in the file, a number in prose different from the spec).
9. STALE: contracts relying on a superseded decision or an old version of a requirement or of resource-math.

Strict but fair; skip nitpicks; «none» for an empty category. The reviewer's table is evidence, not a verdict: the main agent decides each finding.
