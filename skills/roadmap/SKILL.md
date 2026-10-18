---
name: roadmap
description: Turn the whole agreed zkit chain (requirements, resource math, contracts, data, architecture, mechanics, resilience) into an executable roadmap - risk-first phases with go / change / stop gates, a thin end-to-end slice, then increments by requirement priority, with detailed tasks (4-16 hours, dependencies, acceptance criteria traced to requirements, limits, drills and decisions) up to the nearest gates and epics with hour ranges beyond them, and a schedule computed for one developer in best / expected / worst scenarios against the available hours and the deadline or budget, with the cuts that would make it fit. Collects every spike, measurement, drill and validation the earlier steps deferred, checks that every Must requirement and every drill is planned, settles forks with the developer one question at a time, writes docs/zkit/<project>/roadmap.md with a script-generated schedule, and checks it with a script and an independent reviewer. Use this whenever the user wants a roadmap, plan, milestones, phases, task breakdown, backlog, estimates, "what do we do first", "will it fit the time", a plan for an agent or developer to execute, or says resilience/architecture is done and asks for the next step - even if they never say "roadmap".
---

# Roadmap

Take everything the chain produced and turn it into **a plan someone can execute**: which risks to retire first, what the smallest working slice is, how the rest grows, which tasks to do next, how long it takes for the one person doing it, and what to cut if it does not fit. The earlier steps said what to build, how much it costs, how it is structured and how it fails; this step says *in what order, by when, and what proves each step is done*.

Be a sober planner, not a Gantt painter. The usual lies are quiet: a plan that builds infrastructure for months before it learns the unit economics do not work; estimates without ranges; "Must" scope that exceeds the hours available by a factor of four. So put the things that can kill the project first, give every task a range and an acceptance test, let a script do the calendar arithmetic, and make the gates carry real decisions.

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: choosing the phases, slicing the work, estimating ranges, deciding what the gates decide, recommending the cuts. Sub-agents only gather evidence (typical effort for a technology, lead times, provider approval times) through the `research` skill, and never decide. Treat the steps as a shape: compress what is obvious, go deep where an estimate or a dependency decides the date.

## Boundary: roadmap vs. neighbours
| Earlier steps (inputs) | Roadmap (this step) | Beyond (do not do here) |
|---|---|---|
| requirements (priorities, constraints, the developer's capacity); resource-math (cost and hour estimates, spikes); contracts; data; architecture (assumptions with validations); mechanics (models, formats); resilience (drills, residual risks, gates) | Phases `PH-n`, gates `G-n`, detailed tasks `TK-n` and epics `EP-n` with hour ranges, dependencies, waits, acceptance criteria, the computed schedule, cut options, risks of the plan | implementation itself; code, tickets in a tracker (tasks can be exported by hand or by an agent later); re-design of earlier steps (if the plan exposes a problem, it goes back as a finding) |

Rules of thumb:
- **Risk first.** Phase 0 holds what can kill or reshape the project: spikes, measurements, drills and validations deferred by earlier steps (`→ roadmap` lines, assumptions with a named validation, `DR-n`, failing limits, accepted residual risks). Its gate decides *continue / change the design / stop* by criteria taken from requirements and limits, not by feeling.
- **Then a thin slice**: one scenario end to end through the real structure, as small as possible, proving the architecture works. **Then increments** in requirement priority order (Must before Should), each ending in a gate or a release.
- **Rolling detail.** Detailed tasks (4-16 hours, one acceptance test each) only up to the next gates; later phases are epics with best / expected / worst hours and dependencies. After a gate, the skill runs again and details the next phase.
- **Estimates are ranges** (best ≤ expected ≤ worst, in hours) with the planner's reasons in the task or the epic; where an earlier step already estimated (resource-math builder hours), use it and reconcile.
- **The calendar is computed.** The capacity table (hours per week for the one developer in each scenario, deadline in weeks if there is one) plus dependencies and external waits give the schedule; the script does the arithmetic. A plan that misses the deadline in the expected scenario needs cuts or a decision, not a sentence.
- A task is **done** when its acceptance criterion holds: a measurement within a limit, a drill passed, a model run, a scenario walked, a contract test green. If it cannot be checked, rewrite it.
- If a detail is useful only for later re-planning, put it in **Deferred**, one line.
- Don't bend earlier documents silently. If the plan exposes an impossible requirement or a missing step, record it as a finding, ask the developer, and revise the earlier document with a dated revision line and a decision.

## Workflow

### 1. Locate and read the inputs
Zkit docs folder: default `docs/zkit/`; `AGENTS.md`/`CLAUDE.md` may name another; a path in the request wins. Work in `docs/zkit/<project>/` (ask if unclear). Read every document that exists: `concept.md`, `requirements.md`, `resource-math.md` with `resource_model.py`, `ux.md` if present, `contracts.md`, `data.md`, `architecture.md`, `mechanics.md` with `mechanics/`, `resilience.md` with `resilience_model.py`, `decisions.md`, research. Collect every `→ roadmap` line, every assumption with a validation, every drill `DR-n`, every spike named anywhere, every limit that fails in the worst scenario, every accepted residual risk: that is the backlog of *proof work*. Collect the capacity and constraints the developer stated (hours per week, deadline, budget, team).
- No requirements or architecture: say so and offer the missing step first, or a short intake marked "no requirements/architecture behind it". Don't invent them.
- Earlier steps missing (no resource-math, mechanics or resilience): proceed only if the developer wants to, mark the roadmap draft, and list the proof work that is therefore unknown.
- Inputs still draft with an open clarity gate: say what is open; if the developer continues, mark the roadmap draft.
- `roadmap.md` already exists: run the check from step 6 first; if it reports newer inputs or a stale schedule, list what changed before revising. After a gate passes or fails, update: mark done tasks, re-detail the next phase, keep ids.

### 2. Frame the plan
Capacity (hours per week best / expected / worst, deadline), the scope in priority order, the nearest hard question per gate. Show the developer in a few lines and ask what is genuinely open (capacity and deadline are usually the open ones): one question per turn.

### 3. Settle the forks - one question at a time
**Progress counter.** Prefix every question with `[roadmap Q n/N]` (e.g. `[roadmap Q3/12]`): n = questions asked so far, N = your current count of the gaps/forks you still plan to ask about, set once the draft exists. When N changes (new conflict, gap closed by research, developer ends the loop), say it in one line (`N 12→15: new conflict`), never silently. Do not pad questions to reach N; the loop still ends on clarity.

**Context for every question and answer.** Before asking, give the developer enough to decide without re-reading the document: what the question is about, why it matters here (which requirement, limit or risk it moves), what each option changes, and one concrete example of what goes wrong. When the answer comes in, say in a line or two what is now decided and what it affects downstream. When a flow, structure or trade-off is easier to see than to read, add a small diagram (up to about 12 nodes) in the message text before the question, never inside the option labels. Use a ```mermaid block (flowchart, sequence or state) only if the client renders it (the developer said so, or you are publishing to a markdown/artifact viewer); in a plain terminal, or when unsure, draw the same thing as a symbolic ASCII schema (boxes, arrows, a short legend) in a code block.

**Stopping rules.** Budget: 12 questions per step; N never exceeds it. Going over needs a one-line reason and the developer's yes. Freeze the list of blocking gaps (the ones the clarity gate names) once the draft exists; a new blocking gap found later is added explicitly and spends budget. Ask only if a different answer would change a number, priority, verdict or decision, and only about blocking gaps; every other gap becomes `assumed` with a way to validate it, without a question. Every question must close a gap or turn it into `assumed`, so the open count only goes down. At question 8 say: `k gaps left; I suggest accepting my recommendations and writing it up - continue or close?` When the budget is spent, remaining gaps become `assumed` unless the developer extends it.

Typical forks: what goes into the thin slice, whether to buy time with scope (cut Should, shrink the first release) or with calendar (extend the deadline), pilot size, order of risky spikes, build vs. adopt when a spike disappoints, whom to show the slice. For each: 2-3 genuinely different options, what each costs in hours and risk, compared against the schedule, with your recommendation. Facts you lack go to `research` (state *recommended / optional / not needed, because …*). Ask the developer **one question per turn, 2-4 options, recommended first marked "(Recommended)"**, in plain language with a concrete example of what changes in the plan; decide yourself only forks with an obvious winner and say so. On "you decide" take your recommendation, mark it *assumed*. Record settled forks as `D-<n>` in `decisions.md`.

### 4. Build phases, gates and items
Phase 0: the proof work, ordered by (how much the answer can change the plan) × (cheapness), each as a task with a real acceptance criterion. Gate `G-0`: criteria (limits and requirements to meet, drills passed) and **the rule for each outcome** (continue / change the design in a named way / stop). Phase 1: the thin slice. Later phases: increments as epics. Every Must requirement and every drill is served by at least one task or epic. Put external waits (provider approval, hardware lead time) in the *Wait* column so they overlap with work. Keep tasks at 4-16 expected hours; split larger ones.

### 5. Compute and cut
Write the capacity table, then run `python3 <skill-dir>/scripts/check_roadmap.py <project-dir> --update` to fill the schedule block. Read it as a skeptic: which phase eats the hours, which scenario misses the deadline, where the critical path runs. If the expected scenario misses the deadline, stop and work with the developer, one question per turn: cut scope (name the Should items and hours saved), shorten the first release, add capacity, move the deadline, or accept it with a `D-<n>` naming the consequence. Write the options in the *Cuts* section either way.

### 6. Check - before declaring it done
1. **Mechanical:** `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>`, then `python3 <skill-dir>/scripts/check_roadmap.py <project-dir>` (stdlib only; exit 1 on errors). It checks: ids unique; every item has hours (best ≤ expected ≤ worst), a phase, existing dependencies without cycles, tasks have acceptance criteria; gates have criteria and an outcome rule; the first phase holds proof work; every Must requirement and every resilience drill is planned; the schedule block is fresh and the expected scenario meets the deadline or has cuts or a decision; header counts; drift against all earlier documents; the `CLARITY` line; status *agreed* is refused while the gate is open. Fix every ERROR; for each WARN fix it or write one line saying why it stays.
2. **Semantic:** spawn one fresh reviewer sub-agent (not the writer; give it the paths of the project's documents) with the brief in `references/consistency-review.md`. Judge each finding; when an earlier document is wrong, revise it with a dated revision line and a decision, then re-run its checker. Without sub-agents do the pass yourself against that list.

**Clarity gate** for *agreed*: every Must requirement and drill planned; every gate has criteria and outcome rules; the expected scenario meets the deadline or the miss is a recorded decision; the reviewer's findings are resolved or recorded. The developer may end the loop earlier; the status then stays *draft*.

### 7. Write the file
`roadmap.md` in the developer's language per `references/roadmap-template.md` (read it first); the schedule block is generated, never typed. Header `Based on` = the actual dates of the earlier documents. Run `link_docs.py` at the end. No other index files. Then a short chat summary: the verdict on time in one sentence, the phase 0 questions and the first gate, the cuts if needed, what the developer should do first on Monday; offer to detail the next phase after the gate. Don't paste the document.

## Quality bar
- The things that can kill the project are in phase 0 with acceptance criteria and a gate that decides.
- Every task has a range, dependencies, an acceptance criterion and a trace to a requirement, limit, drill or decision; every Must requirement and drill is planned.
- The calendar comes from the script, in three scenarios, against the real capacity and deadline; misses come with cuts.
- Detail is where the next work is; later phases are epics; no 200-row backlog nobody trusts.
- Short beats long: roughly 2,500-4,500 words; tasks live in tables.
