---
name: flow
description: Entry point and router for the whole zkit design chain (concepting, requirements, resource-math, contracts, data, architecture, mechanics, resilience, roadmap). Looks at docs/zkit/<project>/, works out which steps exist, which are agreed or stale, runs the cross-document link check, says what comes next and starts that step's skill. Use this whenever the user says "continue the project", "what's next", "where did we stop", "start a new project/idea with zkit", "run the whole chain", "from idea to roadmap", or names a project under docs/zkit without naming a step - even if they never say "flow".
---

# Flow

The router for zkit (`/zkit:flow`). It owns no design logic: each step's skill does its own work and interviews. This skill only answers **"where is this project, and what is the next step?"** and then hands over, so the developer never has to remember the order or run the checks by hand.

## The order
`concepting` → `requirements` → `resource-math` → `ux` (optional) → `contracts` → `data` → `architecture` → `mechanics` → `resilience` → `roadmap` (helper at any point: `research`).

| Step | File in `docs/zkit/<project>/` |
|---|---|
| concepting | `concept.md` |
| requirements | `requirements.md` |
| resource-math | `resource-math.md` + `resource-math/model.py` |
| ux (optional) | `ux.md`, or a decision `D-n: ux: not applicable - <reason>` |
| contracts | `contracts.md` + `contracts/` |
| data | `data.md` |
| architecture | `architecture.md` |
| mechanics | `mechanics.md` + `mechanics/model_*.py` |
| resilience | `resilience.md` + `resilience/model.py` |
| roadmap | `roadmap.md` + `roadmap/epics/` (an `epic.md` per epic, a file per task) |

## Project layout
One layout for every step, so a project folder stays readable at 200+ files. Only the step documents and `decisions.md` live in the project root; everything else sits in a folder:

```
docs/zkit/<project>/
  concept.md  requirements.md  resource-math.md  ux.md  contracts.md  data.md
  architecture.md  mechanics.md  resilience.md  roadmap.md  decisions.md

  resource-math/   model.py
  contracts/       X-n / I-n files, schemas/
  mechanics/       model_*.py, supporting files
  resilience/      model.py
  roadmap/         epics/EP-n-<slug>/epic.md, epics/EP-n-<slug>/tasks/TK-n-<slug>.md
  diagrams/        *.mmd
  research/        R-n-<slug>.md, and R-n-<slug>/ next to it for that report's probes, measurements and raw data
  checks/<step>/   reviewer tables, checker output and verification scripts worth keeping (review-<date>.md, ...)
  appendix/        anything outside the chain (a domain model, scenarios, imported pre-zkit material); its header names the step it supports
```
- The root holds `<step>.md` only; a step's other files go in the folder with the step's name (`resource-math.md` + `resource-math/`).
- Evidence sits next to its report: `research/R-5-<slug>.md` + `research/R-5-<slug>/`. No top-level `measurements/` or `reference/`.
- Ids in file names are written like in the documents (`X-1-cli.md`, `TK-1-<slug>.md`).
- A step document is a summary plus tables, near its target length (see the step's template); detail goes into the step's folder.
- `scripts/layout.py <project-dir>` warns about root entries outside this list and documents over twice their target; `--migrate` shows (and with `--apply` does) the mechanical moves of an older project: models into their step folder, `validation/<step>-*` into `checks/<step>/`.

## Workflow
1. **Find the project.** List `docs/zkit/*/`. One project → use it. Several → ask which (one question). None, or a new idea → start `concepting` with the idea; project name = short kebab-case, ask only if it is not obvious.
2. **Read the state.** For each file in the table: missing / `Status: draft` / `Status: agreed` (the line in the header). Also note the `Based on:` dates: a document older than the one it is based on is **stale**.
3. **Run the checks** that exist: `python3 <zkit>/skills/requirements/scripts/link_docs.py docs/zkit/<project>` and the step's own `check_<step>.py <project>` for every document present. `link_docs.py` also verifies ids against the registry `IDS` in `flow/scripts/ids.py`, which every `check_<step>.py` imports too (one owner document per prefix: `FR`/`NFR`/`C`/`P`/`Q` requirements, `A`/`L` resource-math, `U`/`J` ux, `X` contracts, `E`/`M` data, `B`/`I`/`S` architecture, `MC` mechanics, `F`/`T`/`O`/`DR`/`RA`/`RL` resilience, `PH`/`G`/`EP`/`TK` roadmap, `D` decisions, `R` research): every cited id must be defined by its owner, every `P-n` should be planned in the roadmap, and local lists (findings, gaps) are numbered plainly, never with an id-like label; it exits 1 on errors. For a project written before the registry (zkit < 0.2.7) offer `link_docs.py <project> --fix-ids`: it renames the old Cyrillic conflict labels `К-n` to `Q-n` everywhere; the remaining errors (local lists numbered with a registry prefix, ids cited but never defined) need a decision per item, so list them for the developer instead of fixing silently. An old roadmap schedule block is a WARN: `check_roadmap.py --update` refreshes it. Also `python3 <zkit>/skills/flow/scripts/layout.py docs/zkit/<project>`: report its WARNs and offer `--migrate` for an older project (apply only with the developer's yes). Report ERRORs; do not fix other steps' content here.
4. **Say where we are** in at most five lines, starting with a step counter `Step k/10` (k = steps agreed + 1; `ux: not applicable` counts as agreed): done steps, the first step that is missing/draft/stale, and why it is the next one. Skipped steps are allowed only if the developer says so; record that as a decision `D-n`. `ux` is the exception: it is optional by design, so after `resource-math` hand over to it, and its skill records `ux: not applicable` itself when the system has no human-facing surface.
5. **Hand over.** Start the next step's skill via the Skill tool, passing the project name. When that skill finishes, return here for step 2 only if the developer wants to keep going; do not auto-run several steps in a row, because every step needs the developer's answers.

## Rules
- A stale or draft earlier document comes before a new step: later steps inherit its errors.
- If a later step's finding contradicts an earlier document, the earlier step's skill fixes it (living documents: dated "Правка" line + `D-n`), not this one.
- Never write step documents yourself and never duplicate a step's method here.
