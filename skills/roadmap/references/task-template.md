# Epic and task files

Divide and conquer: `roadmap.md` is the index (tables, hours, dependencies, the computed schedule); the detail of the work lives in one file per epic and one file per task, next to it:

```
docs/zkit/<project>/
  roadmap.md
  roadmap/epics/
    EP-1-<slug>/
      epic.md
      tasks/
        TK-1-<slug>.md
        TK-2-<slug>.md
    EP-2-<slug>/
      epic.md            (no tasks/ yet: detailed after the gate)
```

Ids in file names match the ids in `roadmap.md`; a task's folder is the epic named in its `Epic` column. The checker reads the headings below (any of the listed words counts, in the developer's language) and fails on a missing file or section.

## Epic file (`epic.md`)
````markdown
# EP-<n>: <epic name>

**Phase:** PH-<n> · **Hours (best / expected / worst):** from roadmap.md · **Depends on:** EP-/TK- ids

## Goal
One paragraph: what is true when the epic is finished, and why it exists (the requirement, limit, risk or drill behind it).

## Boundaries
In: what belongs to this epic. Out: what looks related but belongs elsewhere (name the epic or step that owns it).

## Tasks
The order and the reason for the split, one line per task `TK-n: what it delivers`. Epics without tasks yet: what will be split after which gate.
````

## Task file (`TK-<n>-<slug>.md`)
Written so that a developer or an agent can start without asking anything. 4-16 expected hours; if the description needs more, split the task.

````markdown
# TK-<n>: <task name>

**Epic:** EP-<n> · **Phase:** PH-<n> · **Depends on:** TK- ids · **Estimate (best / expected / worst):** from roadmap.md, with the reasons for the range

## Goal
What this task delivers and why it is needed now: the requirement, limit, drill or decision it serves (ids).

## What must be done
Numbered steps in the order to do them, concrete enough to act on: what to build, measure or write, with which inputs, in what form the result is left. No code, no technology the architecture did not choose.

## Boundaries
- In: what this task covers.
- Out: what it must not touch, and which task or epic does it instead.
- Interfaces: what it consumes from earlier tasks (ids) and what it leaves for later ones, so the task can be done and checked alone.

## Inputs
Documents and ids to read first: `FR-`/`NFR-` requirements, limits `L-`, contracts `X-`, entities `E-`, mechanisms `MC-`, drills `DR-`, decisions `D-`.

## Acceptance
The checks that prove it is done, each one something another person can run or inspect (a measurement within a limit, a scenario walked, a drill passed, a test green). The same criterion as the `Acceptance` cell of `roadmap.md`, in full.

## Risks and notes
What can go wrong or take longer, what to do then, and anything to hand over to the next task.
````

Rules for the split:
- **One reason to exist.** A task delivers one thing someone can check; "and" in its name usually means two tasks.
- **Clear boundaries.** Two tasks never own the same piece of work; what is shared is a task of its own that both depend on.
- **Small and logical.** Split along the seams of the architecture and the proof work (a contract, an entity, a mechanism, a drill), not by layers of effort ("design / code / test").
- **Independent where possible.** Prefer tasks that can be finished, checked and shown on their own; the `Depends` column carries the rest.
