---
name: chain
description: Entry point and router for the whole zkit design chain (concepting, requirements, resource-math, contracts, data, architecture, mechanics, resilience, roadmap). Looks at docs/zkit/<project>/, works out which steps exist, which are agreed or stale, runs the cross-document link check, says what comes next and starts that step's skill. Use this whenever the user says "continue the project", "what's next", "where did we stop", "start a new project/idea with zkit", "run the whole chain", "from idea to roadmap", or names a project under docs/zkit without naming a step - even if they never say "chain".
---

# Chain

The router for zkit. It owns no design logic: each step's skill does its own work and interviews. This skill only answers **"where is this project, and what is the next step?"** and then hands over, so the developer never has to remember the order or run the checks by hand.

## The order
`concepting` → `requirements` → `resource-math` → `contracts` → `data` → `architecture` → `mechanics` → `resilience` → `roadmap` (helper at any point: `research`).

| Step | File in `docs/zkit/<project>/` |
|---|---|
| concepting | `concept.md` |
| requirements | `requirements.md` |
| resource-math | `resource-math.md` + `resource_model.py` |
| contracts | `contracts.md` + `contracts/` |
| data | `data.md` |
| architecture | `architecture.md` |
| mechanics | `mechanics.md` + `mechanics/model_*.py` |
| resilience | `resilience.md` + `resilience_model.py` |
| roadmap | `roadmap.md` |

## Workflow
1. **Find the project.** List `docs/zkit/*/`. One project → use it. Several → ask which (one question). None, or a new idea → start `concepting` with the idea; project name = short kebab-case, ask only if it is not obvious.
2. **Read the state.** For each file in the table: missing / `Status: draft` / `Status: agreed` (the line in the header). Also note the `Based on:` dates: a document older than the one it is based on is **stale**.
3. **Run the checks** that exist: `python3 <zkit>/skills/requirements/scripts/link_docs.py docs/zkit/<project>` and the step's own `check_<step>.py <project>` for every document present. Report ERRORs; do not fix other steps' content here.
4. **Say where we are** in at most five lines: done steps, the first step that is missing/draft/stale, and why it is the next one. Skipped steps are allowed only if the developer says so; record that as a decision `D-n`.
5. **Hand over.** Start the next step's skill via the Skill tool, passing the project name. When that skill finishes, return here for step 2 only if the developer wants to keep going; do not auto-run several steps in a row, because every step needs the developer's answers.

## Rules
- A stale or draft earlier document comes before a new step: later steps inherit its errors.
- If a later step's finding contradicts an earlier document, the earlier step's skill fixes it (living documents: dated "Правка" line + `D-n`), not this one.
- Never write step documents yourself and never duplicate a step's method here.
