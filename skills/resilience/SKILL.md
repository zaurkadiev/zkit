---
name: resilience
description: Turn the agreed zkit architecture and mechanics into the resilience design - a register of faults and threats built by crossing every part, interface, external boundary and data entity with what can go wrong (failure, delay, corruption, hostile input, loss of a copy), each with severity, how it is detected, the response, the recovery target, and the requirement it protects; the observability plan (signals, alerts, diagnostics) that makes failures visible; a numeric model of availability, RPO and RTO with best / expected / worst scenarios checked against the reliability requirements; the security and isolation design (trust boundaries, secrets, access, sandbox containment); and a drill plan that proves the recoveries. Reads requirements, resource-math, contracts, data, architecture, mechanics and decisions in docs/zkit/<project>/, settles each fork with the developer one question at a time (research sub-agents for facts), writes docs/zkit/<project>/resilience.md plus resilience_model.py, and checks them with a script and an independent reviewer. Use this whenever the user wants fault tolerance, reliability, availability or recovery design, backups and RPO/RTO, failure modes (FMEA), threat model or security design, isolation or sandbox containment, monitoring, logging, diagnostics or alerts, or says mechanics is done and asks for the next step - even if they never say "resilience". Phases, spikes and tasks belong to roadmap.
---

# Resilience

Take the architecture and the mechanics and produce **a document and a small model**: what can go wrong or be attacked at every part, interface, boundary and piece of data; how each case is noticed, contained and recovered from; whether the numbers promised to the user (availability, data loss window, recovery time) survive the arithmetic; and how each claim will be proven in a drill. Earlier steps built the structure and made its core behave; this step assumes that structure *will* fail and be attacked and decides what happens next.

Be a pessimist with a spreadsheet, not a checklist author. The expensive gaps are the ones nobody listed: the server holding the database dies with no usable copy; the provider is silent for an hour; a restore brings back data that was meant to be deleted; the log that would explain the incident was never emitted. So build the register by *crossing* what exists with what can happen, let the script prove every part, interface, boundary and entity was looked at, and put numbers on the promises.

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: which failures and threats matter, how bad they are, what response is proportionate, what the model assumes. Sub-agents only gather evidence (hoster failure and restore figures, provider SLAs, known escape classes of an isolation technology, backup tool behaviour, regulatory minimums) through the `research` skill, and never decide. Treat the steps as a shape: compress what is trivial, go deep where a Must requirement or a high-severity fault lives.

## Boundary: resilience vs. neighbours
| Earlier steps (inputs) | Resilience (this step) | Later steps (do not do here) |
|---|---|---|
| architecture: parts, interfaces, scenarios, technology choices; mechanics: the exact behaviour and recoveries inside parts; contracts: boundaries and quotas; data: entities, copies, lifecycle; requirements: the reliability, security and privacy promises | Fault and threat register (`F-n`, `T-n`), observability (`O-n`), numeric model (`RA-n`, `RL-n`), security and isolation design, drills (`DR-n`), residual risks with decisions | roadmap: phases, spikes and tasks that implement and drill all this; implementation: code, dashboards, runbooks in detail |

Rules of thumb:
- Behaviour that is part of normal operation (retries, idempotency, state machines) is mechanics. Here: what happens when those mechanisms themselves are not enough - the node is gone, the dependency is down for an hour, the attacker is inside a sandbox, the copy is corrupted.
- Every register row has a **detection**; a failure with no signal fails silently and is a finding. Every high-severity row has a **drill**, because a recovery nobody has tried is an assumption.
- Numbers are computed, not asserted: availability, RPO and RTO come from the model with best / expected / worst values. A target that fails in the expected scenario needs a decision, not a sentence.
- Security here is design at the trust boundaries (who can reach what, which secrets live where, what a compromised part can touch, what the sandbox contains), not a penetration test. Name residual risks and who accepted them.
- Name a tool or product only as a decision already made in the architecture or as a cheap-to-reverse choice recorded here.
- If a detail is useful only to a later step, put it in **Deferred** (`→ roadmap: spike …`), one line.
- Don't bend earlier documents silently. If the register shows an architecture choice cannot keep a promise (single host vs. 99%), record the finding, ask the developer, then revise the earlier document with a dated revision line and a decision.

## Workflow

### 1. Locate and read the inputs
Zkit docs folder: default `docs/zkit/`; `AGENTS.md`/`CLAUDE.md` may name another; a path in the request wins. Work in `docs/zkit/<project>/` (ask if unclear). Read `requirements.md`, `concept.md`, `resource-math.md` with `resource_model.py`, `contracts.md` with `contracts/`, `data.md`, `architecture.md`, `mechanics.md` with `mechanics/`, `decisions.md` and relevant research. Collect every `→ resilience` line: that is the agenda (architecture and mechanics defer failure policy here). If code or an existing deployment exists, read it.
- No requirements or no architecture: say so and offer the missing step first, or a short intake marked "no requirements/architecture behind it". Don't invent them.
- Inputs still draft with an open clarity gate: say what is open; if the developer continues, mark the resilience draft.
- `resilience.md` already exists: run the check from step 6 first; if it reports newer inputs or a stale model block, list what changed before revising.

### 2. Cross and list
Build the register by crossing, not by brainstorming:
- every part `B-n` × (process dies, stalls, loses state, runs a bad version, is compromised);
- every interface `I-n` and boundary `X-n` × (counterparty down or slow, malformed or hostile input, replay, credential leak or expiry, quota exhausted, contract change);
- every entity `E-n` × (loss, corruption, stale or poisoned copy, unauthorised read, deletion that misses a copy);
- the platform under it (node, disk, network, hoster, clock, certificates, operator mistakes).
Write each real case as a row: `F-n` for accidents and failures, `T-n` for adversaries (what they want, how they reach it, what stops them), with target ids, severity (H: breaks a Must requirement, money, isolation or data; M; L), detection (`O-n`), response, recovery target, the requirement protected, residual risk. Combine rows that share cause and response. Targets with nothing that can go wrong go to *Not applicable* with the reason - the checker requires every target to appear in one place or the other.

### 3. Settle the forks - one question at a time
**Progress counter.** Prefix every question with `[resilience Q n/N]` (e.g. `[resilience Q3/12]`): n = questions asked so far, N = your current count of the gaps/forks you still plan to ask about, set once the draft exists. When N changes (new conflict, gap closed by research, developer ends the loop), say it in one line (`N 12→15: new conflict`), never silently. Do not pad questions to reach N; the loop still ends on clarity.

Typical forks: how much redundancy to buy for the budget (second node, warm standby, backups only), RPO/RTO targets the user is willing to pay for, graceful degradation order (what to shed first), blast-radius limits (per-tenant quotas, kill switches), isolation depth (one more layer vs. accepting the residual risk), secret custody and rotation, alert routing for a solo operator, how much is logged and for how long. For each: 2-3 genuinely different options, what each costs and where it fails, compared against requirements and resource-math prices, with your recommendation. Facts you lack go to `research` (state *recommended / optional / not needed, because …*; run it in the background if the developer agrees; cite `[R-n](research/R-n-<slug>.md)`). Ask the developer **one question per turn, 2-4 options, recommended first marked "(Recommended)"**, in plain language with a concrete example of what goes wrong and what each option means; decide yourself only forks with an obvious engineering winner and say so. On "you decide" take your recommendation, mark it *assumed* and name how to validate it. Record settled forks as `D-<n>` in `decisions.md` (anchor, `### D-<n>: …`, status, alternatives, why, date; continue numbering).

### 4. Observability and drills
**Observability:** list the signals (`O-n`: metric, log, trace, health check, canary, audit record) that detect the rows, where each is emitted (`B-n`), the alert or threshold, who is told and how, how long it is kept (and, for personal data, that the log copy is deletable per the data step). Add the diagnostics needed to explain an incident afterwards. **Drills** (`DR-n`): for each high-severity row, how it will be proven (restore from backup on a clean machine, kill a part mid-action, revoke a key, attempt an escape from the sandbox, silence the provider), the success criterion, and the roadmap task it becomes. A drill that cannot fail proves nothing: state what failure would look like.

### 5. Put numbers on the promises
Copy `references/model-template.py` to `docs/zkit/<project>/resilience_model.py` and fill it: `ASSUMPTIONS` (`RA-n`: failure rates, detection and recovery times, backup interval, copy lifetime, lead times - each with best / expected / worst, evidence level and source), `compute()` (plain arithmetic: RTO, RPO, expected downtime per month, availability), `LIMITS` (`RL-n`: every reliability, recovery and data-loss requirement, `req` pointing to its id). Run `python3 <skill-dir>/scripts/check_resilience.py <project-dir> --update` to fill the generated block and see the verdicts. A limit that fails in the expected scenario stops the step: with the developer, one question per turn, change the target (revise the requirement), change the design (add redundancy, shorten recovery), or accept it with a `D-n` that names the consequence. Never leave it hanging.

### 6. Check - before declaring it done
1. **Mechanical:** `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>`, then `python3 <skill-dir>/scripts/check_resilience.py <project-dir>` (stdlib only; exit 1 on errors). It checks: the generated model block is fresh; model assumptions and limits equal the document tables; every register row is complete, cites existing signals and requirements, and every high-severity row has a drill; every part, interface, boundary and entity of the earlier documents is a target of some row or listed as not applicable with a reason; limits cite existing requirements and any failing in the expected scenario has an accepting decision; header counts and drift against all earlier documents; the `CLARITY` line; status *agreed* is refused while the gate is open. Fix every ERROR; for each WARN fix it or write one line saying why it stays.
2. **Semantic:** spawn one fresh reviewer sub-agent (not the writer; give it the paths of the project's documents, `contracts/`, `mechanics/` and `resilience_model.py`) with the brief in `references/consistency-review.md`. Judge each finding; when an earlier document is wrong, revise it with a dated revision line and a decision, then re-run its checker. Without sub-agents do the pass yourself against that list.

**Clarity gate** for *agreed*: every target covered; every high-severity row has a signal and a drill; no limit fails in the expected scenario without a decision; every *assumed* input that moves a verdict has a validation; the reviewer's findings are resolved or recorded. The developer may end the loop earlier; the status then stays *draft* with the open items on top.

### 7. Write the file
`resilience.md` in the developer's language per `references/resilience-template.md` (read it first); the model block is generated, never typed. Header `Based on` = the actual dates of requirements, architecture, data and contracts. Run `link_docs.py` at the end. No other index files. Then a short chat summary: the verdict on the numbers in one sentence, the worst faults and threats, what the architecture must change, which drills come first, what is open; name the next step (`roadmap`). Don't paste the document.

## Quality bar
- Every part, interface, boundary and entity was crossed with what can go wrong, and the script proves it.
- Every row has a detection; every high-severity row has a drill that could fail.
- Availability, RPO and RTO are computed with ranges and tested against the requirements; failing targets carry decisions.
- Security is expressed as trust boundaries, secret custody, containment and residual risk with named acceptors.
- No code, no dashboards in detail, no tasks (roadmap), no re-design of mechanics.
- Short beats long: roughly 3,000-5,000 words around the model; merge rows with the same cause and response.
