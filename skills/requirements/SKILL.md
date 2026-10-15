---
name: requirements
description: Turn a zkit concept document into a numbered, testable requirements specification. Reads docs/zkit/01-concept.md and decisions.md, drafts functional and non-functional requirements, constraints and load assumptions straight from the concept, then closes the gaps with one question at a time (numbers, priorities, v1 boundary), and writes 02-requirements.md with acceptance criteria and traceability back to the concept. Use this whenever the user wants requirements, an SRS, "what must the system do", acceptance criteria, NFRs/SLOs, a v1 scope cut, or says the concept is ready and asks for the next step — even if they never say "requirements". It states WHAT the system must do and HOW WELL, never how it is built.
---

# Requirements

Take the concept document and produce **one file**: a numbered, testable statement of what the system must do and how well, precise enough that the next stage (`high-level-design`) can be judged against it and the last stage (`tasks`) can be traced to it. The concept said *what we'd build and why*; this step pins down *what exactly must be true when it is built*.

Be a rigorous editor, not a stenographer. Concepts are vague on purpose; the value of this step is exposing what is still undecided (a missing number, two requirements that contradict, a "must" that is really a wish) while it is cheap to fix. Equally, don't invent precision: a number nobody can justify is worse than an honest "assumed, validate in pilot".

## Who does what
The main agent is assumed to be a strong frontier reasoning model (Opus-class) and owns the judgment: deriving requirements from the concept, spotting gaps and conflicts, choosing priorities and targets, the interview. Sub-agents only gather evidence (typical load of comparable products, legal or compliance duties, vendor limits) and never decide a requirement. Treat the steps as a shape, not a checklist: compress what adds nothing for this system, go deeper where it is risky.

## Boundary: requirements vs. concept vs. design
| Concept (done) | Requirements (this step) | Design (later, do not do here) |
|---|---|---|
| Problem, users, verdict, approach style | What the system shall do, observable from outside; how well (with numbers); given constraints | Components, technologies, APIs, data models, algorithms, diagrams |
| Order-of-magnitude scale | Load profile and targets with a stated basis | Capacity plans, sizing, caching/sharding |
| "Fast", "secure", "cheap" | "p95 reply start ≤ 3 s", "no secret leaves the tenant", "≤ $X per active user per month" | How those are achieved |

Rules of thumb:
- A requirement says *what* is true, not *how*. "Shall" + subject + observable behaviour + measure. Solution words (database, queue, framework, microservice) don't belong, unless the **user** imposed them — then it is a *constraint*, recorded with its source.
- If an idea is useful only to an implementer, don't delete it: put it in **Deferred to design** (`→ high-level-design: …`), one line, like the concept stage does.
- Don't re-argue the concept. If the requirements work shows the concept is wrong or incomplete, say so plainly, record it as a finding, and let the developer decide whether to go back (`/zkit:concepting`) — never silently bend a requirement around it.

## Workflow

### 1. Locate and read the inputs
Find the zkit docs folder: default `docs/zkit/`; check the project's `AGENTS.md` (or `CLAUDE.md`) for a line naming another folder for zkit documents; a path in the user's request wins over both. Read `01-concept.md`, `decisions.md` and `index.md` there. Note the concept's **verdict**, first-version scope, success criteria, open questions, risks and the "Deferred to design → requirements" items — those are your starting list.

- No concept document: say so and offer two options — run `/zkit:concepting` first (recommended for anything non-trivial), or do a short intake (three or four questions: who, what job, scale, constraints) and mark the document "no concept behind it". Don't fabricate a concept.
- Verdict is **Don't build** or **Buy or reuse**: say that requirements for building aren't warranted; offer instead requirements for the *selection* of the thing to adopt, if the developer wants them.
- Verdict is **Validate first**: write requirements for the recommended approach's first version anyway, but list the validation gates from the concept as *preconditions* at the top, so nobody mistakes the document for a go decision.
- Superseded decisions (`superseded by D-n`) are history; take requirements only from the current ones.
- `02-requirements.md` already exists: run the check from step 5 first. If it reports that the concept is newer, the existing requirements may be stale; list what changed in the concept before revising.

### 2. Draft from the concept — before asking anything
Do the work you can do alone, so the developer reviews instead of authors:
- Derive candidate **functional requirements** from the system concept's capabilities, main scenario and first-version scope, each with the section or decision it came from.
- Derive **non-functional requirements** from "what matters most", risks and success criteria. Walk the quality areas that apply — performance, availability and reliability, security and privacy, cost, scalability, operability (monitoring, deploy, recovery), usability, compliance and legal, data retention, portability — and say explicitly which you skipped and why.
- Pull **constraints** the developer already gave (budget, team, deadline, banned or mandated tech).
- Sketch a **load profile**: users, volume, growth, peaks — as order-of-magnitude assumptions with stated basis.
- Tag every item **known** (said by the user or found in a source), **derived** (follows from the concept) or **assumed** (your proposal).
- Check the draft against the concept: every success criterion and in-scope capability should map to at least one requirement, and every requirement should map back to something — an orphan means either invented scope or a missing concept item.

### 3. Close the gaps — one question at a time
Ask about the gaps that change the outcome most: a number you can't derive (latency, volume, budget per user), a priority fork (is this must-have for v1?), a conflict between two requirements, a boundary between v1 and later. One question per turn, **2-4 concrete options with your recommended one first, marked "(Recommended)", and a one-line reason**; use an interactive question tool (e.g. AskUserQuestion) if available, plain text otherwise. For numbers, offer concrete values with the reasoning, not "how fast do you want it?". When the developer is unsure or says "you decide", take your recommendation and mark it *assumed*. Skip questions whose answer wouldn't change a requirement. Check in before closing ("I think the list is complete — anything missing before I write it up?"); the developer can end the loop at any time.

When a figure or a fact needs evidence (what do comparable systems achieve, what does a legal duty actually require, what is a vendor's real limit, what does a cost really come to), use the `research` skill (`/zkit:research`): state your opinion — *recommended / optional / not needed, because …* — and, if the developer agrees, let it run the sub-agents in the background while you keep interviewing. Cite its reports as `[R-n]` next to the requirement or assumption they support; a target backed by a report can move from *assumed* to *derived* or *known*. An open research question that blocks a number becomes a precondition or an open question in the document.

### 4. Make each requirement good
A requirement earns its place by being checkable. For every one:
- **Atomic and unambiguous:** one behaviour per requirement; split "and"; replace "fast", "secure", "scalable", "user-friendly", "etc." with a measure or delete.
- **Testable:** an acceptance criterion a stranger could run or inspect — observable condition, number, or the evidence that proves it. A requirement you can't verify isn't a requirement yet; either sharpen it or move it to open questions.
- **Prioritized (MoSCoW):** Must / Should / Could for v1, plus **Won't (v1)** for things deliberately postponed — recorded so that "not now" doesn't later look like "forgotten". If more than about a third are Must, the v1 scope is probably too big; say so.
- **Traced:** source (concept section, decision `D-n`, interview answer) and evidence tag. Targets that are *assumed* get a way to validate them (pilot, measurement, interview).
- **Consistent:** look for pairs that can't both hold (cheap vs. independently verified results, instant vs. human approval) and surface them as an explicit trade-off question instead of picking silently.
- **Stable IDs:** `FR-n` functional, `NFR-n` non-functional (with a category), `C-n` constraints. IDs never get reused or renumbered on revision; dropped ones are marked withdrawn. Later stages and tasks link to them.

### 5. Check consistency with the concept — before declaring it done
The two documents must agree, and agreement is verified, not asserted. Two checks, in this order:

1. **Mechanical:** run `python3 <skill-dir>/scripts/check_requirements.py <zkit-docs-folder>` (stdlib only; exit code 1 on errors). It checks the things a script can: IDs unique, every row has priority, acceptance, source and basis; header counts equal actual counts; every cited `D-n` exists in `decisions.md` and isn't superseded; cited concept sections exist; every requirement appears in the traceability table and nothing there points to a missing ID; the concept isn't newer than the date the requirements are based on; a *Validate first* verdict has preconditions; no solution words outside Constraints; Must share ≤ 40% (a warning). Fix every ERROR. For each WARN, fix it or write one line in the document saying why it stays (e.g. why Must is high). Don't edit the script's findings away by weakening the document's claims — fix the cause.
2. **Semantic:** a script can't tell that a requirement contradicts the concept in meaning. Spawn one fresh reviewer sub-agent (it must not have written the document; give it only the paths of `01-concept.md`, `decisions.md` and `02-requirements.md`) with the brief in `references/consistency-review.md`. It returns a table of findings; you judge each one (it is evidence, not a verdict): fix the requirements, or, when the requirement is right and the concept is wrong or vague, record it under *Conflicts and open questions* as a concept issue for the developer to take back to `/zkit:concepting` — don't rewrite the concept on your own. Both documents are living: when the developer decides how a contradiction resolves, update whichever side is wrong (the concept too, with a dated "Правка/Revision" line near its top, matching `Changes since previous version` in spirit, plus a new `D-n` in `decisions.md`), then re-run both checks. Ask the developer with plain-language context (a concrete example of what goes wrong, what each option means for them), because they may not share your jargon. Without sub-agents, do the same pass yourself with that file's list, re-reading the concept rather than relying on memory.

Then record the outcome in the document's *Consistency check* section: date, script result, reviewer verdict, what was fixed, what stays open. Re-run both checks after any change you make because of them.

### 6. Write the file
Write a single Markdown file in the developer's language (the concept's language, by default) as `02-requirements.md` in the zkit docs folder (create it if missing), using `references/requirements-template.md` — read it before writing. If the file exists, read it and revise instead of overwriting: keep what still holds, keep IDs, and add a short `## Changes since previous version` note on top. If the concept changed after the requirements were written (compare dates/versions), say which requirements may be stale. Set the header's `Based on` line to the concept's actual date: the script uses it to detect drift later.

Also update, in the same folder:
- `index.md`: add or refresh **only your own row** (`#`, file as link, stage, status, date, one-line summary — for requirements: counts and the main open item); leave other stages' rows alone.
- `decisions.md`: append `### D-<n>: <decision>` entries (continue the existing numbering) for decisions made here that change what gets built — a priority cut, a chosen target, a trade-off resolved — each with alternatives, why, date.

Then give a short summary in chat: the consistency-check result, counts (Must/Should/Could), the 2-3 riskiest assumed targets, any conflict or concept issue found, and what is still open; offer another question round if gaps remain; name the next step (`high-level-design`). Don't paste the document.

## Quality bar
- Every requirement is atomic, testable and traced; no solution words unless a user-imposed constraint with a source.
- Every NFR has a number (or a stated reason it can't yet) and a basis tag; assumed ones say how to validate.
- Concept ↔ requirements both ways and *checked*: the script passes without errors and the reviewer's findings are resolved or recorded; nothing in v1 scope uncovered, no orphan requirements.
- Scope is explicit: Must/Should/Could for v1 and a visible Won't list.
- Conflicts and concept problems are surfaced, not smoothed over.
- Short beats long: tables over prose, roughly 2,000-3,500 words; past ~60 requirements, the v1 is likely too big or the requirements are really design.
- Stop at requirements: no diagrams, data models, API shapes, technology choices, task breakdown or code.
