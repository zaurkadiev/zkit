# Resilience template

Aim for roughly 3,000-5,000 words plus the model. Tables over prose. Sections in this order; drop one only if irrelevant and say so in one line. No code, no tasks, no re-design of mechanics.

````markdown
# <Name> — Resilience

> **Links:** [concept](concept.md) · [requirements](requirements.md) · [resource-math](resource-math.md) · [contracts](contracts.md) · [data](data.md) · [architecture](architecture.md) · [mechanics](mechanics.md) · [decisions](decisions.md)
> **Status:** draft / agreed (agreed only when the clarity gate passes, SKILL.md step 6) · **Date:** <date> · **Based on:** requirements.md (<date>), architecture.md (<date>), data.md (<date>), contracts.md (<date>)
> **Counts:** <n> F · <n> T   (the checker compares these with the register)

## 1. Summary
The verdict in ≤5 sentences: do the promised availability, RPO and RTO hold (expected / worst), the worst faults and threats, what the architecture must change, the first drills.

## 2. Faults
| ID | Target | Failure | Severity | Detection | Response | Recovery | Serves | Residual |
|---|---|---|---|---|---|---|---|---|
| F-1 | B-3, E-1 | the node with the database dies | H | O-1, O-4 | fail over to restored node; queue stops, no data written | RTO RL-1, RPO RL-2 | NFR-11 | accepted: D-<n> |

`Target`: ids of parts, interfaces, boundaries, entities (`B-`, `I-`, `X-`, `E-`). `Severity`: H (breaks a Must requirement, money, isolation or data) / M / L. `Detection`: signals from section 4. `Recovery`: the target and the model limit that tests it.

## 3. Threats
| ID | Target | Threat (who, wants what, how) | Severity | Detection | Response | Recovery | Serves | Residual |
|---|---|---|---|---|---|---|---|---|
| T-1 | B-6, X-7 | hostile code in the sandbox tries to reach the host or other tenants | H | O-6 | contained by isolation layer; kill and wipe the environment | — | NFR-9 | accepted: D-<n> |

## 4. Security and isolation design
Trust boundaries (a short list: who trusts whom), where secrets live and who can read them, rotation and revocation, what a compromised part can touch (blast radius), sandbox containment layers, the residual risks and who accepted them.

## 5. Observability
| ID | Signal | Detects | Emitted by | Alert / threshold | Kept for |
|---|---|---|---|---|---|
| O-1 | heartbeat of the platform node | F-1 | B-9 | 2 missed beats → message to the operator | 30 days |

Diagnostics for incidents: what must be in logs and traces to explain a failure afterwards, and the deletion path of personal data in them.

## 6. Drills
| ID | Covers | How | Success criterion | Becomes |
|---|---|---|---|---|
| DR-1 | F-1 | restore the backup on a clean machine, run the smoke scenario | working in ≤ RTO, data age ≤ RPO | roadmap task |

State what a failed drill would look like.

## 7. Assumptions
| ID | Assumption | Unit | Best | Expected | Worst | Evidence | Source | Validation |
|---|---|---|---|---|---|---|---|---|
| RA-1 | node failures per year | 1/year | 0.5 | 1 | 2 | assumed | hoster statistics [R-n](research/R-n-slug.md) | measured in the pilot |

`Evidence`: known / measured / assumed. Values here equal `resilience_model.py` (the checker compares ids).

## 8. Model
Formulas in words (one line each), then the generated block - never type numbers into it, run `check_resilience.py <project-dir> --update`:

<!-- model:begin -->
<!-- model:end -->

## 9. Limits and verdicts
| ID | Limit | Requirement | Verdict (expected / worst) | Accepted by |
|---|---|---|---|---|
| RL-1 | availability ≥ 99% | NFR-11 | fits / fits with changes / does not fit | `D-<n>` if it fails and the failure is accepted, else — |

## 10. Not applicable
Targets (`B-`, `I-`, `X-`, `E-`) with nothing that can go wrong, each with the reason.

## 11. Reconciliation with earlier steps
What the register changed or found in earlier documents (architecture redundancy, mechanics recoveries, data copies, requirements promises) with the decision or the pending question.

## 12. Risks, assumptions and open questions
Ranked; every assumed number has the cheapest way to validate it (a drill, a measurement, a spike).

## 13. Deferred
One line per detail, tagged with the target stage (`→ roadmap: …`).

## 14. Consistency check
Date; `check_resilience.py` result (errors / warnings left and why); verdict of the independent reviewer; what was fixed; what stays open.

## Sources
Numbered URLs; delegated findings link to `[R-n]` reports with their confidence.
````
