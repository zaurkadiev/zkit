# Resource math template

Aim for roughly 1,500-3,000 words around the model, at most ~20 assumptions. Tables over prose. Sections in this order; drop one only if irrelevant and say so in one line. Products appear only as sources of numbers. No architecture, no data formats, no algorithms.

```markdown
# <Name> — Resource math

> **Links:** [concept](concept.md) · [requirements](requirements.md) · [decisions](decisions.md) · [model](resource_model.py)
> **Status:** draft / agreed (agreed only when the clarity gate passes, SKILL.md step 6) · **Date:** <date> · **Based on:** [requirements.md](requirements.md) (<requirements' own date>)
> **Verdict:** fits / fits with changes / does not fit
> **Counts:** <n> A · <n> L   (the checker compares these with resource_model.py)

## 1. Summary
The verdict in ≤5 sentences: what was tested, does it fit in the expected and the worst scenario, the 2-3 assumptions that decide it, what the design must respect.

## 2. Workload
The units that arrive (users, organizations, agents, tasks, messages, frames, samples), how many, how often, how bursty, how they combine. Where each figure comes from (requirement, concept §n, assumption A-n).

## 3. Resources in play
| Resource | Binds? | Why / why not |
|---|---|---|
| e.g. memory per active environment | yes | sets servers per organization, therefore cost |

## 4. Assumptions
| ID | Assumption | Unit | Best | Expected | Worst | Evidence | Source | Validation |
|---|---|---|---|---|---|---|---|---|
| A-1 | … | … | … | … | … | known / measured / assumed | requirement id, [R-n](research/R-n-slug.md), "developer" | cheapest check for an *assumed* one (measurement, spike, pilot) |

`best` is the value most favourable for the limits, `worst` the least favourable. Values here must equal resource_model.py (the checker compares ids and counts).

## 5. Model
Formulas in words, one line each (the code is in `resource_model.py`; comment names the resource). Then the generated block - never type numbers into it, run `check_resource_math.py <project-dir> --update`:

<!-- model:begin -->
<!-- model:end -->

## 6. Limits and verdicts
| ID | Limit | Requirement | Verdict (expected / worst) | Accepted by |
|---|---|---|---|---|
| L-1 | … | NFR-… / C-… | fits / fits with changes / does not fit | `D-<n>` if it fails and the failure is accepted, else — |

Numeric Must requirements the math cannot test are listed here as **not resource-bound** with the reason.

## 7. Consequences for the design
Ceilings and unit costs the architecture must respect (per part, per unit, per call), what to measure first and why (the largest uncertainty × the verdict), where the first spike belongs. Constraints, not a design. Each line tagged `→ architecture: …`, `→ contracts: …`, `→ data: …`, `→ roadmap: spike …`.

## 8. Risks, assumptions and open questions
Ranked. Requirements issues found by the math (impossible, conflicting, missing) with the decision taken or pending.

## 9. Consistency check
Date; `check_resource_math.py` result (errors / warnings left and why); verdict of the independent reviewer; what was fixed; what stays open.

## Sources
Numbered URLs; delegated findings link to `[R-n]` reports with their confidence.
```
