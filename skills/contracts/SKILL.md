---
name: contracts
description: Turn agreed zkit requirements (and resource math) into the contracts at the system's external boundaries - what the system consumes from others (model providers, sign-in, mail, hosting, devices, hardware buses) and what it publishes (its public API, incoming events, files, frames) - as machine-readable specs (OpenAPI, AsyncAPI, JSON Schema in YAML, or a card for registers and binary frames) plus an index document, with examples validated against the schemas, error and retry behaviour, limits tied to the resource-math limits, authentication, versioning, and a record of what is verified against the counterparty's documentation. Reads requirements, concept, resource-math and decisions in docs/zkit/<project>/, settles each fork with the developer one question at a time (research sub-agents for what counterparties really do), writes docs/zkit/<project>/contracts.md and contracts/*.yaml, and checks them with a script and an independent reviewer. Use this whenever the user wants API contracts, interface specs, OpenAPI/AsyncAPI, "how do we talk to X", boundary or integration contracts, event formats, or says resource math is done and asks for the next step - even if they never say "contract". Internal contracts between the system's own parts belong to the architecture step; storage formats to the data step.
---

# Contracts

Take the requirements and the resource math and produce **an index document and a set of spec files**: for every boundary between the system and the outside world, a contract precise enough that someone on either side can build against it without a meeting. Resource math told us what the numbers must be; this step pins down *what crosses each boundary, in which shape, with which failure behaviour*, before the architecture decides which parts sit behind it.

Be a contract lawyer, not a typist. A published contract is a promise you must keep; a consumed contract is a dependency you have not yet checked. The usual failure is a boundary written from memory: the provider does not return usage the way the spec assumed, the sign-in service has no field the design needs, the retry rule was never stated. Check consumed contracts against the counterparty's real documentation (through `research`), and mark honestly what is still unverified.

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: which boundaries exist, what each contract must say, which fork is worth a question. Sub-agents only gather evidence (provider docs, field lists, limits, error codes, standards) through the `research` skill and never decide. Treat the steps as a shape: compress a boundary that is trivial, go deeper where a requirement or a resource-math limit depends on it.

## Boundary: contracts vs. neighbours
| Contracts (this step) | Later steps (do not do here) |
|---|---|
| Boundary with every outside actor and system, both directions: consumed (they dictate, we record what we rely on, verified) and published (we dictate) | architecture: parts, internal interfaces between them, products and hosts; the public API may be refined once parts are known |
| Operations, payload fields with types and examples, errors, retries and idempotency, auth, limits and quotas (tied to resource-math `L-n`), versioning | data: how things are stored; mechanics: algorithms; resilience: failure handling inside the system |
| For a counterparty not yet chosen: the **capabilities required** of any candidate, plus which candidates were checked | choosing the counterparty or the product: architecture and decisions |

Rules of thumb:
- Name a counterparty only as a fact about the boundary (it is the sign-in service the requirements already fix, or a candidate that was checked). Picking among candidates is a decision (`D-n`), usually architecture's.
- Contracts mention no internal parts (`B-n`); they are written before the parts exist. Where a published API will obviously change with the architecture, mark it `x-status: draft` rather than guessing.
- If a detail is useful only to a later step, put it in **Deferred** (`→ architecture: …`), one line.
- Don't bend the requirements silently: a contract that cannot satisfy a requirement (the provider lacks the field, the quota is below the load) is a finding. Record it, ask the developer, then change the requirement with a dated revision line and a decision, or the approach.

## Workflow

### 1. Locate and read the inputs
Zkit docs folder: default `docs/zkit/`; `AGENTS.md`/`CLAUDE.md` may name another; a path in the request wins. Work in `docs/zkit/<project>/` (ask if unclear). Read `requirements.md`, `concept.md`, `decisions.md`, and `resource-math.md` with `resource_model.py` if they exist, and `ux.md` if the ux step was done; read relevant research. Collect every `→ contracts` line (those of `ux.md` are the operations its surfaces need): that is the agenda. If code or existing API files exist, read them: an existing contract is a constraint.
- No requirements: say so and offer `/zkit:requirements` first, or a short intake marked "no requirements behind it". Don't invent them.
- No resource-math: proceed, but say limits are not tied to numbers and list quotas as open (recommend running `resource-math` first for any system with real load or a budget).
- Requirements or resource-math still draft with an open clarity gate: say what is open; if the developer continues, mark the contracts draft.
- `contracts.md` already exists: run the check from step 6 first; if it reports newer inputs, list what changed before revising.

### 2. Map the boundaries
From the requirements' actors, integrations and constraints, and the concept, list every place where the system meets the outside (`X-n`). For each: who is on the other side, direction (**consumed** - they dictate, **published** - we dictate), and the paradigm (HTTP request/response, events or messages, files, streams, interrupts or registers, shared memory, binary frames). Typical sets: people and their clients (UI, chat, email; when `ux.md` exists its surfaces define what these boundaries must carry, and the person-facing side itself stays in that document), identity, model or data providers, payment, storage, hosting and runtime, other systems that call in, hardware buses. For embedded and real-time systems the boundaries are buses, registers, interrupts, timing windows and frame layouts; use a card for them (below). Show the list to the developer in a few lines; ask only what is genuinely open.

### 3. Fill each contract - one question at a time
**Progress counter.** Prefix every question with `[contracts Q n/N]` (e.g. `[contracts Q3/12]`): n = questions asked so far, N = your current count of the gaps/forks you still plan to ask about, set once the draft exists. When N changes (new conflict, gap closed by research, developer ends the loop), say it in one line (`N 12→15: new conflict`), never silently. Do not pad questions to reach N; the loop still ends on clarity.

**Consumed:** the counterparty's documentation is the source. Send the facts to `research` (field names and units, error codes, rate and size limits, retry guidance, versioning, pricing fields) - state your opinion *recommended / optional / not needed, because …* and, if the developer agrees, run it in the background; cite `[R-n](research/R-n-<slug>.md)`. Write what the system **relies on** (not the whole foreign API), mark `x-verified`, and tie quotas and prices to resource-math `L-n`. A reliance the documentation does not support is a finding, not a footnote.
**Published:** derive operations from the functional requirements and scenarios, then design them: resources and verbs, inputs and outputs with types, pagination, errors, authentication and who may call, idempotency of every mutating operation, rate limits, versioning and compatibility rules, events with ordering and delivery guarantees.
For every fork (sync vs. async, polling vs. push, one provider-neutral shape vs. native shapes, versioning style, error model) ask **one question per turn, 2-4 options, recommended first marked "(Recommended)"**, in plain language with a concrete example of what goes wrong and what each option means; decide yourself only forks with an obvious engineering winner, and say so. On "you decide" take your recommendation, mark it *assumed* and name how to validate it. Record settled forks as `D-<n>` in `decisions.md` (anchor, `### D-<n>: …`, status, alternatives, why, date).

### 4. Write the specs
One file per boundary in `contracts/`: OpenAPI 3.1 for request/response, AsyncAPI 3 for events and messages, a JSON Schema for a standalone payload or file, a Markdown **card** (`layout`, `timing and limits`, `errors` sections) for registers, bus frames and other binary paradigms. Use `references/contract-examples.md` for the skeleton and the `x-` extensions the checker reads. Every payload has a schema and at least one realistic example (the checker validates examples against schemas); every operation has an error response; every mutating operation states its idempotency; consumed contracts carry `x-verified`; every spec carries `x-limits`, `x-serves`.

### 5. Check - before declaring it done
1. **Mechanical:** `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>`, then `python3 <skill-dir>/scripts/check_contracts.py <project-dir>` (needs PyYAML and jsonschema for the full check; without them it says what was not checked). It checks: index rows vs spec files; each spec parses, carries its boundary id and direction; OpenAPI/AsyncAPI structure, error responses, operation ids, security, idempotency; examples validate against their schemas; limits cited exist in resource-math; served requirements exist; consumed contracts verified; header counts and drift against requirements and resource-math; the `CLARITY` line; status *agreed* refused while the gate is open. Fix every ERROR; for each WARN fix it or write one line saying why it stays.
2. **Semantic:** spawn one fresh reviewer sub-agent (not the writer; give it the paths of `concept.md`, `requirements.md`, `resource-math.md`, `decisions.md`, `contracts.md` and `contracts/`) with the brief in `references/consistency-review.md`. Judge each finding; when a requirement is wrong, update it with a dated revision line and a decision, then re-run its checker. Without sub-agents do the pass yourself against that list.

**Clarity gate** for *agreed*: every requirement that crosses a boundary is served by a contract; every consumed contract that serves a Must requirement is verified against the counterparty's documentation; no fork is open; the reviewer's findings are resolved or recorded. The developer may end the loop earlier; the status then stays *draft* with the open items on top.

### 6. Write the index
`contracts.md` in the developer's language per `references/contracts-template.md` (read it first): the boundary table, the conventions shared by all specs (error model, identifiers, time, versioning), the consequences for the architecture, deferred items, risks, the check record. Header `Based on` = the actual dates of the requirements, resource-math and, when present, ux. Run `link_docs.py` at the end. No other index files. Then a short chat summary: the boundaries in two sentences, the contracts that rest on unverified assumptions, requirement findings, what is open; name the next step (`data`). Don't paste the document.

## Quality bar
- Every boundary of the requirements' actors and integrations has a contract, in both directions where both exist.
- A consumed contract says what we rely on and where that was verified; unverified ones are visible.
- Specs are valid, examples validate, every operation has errors, mutating operations state idempotency, quotas tie to resource-math.
- No internal parts, storage formats or product choices; capabilities required when the counterparty is open.
- Short beats long: a spec states what is promised, not the whole foreign API; the index is a page or two.
