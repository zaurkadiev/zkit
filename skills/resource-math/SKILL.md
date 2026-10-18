---
name: resource-math
description: Turn agreed zkit requirements into resource math - the workload the system must carry, the resources that bind it (compute, memory, storage, network, external quotas, money, human time), a small executable model with best / expected / worst scenarios, a verdict against every numeric requirement and the budget, and a sensitivity ranking of the assumptions that move the result most. Reads requirements, concept and decisions in docs/zkit/<project>/, settles unknown inputs with the developer one question at a time (research sub-agents for prices and benchmarks), writes docs/zkit/<project>/resource-math.md plus resource_model.py that recomputes everything when an assumption changes, and checks them with a script and an independent reviewer. Use this whenever the user wants capacity or cost estimates, "will it fit the budget / the hardware / the frame time", throughput, sizing, unit economics, or says requirements are agreed and asks for the next step before architecture - even if they never say "math". It does not choose components, products or data formats; those belong to the later steps.
---

# Resource math

Take the requirements and produce **a document and a model**: how much work arrives, which resources it consumes, whether the numbers fit the limits the requirements and the budget set, and which assumptions the answer hangs on. Requirements said *what must be true*; this step checks that it *can* be true before anyone draws an architecture around it - the cheapest moment to learn that a budget, a frame time or a battery cannot work.

Be an honest calculator, not a justifier. Almost every input is an assumption, so say so, give a range, and let the ranking of sensitivities show which guess matters. A verdict "fits" built on one optimistic number is worse than "does not fit": it moves the failure to production. "Does not fit" is a successful result - it sends the developer back to the requirements while the change is cheap.

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: which resources bind this system, which formulas are honest, what the verdict is. Sub-agents only gather evidence (prices, benchmarks, vendor limits, published measurements) through the `research` skill and never decide. Treat the steps as a shape: skip a resource that cannot bind, go deeper where a number decides the verdict.

## Boundary: resource math vs. neighbours
| Requirements (done) | Resource math (this step) | Later steps (do not do here) |
|---|---|---|
| Numeric targets, constraints, budget | Workload model, resource formulas, scenarios, verdicts, sensitivities, per-unit costs and ceilings the design must respect | contracts: external interface formats; data: layout and lifecycle; architecture: parts, products, hosts, queues |
| "≤ N ms", "≤ X per month" | "does it fit, with what margin, if the guess is wrong" | mechanics: algorithms and data structures; resilience: failure handling |

Rules of thumb:
- Name a product, instance type or provider only as the **source of a number** (a price, a published limit), never as a decision. "A 8 GB server costs about 30 per month [R-3]" is evidence; "we run on provider X" is architecture.
- The output of this step is constraints for the design: ceilings per part or per unit ("an environment must idle below 50 MB", "an action must finish within 12 ms"), not the design itself.
- If a detail is useful only to a later step, put it in **Deferred** (`→ architecture: …`), one line.
- Don't bend the requirements silently. If the math shows a target impossible, record the finding, ask the developer, then change the requirements with a dated revision line and a new decision.

## Workflow

### 1. Locate and read the inputs
Zkit docs folder: default `docs/zkit/`; `AGENTS.md`/`CLAUDE.md` may name another; a path in the request wins. Work in `docs/zkit/<project>/` (ask if unclear). Read `requirements.md`, `concept.md`, `decisions.md` fully and relevant research. Collect every `→ resource-math` line: that is the agenda. If code or measurements already exist for this system, read them: a measurement beats any guess.
- No requirements: say so and offer `/zkit:requirements` first, or a short intake marked "no requirements behind it". Don't invent targets.
- Requirements still draft with an open clarity gate: say what is open, offer to finish it; if the developer continues, mark the math draft.
- `resource-math.md` already exists: run the check from step 6 first; if it reports stale requirements or a stale block, list what changed before revising.

### 2. Find what binds this system
Read the requirements as a calculator: which are numeric and resource-bound (latency, throughput, memory, battery, cost, quota, binary size, frame budget) and which are not. Decide which resources can bind for *this* kind of system and say why the others cannot:
- cloud/SaaS: requests and tasks per unit time, compute and memory per active unit, storage and its growth, egress, external-API quotas and rate limits, money per unit (user, organization, request), operator time, and the builder's own time (hours needed for the scope against hours available - for a small team this often binds before money does);
- AI-backed: tokens in and out per task, model price per token, concurrency limits, retries;
- real-time/embedded/games: time per loop or frame, instructions or cycles, RAM and flash, power, interrupt rate;
- data processing: volume and rate, working set, throughput per core.
Write the **workload model**: the units that arrive (users, organizations, agents, tasks, messages, frames, samples), how many, how often, how bursty, and how they combine. Show the developer the binding resources and the workload in a few lines; ask only what is genuinely open.

### 3. Fill the inputs - one question at a time
**Progress counter.** Prefix every question with `[resource-math Q n/N]` (e.g. `[resource-math Q3/12]`): n = questions asked so far, N = your current count of the gaps/forks you still plan to ask about, set once the draft exists. When N changes (new conflict, gap closed by research, developer ends the loop), say it in one line (`N 12→15: new conflict`), never silently. Do not pad questions to reach N; the loop still ends on clarity.

List the assumptions (`A-n`) the formulas need - about 15-20, not more: merge inputs that always move together, and write inputs that cannot change any verdict as plain constants in the model with a comment (trial runs produced 35-44 assumptions and 5,000-word documents, which buried the three that mattered). For each give a unit, a **best / expected / worst** value, an evidence level (**known** - from a requirement or source; **measured**; **assumed**) and a source. Facts you lack go to `research` (prices, published benchmarks, vendor limits): state your opinion - *recommended / optional / not needed, because …* - and, if the developer agrees, run it in the background; cite `[R-n](research/R-n-<slug>.md)`. For facts only the developer has (expected users, usage pattern, what they are willing to pay or spend), ask **one question per turn, 2-4 options, recommended first marked "(Recommended)"**, in plain language with a concrete example of what changes in the result and what each option means. When the developer says "you decide", take your value, mark it *assumed* and give the cheapest validation (a measurement, a spike, a pilot - it becomes a task at the roadmap).

### 4. Build the model
Copy `references/model-template.py` to `docs/zkit/<project>/resource_model.py` and fill it: `ASSUMPTIONS`, `compute()` (plain arithmetic, stdlib, one formula per line with a comment naming the resource), `LIMITS` (every numeric requirement and the budget that the math can test: `req` points to its `NFR-`/`C-` id), optional `UNITS`. Keep it small - a model that needs a manual is a design. Then run `python3 <skill-dir>/scripts/check_resource_math.py <project-dir>` to see the three scenarios and the sensitivity. Sanity-check results against intuition and against any measurement; a surprising number is either a finding or a bug - find out which before showing it.

### 5. Verdict and consequences
For every limit: fits / fits with changes / does not fit, in the best, expected and worst scenarios. Then decide:
- **Fits** in expected and worst: record the margin and the top sensitivities.
- **Fits in expected only:** the worst-case gap is a risk with a named validation, or a requirement or design change.
- **Does not fit in expected:** stop. Options with the developer, one question per turn: change the target (requirements, dated revision + `D-n`), change the scope or the approach (concept or requirements), or accept it with a decision `D-n` that names the cost. Never leave it hanging.
Write the **consequences for the design**: ceilings and unit costs the architecture must respect, the one or two measurements that would most shrink the uncertainty, and where the first spike belongs. Record each settled fork or accepted gap as `D-<n>` in `decisions.md` (anchor, `### D-<n>: …`, status, alternatives, why, date; continue numbering).

### 6. Check - before declaring it done
1. **Mechanical:** `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>`, then `python3 <skill-dir>/scripts/check_resource_math.py <project-dir>` (`--update` regenerates the model block). It checks: the generated block matches the model; every `A-n` and `L-n` of the model is in the document tables and vice versa; evidence levels and sources; every limit cites an existing requirement; a limit failing in the expected scenario has an accepting `D-n`; header counts, verdict, requirements-newer-than-based-on drift; the `CLARITY` line; status *agreed* is refused while the gate is open. Fix every ERROR; for each WARN fix it or write one line saying why it stays.
2. **Semantic:** spawn one fresh reviewer sub-agent (not the writer; give it the paths of `concept.md`, `requirements.md`, `decisions.md`, `resource-math.md`, `resource_model.py`) with the brief in `references/consistency-review.md`. Judge each finding; when a requirement is wrong, update it with a dated revision line and a decision, then re-run `check_requirements.py`. Without sub-agents do the pass yourself against that list.

**Clarity gate** for *agreed*: every numeric Must requirement is either tested by a limit or marked not resource-bound; no limit fails in the expected scenario without a decision; every *assumed* input that moves a verdict has a validation; the reviewer's findings are resolved or recorded. The developer may end the loop earlier; the status then stays *draft* with open items on top.

### 7. Write the files
`resource-math.md` in the developer's language per `references/resource-math-template.md` (read it first); the results block is generated, never typed. Header `Based on` = the requirements' actual date. Run `link_docs.py` at the end. No index files. Then a short chat summary: the verdict in one sentence, the 2-3 assumptions that decide it, what the design must respect, what to measure first, what is open; name the next step (`contracts`). Don't paste the document.

## Quality bar
- Every number is an input with a source, or a result of the model; none is typed twice by hand.
- Ranges, not points; the sensitivity ranking says which guess to spend effort on.
- Verdicts are given per scenario; "does not fit" and "fits only if" are stated plainly.
- Consequences are ceilings and unit costs for the design, not a design.
- Short beats long: roughly 1,500-3,000 words around a model of 30-80 lines and at most ~20 assumptions; if it needs more, the system is probably two systems or the model is modelling noise.
