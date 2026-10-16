---
name: high-level-design
description: Turn an agreed zkit requirements document into a high-level design - the big parts of the system, their responsibilities and links, a draft API between them, and the few expensive architectural decisions with options and evidence. Reads requirements, concept and decisions in docs/zkit/<project>/, extracts the architecturally significant requirements, settles each fork with the developer one question at a time (research sub-agents for facts), walks key scenarios including failures against the structure, and writes docs/zkit/<project>/high-level-design.md with a Mermaid diagram, traceability from every Must requirement to a part, and a script plus independent-reviewer check. Use this whenever the user wants architecture, a high-level design or HLD, system structure, "what are the components", build vs adopt of a foundation, a draft API, or says requirements are agreed and asks for the next step - even if they never say "design". It chooses styles and classes of solutions; languages, databases, brokers, versions and detailed API belong to design-details.
---

# High-level design

Take the requirements and produce **one file**: the architecture at the level where it is still cheap to change - which big parts exist, what each is responsible for, how they talk, and which few decisions shape everything else - with proof that it can meet the requirements. Requirements said *what must be true*; this step answers *what structure makes it true*, so that `design-details`, `final design` (C4), `detailed specs` and finally `roadmap`/`tasks` have something solid to refine.

Be an honest architect, not a diagram painter. A structure that looks tidy but was never walked through the hard requirements (restart in the middle of a send, quota exhausted, hostile input) only moves the failure to implementation. Prefer the simplest structure that serves the drivers and the load; say where complexity is speculative.

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: choosing drivers, structuring the parts, comparing options, walking scenarios, recommending. Sub-agents only gather evidence (what a foundation product really supports, licences, limits, how a pattern fails in practice) through the `research` skill, and never decide. Treat the steps as a shape: compress what adds nothing, go deeper where a requirement is hard.

## Boundary: high-level design vs. neighbours
| Requirements (done) | High-level design (this step) | Later stages (do not do here) |
|---|---|---|
| What, how well, constraints | Parts, responsibilities, ownership of state, links, delivery semantics, draft API (operations in words), key decisions with options | design-details: languages, databases, brokers, versions, field-level contracts, detailed API, data model, algorithms |
| Numbers | Which part carries which number; scenarios proving it | final design: C4 levels; detailed specs; roadmap and tasks |

Rules of thumb:
- Choose the **style and class** of a solution (adopt a foundation or build, actor model or queues, where isolated work environments live, managed service or own) and name products only where the choice itself is the decision (e.g. adopt a named open-source foundation). Language, database, broker, cloud service, version: `→ design-details`.
- The **draft API** is operations as verb + object between parts and to the outside, inputs and outputs in words, and delivery semantics where a requirement demands them (idempotent, at-most-once, ordered). Not schemas or field types; design-details refines it.
- One simple Mermaid diagram of parts and links; C4 is built from it at final design, so don't draw levels twice.
- If a detail is useful only to a later stage, don't delete it: put it in **Deferred** (`→ design-details: …`), one line.
- Don't re-argue the requirements. If the design shows a requirement is wrong, impossible or conflicting, record it as a finding and let the developer decide; update the requirements (dated revision line + a decision) instead of silently bending the design around it.

## Workflow

### 1. Locate and read the inputs
Find the zkit docs folder: default `docs/zkit/`; check the project's `AGENTS.md` (or `CLAUDE.md`) for another folder; a path in the user's request wins. Work in the project the request is about (`docs/zkit/<project>/`; ask if unclear). Layout shared by all zkit skills: `concept.md`, `requirements.md`, `high-level-design.md`, `decisions.md` (one file, entries `D-<n>`), `research/R-<n>-<slug>.md`, no index files. Read `requirements.md`, `concept.md` and `decisions.md` fully, plus relevant research reports. Collect every `→ high-level-design` line from the concept and requirements: that is your starting agenda. If the repository already contains code for this system, look at it: existing structure is a constraint and a candidate foundation.

- No requirements document: say so and offer to run `/zkit:requirements` first (recommended), or a short intake marked "no requirements behind it". Don't fabricate requirements.
- Requirements still `черновик`/draft with an open clarity gate: say what is open (the checker prints a `CLARITY` line) and offer to finish it first; if the developer wants to continue, continue and mark the design draft, listing which requirements it rests on unconfirmed.
- Concept verdict *Validate first*: design the recommended path anyway, keep its gates visible as risks, and prefer structures that keep the validation cheap.
- Superseded decisions are history; design from the current ones.
- `high-level-design.md` already exists: run the check from step 6 first; if it says the requirements are newer, list what changed before revising.

### 2. Extract the drivers - before designing anything
Read the requirements as an architect: which ones are *architecturally significant* (hard to meet, numeric, cross-cutting, or constraining the structure) and which are plain features that fit wherever the structure puts them. Write the driver table (requirement → why it shapes the structure), rank the top 3-5 quality attributes, and gather the constraints and load figures the design is sized against. Show this to the developer in a few lines and ask only if the ranking is genuinely open (e.g. cost vs. reliability) - one question, with your recommendation.

### 3. Settle the forks - one question at a time
List the decisions that are expensive to reverse (adopt vs. build a foundation, how agents or workers are modelled, where isolated environments live, how approvals are enforced, how state and history are kept, tenant isolation, managed vs. self-hosted). For each fork:
- 2-3 genuinely different options at style level, what each costs and where it is the wrong choice, compared on the drivers, with your recommendation.
- Facts you lack (does the foundation support X, licence terms, a service's real limits) go to `research`: state your opinion - *recommended / optional / not needed, because …* - and, if the developer agrees, run it in the background and keep going. Cite reports as `[R-n](research/R-n-<slug>.md)`.
- Ask the developer **one question per turn, 2-4 options, your recommended one first marked "(Recommended)"**, in plain language with a concrete example of what goes wrong and what each option means for them (they may not share your jargon); use an interactive question tool if available. Decide yourself only forks that are pure engineering with an obvious winner, and say so. When the developer says "you decide", take your recommendation and mark it *assumed* with the way to validate it.
- Record each settled fork as `D-<n>` in `decisions.md` (anchor, `### D-<n>: …`, status line, alternatives, why, date; continue the numbering).

### 4. Build the structure
Derive 4-8 parts (`B-n`) from the decisions and drivers; fewer parts than ten is the rule, not the exception. For each: one-sentence responsibility, what state it owns (exactly one owner per piece of state), build/adopt/buy, and the requirements it serves. Then the interfaces (`I-n`): who talks to whom, what passes, sync/async/event, and the draft API operations with delivery semantics where a requirement demands them. Draw the Mermaid diagram from the tables, not the other way round. Test each part: if you can't say what would change it, merge it; if it has two reasons to change, split it.

### 5. Walk the scenarios
Pick 3-5 scenarios (`S-n`): the main flow and at least two taken from the hardest Must requirements (restart in the middle of an external action, quota exhausted mid-goal, hostile input, a part unavailable, the human not answering). Walk each step by step through parts and interfaces; for each write the outcome against the requirement and any gap found. A gap is a finding: fix the structure (and say so), or record it as a risk or a requirements issue. A scenario that always passes proves nothing - choose ones that could fail.

### 6. Check the design - before declaring it done
Two checks, in this order:

1. **Mechanical:** run `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>` (links `D-n` and `[R-n]` mentions, rebuilds back-links), then `python3 <skill-dir>/scripts/check_hld.py <project-dir>` (stdlib only; exit 1 on errors). It checks: IDs unique and complete rows; header counts; every Must requirement of the requirements appears in the traceability table and points to existing parts or decisions; every part serves something and appears in the diagram, every diagram node and interface endpoint exists; scenarios use existing parts and interfaces and at least one is a failure scenario; cited decisions exist, are not superseded and are links; research links; relative links resolve; requirements not newer than the date the design is based on; technology words outside decisions and constraints; the `CLARITY` line (Must requirements without a covering part, forks still open, architectural assumptions without a validation) and the rule that status *agreed* is refused while the gate is open. Fix every ERROR; for each WARN fix it or write one line saying why it stays.
2. **Semantic:** spawn one fresh reviewer sub-agent (it must not have written the document; give it only the paths of `concept.md`, `requirements.md`, `decisions.md`, `high-level-design.md`) with the brief in `references/consistency-review.md`. Judge each finding: fix the design, or - when the requirement is wrong or impossible - update the requirements with a dated revision line and a new decision, then re-run `check_requirements.py` of the `requirements` skill too. Ask the developer with plain-language context before changing what they decided. Without sub-agents do the same pass yourself against that list, re-reading the requirements.

The **clarity gate** for the status *agreed*: every Must requirement is covered by a part; no fork is still open; each architectural assumption that carries a Must requirement has a named validation (a spike or measurement - it becomes a task at the roadmap stage); the reviewer's findings are resolved or recorded. The developer can end the loop earlier; then the status stays *draft* and the open items sit at the top.

### 7. Write the file
Write `high-level-design.md` in the project folder in the developer's language, using `references/hld-template.md` (read it before writing). If the file exists, read and revise it: keep IDs, add a short `## Changes since previous version`. Set the header's `Based on` line to the requirements' actual date (the script uses it to detect drift) and record the check outcome in the *Consistency check* section. Run `link_docs.py` at the end (write mentions as plain `D-<n>`). There are no index files.

Then a short chat summary: the architecture in two sentences, the 2-3 decisions that matter most, the check results, the riskiest assumption and how it will be validated, and what is open; offer another question round if gaps remain; name the next step (`design-details`). Don't paste the document.

## Quality bar
- Every Must requirement traces to a part, an interface or a decision; no part exists without a reason.
- Every expensive fork has options, a recommendation, evidence where facts mattered, and a `D-n` entry.
- The scenarios include failures and could have failed; gaps they found were fixed or recorded.
- Parts, interfaces, diagram and scenarios agree with each other, and this is checked.
- Styles and classes are chosen, products only where the choice is the decision; no schemas, languages, databases, brokers, versions or C4 levels.
- Short beats long: tables over prose, roughly 3,000-4,500 words (trial runs overshot to ~5,500 by repeating the part-to-requirement mapping in three tables: state it once in the parts table, group the traceability rows by theme); past about 10 parts the structure is probably design-details in disguise.
