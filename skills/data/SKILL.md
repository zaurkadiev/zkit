---
name: data
description: Turn agreed zkit requirements, resource math and contracts into the logical data model - which data exists (entities), who writes it, how big it is and how fast it grows (tied to resource-math assumptions), how long it lives, where copies hide (backups, caches, derived data), how sensitive it is, what consistency and speed it needs, and which class of storage fits each group (relational, document, files with versions, append-only log, queue, cache, memory, flash) - plus the memory strategy for in-process and embedded systems (static allocation, pools, buffers, ring buffers sized against the RAM limits). Reads requirements, concept, resource-math, contracts and decisions in docs/zkit/<project>/, settles each fork with the developer one question at a time (research sub-agents for facts), writes docs/zkit/<project>/data.md with a Mermaid ER diagram, and checks it with a script and an independent reviewer. Use this whenever the user wants a data model, entities and relations, storage choice or storage class, retention, deletion or export planning, data lifecycle, memory layout or buffers, or says contracts are done and asks for the next step - even if they never say "data". Tables, indexes, DDL and products belong to later steps; the owner part of each entity is decided at architecture.
---

# Data

Take the requirements, the resource math and the contracts and produce **one file**: the data the system has to hold, in logical form - what it is, who creates it, how much, how long, how sensitive, how consistent, and which class of storage fits - so that the architecture can assign owners and the numbers of the resource math can be checked against real data. The boundary contracts told us what crosses the edge; this step says what lives inside and how it ages.

Be a data steward, not a schema painter. The expensive mistakes are quiet: a copy nobody listed that makes "delete within 30 days" false; a log that grows ten times faster than the budget assumed; two writers for one fact; a class of storage chosen by habit. Prefer the simplest storage class that serves the real access pattern, and say where complexity is speculative.

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: finding the entities, their lifecycles and the tension between requirements (history vs deletion, speed vs consistency, cost vs retention). Sub-agents only gather evidence (limits of a storage class, retention rules, typical sizes, regulatory minimums) through the `research` skill and never decide. Treat the steps as a shape: compress what is trivial, go deeper where a requirement or a number depends on a lifecycle.

## Boundary: data vs. neighbours
| Data (this step) | Earlier (inputs) | Later (do not do here) |
|---|---|---|
| Entities, relations, invariants, writers as **actors** (not parts), size and growth (resource-math `A-n`), retention, copies, deletion path, sensitivity, consistency and access needs, **storage class** with reasons, memory regions for in-process systems | contracts: what crosses the boundary (an entity may mirror a contract payload; the contract wins at the edge); resource-math: the numbers | architecture: which part owns an entity, the product or engine, shards, replicas, topology; mechanics: tables, indexes, DDL, struct layouts, algorithms; resilience: backup and recovery design |

Rules of thumb:
- Choose the **class** of storage (relational, document, versioned files, append-only log, queue, cache, memory, flash) and why; name a product only if a requirement or constraint fixes it. Engines and versions: `→ architecture`.
- Writers are actors (owner, operator, agent role, device, external service), because the parts do not exist yet; the architecture assigns one owning part per entity.
- Logical fields only when they carry an invariant, a size driver or a sensitivity (e.g. "action key, unique per task"); no table design, no types, no indexes.
- If a detail is useful only to a later step, put it in **Deferred** (`→ architecture: …`), one line.
- Don't bend the requirements silently: a lifecycle that cannot meet a requirement is a finding. Record it, ask the developer, then change the requirement with a dated revision line and a decision, or the design approach.

## Workflow

### 1. Locate and read the inputs
Zkit docs folder: default `docs/zkit/`; `AGENTS.md`/`CLAUDE.md` may name another; a path in the request wins. Work in `docs/zkit/<project>/` (ask if unclear). Read `requirements.md`, `concept.md`, `decisions.md`, `resource-math.md` with `resource_model.py`, `contracts.md` with the specs in `contracts/`, and relevant research. Collect every `→ data` line: that is the agenda. If code or schemas already exist, read them: existing data is a constraint.
- No requirements: say so and offer `/zkit:requirements` first, or a short intake marked "no requirements behind it". Don't invent them.
- No resource-math or contracts: proceed, but mark volumes as unanchored and list what is missing; recommend running them first for any system with real load or boundaries.
- Inputs still draft with an open clarity gate: say what is open; if the developer continues, mark the data model draft.
- `data.md` already exists: run the check from step 5 first; if it reports newer inputs, list what changed before revising.

### 2. Find the data
Read the requirements, scenarios and contract payloads as a data steward and list the entities (`E-n`): things the system must remember, produce or hold in memory, including the quiet ones (journals, versions, caches, derived summaries, upload staging, backups, exports, credentials, counters). For each: meaning in a line, writers (actors), size per item and count (as resource-math `A-n` or a known figure), growth, retention, storage class, sensitivity (public / internal / personal / secret), consistency and access needs (needs a transaction with E-m, read-mostly, append-only, latency budget `L-n`), the requirements it serves. Draw the relations in one Mermaid `erDiagram`. Show the developer the entity list in a few lines; ask only what is genuinely open.

### 3. Settle the forks - one question at a time
**Progress counter.** Prefix every question with `[data Q n/N]` (e.g. `[data Q3/12]`): n = questions asked so far, N = your current count of the gaps/forks you still plan to ask about, set once the draft exists. When N changes (new conflict, gap closed by research, developer ends the loop), say it in one line (`N 12→15: new conflict`), never silently. Do not pad questions to reach N; the loop still ends on clarity.

**Context for every question and answer.** Before asking, give the developer enough to decide without re-reading the document: what the question is about, why it matters here (which requirement, limit or risk it moves), what each option changes, and one concrete example of what goes wrong. When the answer comes in, say in a line or two what is now decided and what it affects downstream. When a flow, structure or trade-off is easier to see than to read, add a small diagram (up to about 12 nodes) in the message text before the question, never inside the option labels. Use a ```mermaid block (flowchart, sequence or state) only if the client renders it (the developer said so, or you are publishing to a markdown/artifact viewer); in a plain terminal, or when unsure, draw the same thing as a symbolic ASCII schema (boxes, arrows, a short legend) in a code block.

Typical forks: one store for everything or classes per group, history kept or overwritten, soft vs hard delete, copies and their lifetime vs the deletion requirement, what is derived and recomputable vs stored, who may see which sensitivity, memory strategy (static vs pool vs heap) in constrained systems. For each: 2-3 genuinely different options, what each costs and where it is wrong, compared against the requirement and the resource-math numbers, with your recommendation. Facts you lack go to `research` (state *recommended / optional / not needed, because …*; run it in the background if the developer agrees; cite `[R-n](research/R-n-<slug>.md)`). Ask the developer **one question per turn, 2-4 options, recommended first marked "(Recommended)"**, in plain language with a concrete example of what goes wrong and what each option means; decide yourself only forks with an obvious engineering winner and say so. On "you decide" take your recommendation, mark it *assumed* and name how to validate it. Record each settled fork as `D-<n>` in `decisions.md` (anchor, `### D-<n>: …`, status, alternatives, why, date; continue numbering).

### 4. Lifecycle, copies and memory
For every entity write the lifecycle row: who creates and changes it, when and how it is deleted, and **every copy** (backups, caches, replicas, derived data, logs that quote it, exports, the provider's side) with its lifetime. Personal and secret data must list copies, and the longest chain of copies must meet the deletion and retention requirements - compute it (e.g. backup 14 days + provider retention 7 days = 21 ≤ 30). For in-process and embedded systems add the memory regions (`M-n`): contents, lifetime, size (against the RAM limit `L-n` of resource-math), allocation (static, pool, stack, heap) and what happens on exhaustion. Feed new volumes or growth back: if an entity needs an assumption resource-math lacks, add it there (`resource_model.py`, dated note) rather than inventing a number here.

### 5. Check - before declaring it done
1. **Mechanical:** `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>`, then `python3 <skill-dir>/scripts/check_data.py <project-dir>` (stdlib only; exit 1 on errors). It checks: every entity has meaning, writers, volume, retention, storage class, sensitivity and a serving requirement; volumes cite existing resource-math assumptions; every entity has a lifecycle row with creation and deletion, and personal or secret ones list copies; the ER diagram and the catalog agree; memory regions are complete and cite existing limits; Must requirements about data are served; header counts, drift against requirements, resource-math and contracts; the `CLARITY` line; status *agreed* is refused while the gate is open. Fix every ERROR; for each WARN fix it or write one line saying why it stays.
2. **Semantic:** spawn one fresh reviewer sub-agent (not the writer; give it the paths of `concept.md`, `requirements.md`, `resource-math.md`, `contracts.md` with `contracts/`, `decisions.md`, `data.md`) with the brief in `references/consistency-review.md`. Judge each finding; when a requirement is wrong, update it with a dated revision line and a decision, then re-run its checker. Without sub-agents do the pass yourself against that list.

**Clarity gate** for *agreed*: every entity has a volume (a figure or a resource-math assumption); every retention and deletion requirement is met by the lifecycle including copies, or the gap is a recorded decision; no fork is open; the reviewer's findings are resolved or recorded. The developer may end the loop earlier; the status then stays *draft* with the open items on top.

### 6. Write the file
`data.md` in the developer's language per `references/data-template.md` (read it first). Header `Based on` = the actual dates of requirements, resource-math and contracts. Run `link_docs.py` at the end. No other index files. Then a short chat summary: the main entities and storage classes in two sentences, the lifecycle gaps, changes needed in earlier documents, what is open; name the next step (`architecture`). Don't paste the document.

## Quality bar
- Every entity has a size, a growth, a retention, a class, a sensitivity and a serving requirement; none is stored "just in case".
- Copies are listed, and the deletion and retention requirements are checked against them, not asserted.
- Volumes trace to resource-math assumptions; storage totals stay inside the limits.
- Classes of storage are chosen with reasons; no tables, indexes, DDL, products or owning parts.
- Short beats long: roughly 1,500-3,000 words; past about 25 entities the model is probably a schema in disguise (group the small ones).
