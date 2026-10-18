---
name: concepting
description: Turn a vague software or system idea into one critical, researched concept document. Interviews the developer until the intent is clear, then weighs the idea fairly (strengths and weaknesses across problem, users, difficulty, competitors, alternative approaches), researches prior art on the web, compares alternative approaches at the level of overall shape, and writes a single concept document (no detailed design). Use this whenever the user floats a half-formed idea ("I want to build...", "what if we made...", "is it worth building X", "help me think through a system for..."), asks to clarify, validate, critique or shape a product/system/tool idea, or wants a concept/spec/one-pager BEFORE any implementation planning — even if they never say "concept".
---

# Concepting

Take a vague idea and produce **one file**: a concept document that says whether the thing deserves to exist, which design approach is the most defensible, and — most importantly — **what exactly the system we'd build is**: a clear conceptual description of it (purpose, boundaries, main parts, how it behaves, how people use it), so a reader can picture it and the next step (planning) can start from it. This is the step *before* planning and coding, so the output is a decision aid, not a task list.

Be a rigorous but fair critic. Vague ideas usually survive because nobody attacked them — but blind negativity is as useless as flattery. Name what is genuinely strong about the idea as clearly as what is weak. A concept that says "don't build this" or "buy X instead" is a successful result, not a failure — say it plainly if the evidence points there.

## Who does what
This skill assumes the main agent is a strong frontier reasoning model (Opus-class) and is written to lean on its judgment rather than script it. The main agent owns everything that needs reasoning and taste: the interview, the critique, comparing approaches, the recommendation and the verdict. Delegate only evidence-gathering to sub-agents (which may run on a cheaper or faster model) and never the conclusions drawn from it — re-read their findings critically and make the call yourself. Treat the steps below as a shape to follow, not a checklist to fill mechanically: skip or compress a step when it adds nothing for this idea, and go deeper where the idea is risky or unclear.

## Boundary: concept vs. design
`concepting` answers **what, for whom, why, and in what overall shape**. Everything about **how it is built** belongs to the later design stages of the zkit chain (`requirements` → `resource-math` → `ux` (optional) → `contracts` → `data` → `architecture` → `mechanics` → `resilience` → `roadmap`). Keeping this wall clean matters: concept decisions are cheap to reverse and made on thin evidence, design decisions are expensive and need numbers. Mixing them makes the concept look more certain than it is and buries the real question — whether to build at all.

| Belongs in the concept | Belongs to design (do not do here) |
|---|---|
| Problem, users, intent, success criteria | Functional / non-functional requirements with numbers and estimates |
| Landscape, strengths, weaknesses, verdict | API, data model, schemas, algorithms |
| Candidate approaches compared by *style* and trade-off (build vs. buy, thin service vs. broker-based, …) | Exact components, technologies, versions, configs, pricing tiers, queue/lock/cache tricks |
| System in plain words: purpose, main scenario, few main parts, boundaries | Diagrams (C4, sequence, ER), scaling, sharding, caching, capacity plans |
| Order-of-magnitude scale and effort | Precise estimates, SLOs, cost models |
| Open questions and next steps | Roadmap, task breakdown, code |

Rules of thumb:
- Name a specific technology only when the choice *is* the concept (e.g. "use an existing SaaS" vs. "build"), or when it's a real competitor.
- If a sentence is useful only to someone implementing, don't delete it silently: move it to a **"Deferred to design"** list at the end of the document (one line each, tagged with the stage that should pick it up, e.g. `→ architecture: outbox pattern for delivery guarantees`). Nothing is lost and the concept stays clean.
- Do not smuggle design in through "recommended approach" or "System concept": they describe shape and trade-offs, not mechanisms.
- Target length: roughly 1,500-2,500 words. Longer usually means you're designing.

## Workflow

### 1. Clarify together — the agent brings answers, not just questions
**Progress counter.** Prefix every question with `[concepting Q n/12 · gaps c/T closed]` (e.g. `[concepting Q3/12 · gaps 4/7 closed]`): n = questions asked so far out of the step budget of 12 (see Stopping rules); T = the blocking gaps found so far (the ones the clarity gate names); c = how many of them are closed or turned into `assumed`. c/T is the real progress, n/12 only shows budget spent. When T changes (new conflict, gap closed by research, developer ends the loop), say it in one line (`T 7→8: new conflict`), never silently. Do not pad questions; the loop still ends on clarity or budget.

**Context for every question and answer.** Before asking, give the developer enough to decide without re-reading the document: what the question is about, why it matters here (which requirement, limit or risk it moves), what each option changes, and one concrete example of what goes wrong. When the answer comes in, say in a line or two what is now decided and what it affects downstream. When a flow, structure or trade-off is easier to see than to read, add a small diagram (up to about 12 nodes) in the message text before the question, never inside the option labels. Use a ```mermaid block (flowchart, sequence or state) only if the client renders it (the developer said so, or you are publishing to a markdown/artifact viewer); in a plain terminal, or when unsure, draw the same thing as a symbolic ASCII schema (boxes, arrows, a short legend) in a code block.

**Stopping rules.** Budget: 12 questions per step (the 12 in the counter). Going over needs a one-line reason and the developer's yes. Freeze the list of blocking gaps (the ones the clarity gate names) once the draft exists; a new blocking gap found later is added explicitly and spends budget. Ask only if a different answer would change a number, priority, verdict or decision, and only about blocking gaps; every other gap becomes `assumed` with a way to validate it, without a question. Every question must close a gap or turn it into `assumed`, so the open count only goes down. At question 8 say: `k = T - c gaps left; I suggest accepting my recommendations and writing it up - continue or close?` When the budget is spent, remaining gaps become `assumed` unless the developer extends it.

The idea lives in the developer's head, but clarity is a joint job: don't hand the developer a questionnaire. First do the thinking you can do alone — restate the idea in 2-4 sentences, infer the most plausible intent, audience and scope, and run a quick search if a fact would sharpen a question (e.g. "does a standard tool for this already exist?").

Then run an **iterative loop, one question at a time** (most decision-changing first) — batches overwhelm the developer and make them skim. Give **2-4 concrete options with your recommended one first, marked "(Recommended)", and a one-line reason**; if an interactive question tool (e.g. AskUserQuestion) is available, use it, otherwise offer the same options in plain text. The developer can pick one, correct it, or answer freely — this is faster than answering from scratch and exposes your reasoning for them to challenge. When the developer is unsure or says "you decide", take your recommendation, mark it *assumed*, and move on. Fold the answer in and ask the next question. "Everyone" is not an answer to "for whom": say so, propose one first segment with a reason, and record the rest as later — a vague audience makes competitors and risks impossible to judge. If research shows the idea already exists, say it plainly and turn the next question into "where do we differ", not "what do we build". If the developer changes what the product is mid-interview, name which earlier answers and decisions it supersedes, re-offer research for what is now uncovered (old findings may not transfer), and revise the concept file instead of patching it; mark the old entries' status "заменено / superseded by D-n". Keep going until you and the developer agree there's enough clarity — check in explicitly ("I think I understand X, Y, Z — anything else before I go deeper?") — and let them end the loop at any time. The question budget is in Stopping rules; don't ask questions whose answers wouldn't change the design or verdict.

Cover these areas (skip what's already answered):
- **Intent:** real pain, curiosity, learning, business, portfolio? What does success look like?
- **For whom:** who will use it, and is that the developer themself?
- **For what:** the concrete job it does, and what happens today without it.
- **Difficulty & resources:** skills, time, budget, team size, deadline, tech preferences or bans.
- **Constraints:** scale, privacy, platform, integrations, must-reuse systems.
- **Alternatives they know:** tools tried or rejected, and why.

**Clarity gate** for ending the interview (the blocking gaps for the stopping rules): the intent and what success looks like are stated; one first user segment is named (not "everyone"); the job and what happens today without it are described; at least one existing alternative is named, or a search shows none; the main constraints (time, budget, platform, scale) have an answer or an `assumed`; the main risks are listed. When all hold, check in and move on to step 2.

Questions continue later: when research or design surfaces a fork, bring it back with your recommendation. Record every question with its answer, your recommendation and its status — they go into the concept file's *Intent & Questions* section.

#### Offering deeper research via sub-agents
During the interview, when a sub-topic is open and would materially change the concept (a competitor niche, a technology's real limits, a pattern's fit, market size, legal constraints), **offer to delegate it** instead of researching inline or guessing, using the `research` skill (`/zkit:research`). Always state your own opinion: *"Research recommended / optional / not needed — because …"* so the developer can just agree. Skip the offer for trivia you can settle in one search. The skill runs the sub-agents in the background, verifies and saves the report to `docs/zkit/research/`; you keep interviewing meanwhile, then summarize what was found and how it changes your recommendations, cite it in the concept as a link, `[R-n](research/R-n-<slug>.md)`, next to the claim it supports and in the Sources section, and ask the next question.

### 2. Define the problem and users
- The problem in one sentence, from the user's side, not the solution's side.
- Who has it, how often, how painful, and what they do today (including "nothing" and "a spreadsheet").
- Primary user vs. secondary users vs. people who explicitly are *not* the target.
- Evidence level for each claim: **known** (user said / source found), **assumed**, or **unknown**. Unknowns that could kill the idea go to the risks section.

### 3. Research — don't answer from memory
Use web search and fetch actively. Competitor and prior-art landscapes change fast, and memory is where plausible-sounding fiction comes from.
- Find direct competitors, adjacent tools, open-source alternatives, and the "just use X" incumbents (including DIY with existing tools).
- For each: what it does, rough price level and licence, where it's strong, where it's weak, last activity (a dead project is a signal too).
- Look for failed attempts and why they failed, and for the standard industry approach to the technical problem.
- Run independent searches in parallel; for a sub-topic that needs a deep dive, use the sub-agent offer from step 1. Record the source URL next to every non-obvious claim. For claims the verdict rests on (a competitor already does X, a project is dead, a hard limit exists), open the primary source — the vendor's docs, the repo, the paper — rather than trusting a search snippet or a third-party listicle; say when you couldn't. Pricing is only needed as an order of magnitude (free / tens / thousands per month), so don't spend effort reconciling exact tiers. If search finds nothing, say so — "no competitors found" usually means weak search or no market, so state which you suspect.

### 4. Evaluate the idea — strengths and weaknesses
Weigh it honestly, in both directions:
- **Strengths:** what's genuinely good — real pain, timing, a gap in the landscape, unfair advantage the developer has, a cheap path to a first version. Be specific, not cheerleading.
- **Weaknesses / case against:** problem too rare, incumbent good enough, tiny audience, maintenance burden, platform risk, legal/privacy, hard to reach users.
- **Difficulty:** how hard is it to build and to *run*, for this developer — the hardest 2-3 parts and why.
- **Downsides of the idea itself:** cost, complexity, lock-in, operational and security surface.
- **Pre-mortem:** assume it failed in a year — the three most likely reasons.
- **Verdict:** **Build / Build smaller / Validate first / Buy or reuse / Don't build**, one-sentence reason, and what evidence would change it. Make sure the verdict visibly accounts for the strengths too.

### 5. Explore approaches
Answer "what other ways could this problem be solved?" Produce 2-4 genuinely different options (include non-software or reuse-existing options when they're real contenders); keep each option to a short paragraph at style level, per the boundary above (not one design with cosmetic variants), spanning real axes: build vs. adopt, monolith vs. services, sync vs. event-driven, client-heavy vs. server-heavy, managed service vs. self-hosted, etc. Name relevant design patterns and architectural styles where they actually apply — and say why a pattern fits rather than listing it for decoration. For each option: how it works in a few sentences, what it's good at, what it costs (complexity, money, operational burden, risk), and when it would be the wrong choice. Compare in a table on criteria that matter for *this* idea, then give a clear recommendation and justify it — the developer should never have to pick from a menu without knowing which option you'd choose and why. Prefer the simplest option that meets the real requirements; call out where complexity is speculative.

### 6. Write the concept file
Write a single Markdown file, in the developer's language. It lives in a **project** inside the project's **zkit docs folder**, by default `docs/zkit/` (create it; every zkit skill reads and writes there). A project is one coherent piece of work through the whole chain: the first product is usually `mvp`, a large later feature gets its own project (ask the developer for the name if it isn't obvious from the request; reuse the existing project when the work continues it). Layout, shared by all zkit skills:

```
docs/zkit/
  <project>/                  a project: "mvp", or a big feature (kebab-case name); everything about it lives here
    concept.md
    requirements.md           (later stages add resource-math.md, ux.md, contracts.md, data.md, architecture.md, ... in the same folder)
    decisions.md              ONE file: every decision as an entry `### D-<n>: title`, numbered within the project
    research/R-<n>-<slug>.md  one file per research question, numbered within the project
```

The concept goes to `<project>/concept.md`. The docs folder can be changed: before writing, check the project's `AGENTS.md` (or `CLAUDE.md`) for a line naming another folder for zkit documents, and use it; a path the user names in the request wins over both. If the file already exists, read it and revise it rather than overwriting: keep what still holds and add a short `## Changes since previous version` note at the top. Use the structure in `references/concept-template.md` (read it before writing). There are no index files: the projects are the folders, the documents are the files. Write each key decision as an entry in `<project>/decisions.md` (create it; `<a id="D-<n>"></a>` anchor, `### D-<n>: <decision>`, a `> **Статус:** принято · **Дата:** …` line, alternatives, why; continue the numbering). Documents must link to each other: mention a decision as `D-<n>` and a research report as `[R-<n>]` in the text, then run `python3 <skills-dir>/requirements/scripts/link_docs.py <project-dir>` — it turns those mentions into real links and rebuilds each decision's and report's back-links and the summary table at the top of `decisions.md`. The file must contain a standalone **System concept** section: describe the recommended system as if it already exists — what it is, who uses it and how (a short walk-through of the main scenario), its core capabilities, the few main parts and their responsibilities in plain words, how information moves through them in a few sentences, external dependencies, boundaries (what it deliberately doesn't do), and the two or three qualities that matter most (no numbers or SLOs). A reader who skips everything else should still understand what is to be built. Then give the user a short summary: the verdict, the recommended approach, and the top open questions — and offer another question round if open questions remain, and name the next step in the chain (`requirements`) when the verdict is Build, Build smaller or Validate first. Don't paste the document into chat.

## Quality bar
- Concrete over generic: named competitors, order-of-magnitude numbers, specific failure modes. If a sentence would fit any project, cut or sharpen it.
- Every question asked is recorded with its answer; every assumption is labelled; every researched claim has a source.
- Balanced: strengths and weaknesses both stated with evidence. The recommendation follows from the comparison, and the verdict from the evaluation — a reader should see *why*.
- Scope is explicit: what's in the first version, what's deliberately out.
- Short beats long. A reader should get the verdict in the first screen; detail sits below it.
- Stop at concept, per the boundary above. No diagrams, data models, API sketches, implementation plan, task breakdown or code — those belong to later steps. The system description stays conceptual (what and how it fits together, not file layouts or APIs line by line), but it must be concrete enough to be unambiguous.
