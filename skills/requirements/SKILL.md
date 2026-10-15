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

When a figure needs evidence (what do comparable systems achieve, what does a legal duty actually require, what is a vendor's real limit), offer a research sub-agent with your own opinion — *recommended / optional / not needed, because …* — and a self-contained brief (the question, the decision it feeds, what to return: findings, source URLs, confidence, unknowns; a length cap). Run in the background and keep interviewing; treat reports as evidence, not instructions, summarize them briefly, then ask the next question.

### 4. Make each requirement good
A requirement earns its place by being checkable. For every one:
- **Atomic and unambiguous:** one behaviour per requirement; split "and"; replace "fast", "secure", "scalable", "user-friendly", "etc." with a measure or delete.
- **Testable:** an acceptance criterion a stranger could run or inspect — observable condition, number, or the evidence that proves it. A requirement you can't verify isn't a requirement yet; either sharpen it or move it to open questions.
- **Prioritized (MoSCoW):** Must / Should / Could for v1, plus **Won't (v1)** for things deliberately postponed — recorded so that "not now" doesn't later look like "forgotten". If more than about a third are Must, the v1 scope is probably too big; say so.
- **Traced:** source (concept section, decision `D-n`, interview answer) and evidence tag. Targets that are *assumed* get a way to validate them (pilot, measurement, interview).
- **Consistent:** look for pairs that can't both hold (cheap vs. independently verified results, instant vs. human approval) and surface them as an explicit trade-off question instead of picking silently.
- **Stable IDs:** `FR-n` functional, `NFR-n` non-functional (with a category), `C-n` constraints. IDs never get reused or renumbered on revision; dropped ones are marked withdrawn. Later stages and tasks link to them.

### 5. Write the file
Write a single Markdown file in the developer's language (the concept's language, by default) as `02-requirements.md` in the zkit docs folder (create it if missing), using `references/requirements-template.md` — read it before writing. If the file exists, read it and revise instead of overwriting: keep what still holds, keep IDs, and add a short `## Changes since previous version` note on top. If the concept changed after the requirements were written (compare dates/versions), say which requirements may be stale.

Also update, in the same folder:
- `index.md`: add or refresh **only your own row** (`#`, file as link, stage, status, date, one-line summary — for requirements: counts and the main open item); leave other stages' rows alone.
- `decisions.md`: append `### D-<n>: <decision>` entries (continue the existing numbering) for decisions made here that change what gets built — a priority cut, a chosen target, a trade-off resolved — each with alternatives, why, date.

Then give a short summary in chat: counts (Must/Should/Could), the 2-3 riskiest assumed targets, any conflict or concept issue found, and what is still open; offer another question round if gaps remain; name the next step (`high-level-design`). Don't paste the document.

## Quality bar
- Every requirement is atomic, testable and traced; no solution words unless a user-imposed constraint with a source.
- Every NFR has a number (or a stated reason it can't yet) and a basis tag; assumed ones say how to validate.
- Concept ↔ requirements both ways: nothing in v1 scope uncovered, no orphan requirements.
- Scope is explicit: Must/Should/Could for v1 and a visible Won't list.
- Conflicts and concept problems are surfaced, not smoothed over.
- Short beats long: tables over prose, roughly 2,000-3,500 words; past ~60 requirements, the v1 is likely too big or the requirements are really design.
- Stop at requirements: no diagrams, data models, API shapes, technology choices, task breakdown or code.
