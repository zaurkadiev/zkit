# UX template

Aim for roughly 1,000-2,500 words. Tables over prose. Sections in this order; drop one only if irrelevant and say so in one line. No payloads or operation specs (contracts), no frameworks, no colours, fonts or styling. Translate headings into the developer's language.

````markdown
# <Name> — UX

> **Links:** [concept](concept.md) · [requirements](requirements.md) · [resource-math](resource-math.md) · [decisions](decisions.md)
> **Status:** draft / agreed (agreed only when the clarity gate passes, SKILL.md step 5) · **Date:** <date> · **Based on:** requirements.md (<date>), resource-math.md (<date>)
> **Counts:** <n> U · <n> J   (the checker compares these with the tables)

## 1. Summary
The UX in ≤5 sentences: who uses it, how many surfaces and journeys, the tightest budget, the biggest assumption about people, the main finding.

## 2. Surfaces
| ID | Surface | Kind | Actor | Platform / input | Feedback budget | Serves |
|---|---|---|---|---|---|---|
| U-1 | Task board | screen | owner | desktop browser, keyboard + mouse | reaction ≤ 100 ms, result ≤ L-3 | FR-4, NFR-2 |

`Kind`: screen / cli / console / chat / notification / config / voice / controls. `Feedback budget`: a figure or the resource-math limit `L-n`; `—` for non-interactive kinds (notification, config).

## 3. Journeys
| ID | Journey | Actor | Surfaces | Happy path | Failure and empty cases | Serves |
|---|---|---|---|---|---|---|
| J-1 | Approve a risky action | owner | U-2, U-1 | notice arrives → open → read the reason → approve | notice missed (reminder after 1 h); action expired (shown as expired, nothing is sent) | FR-9, NFR-7 |

First-run and recovery journeys are listed like any other.

## 4. States and messages
| Surface | State | What the person sees and can do |
|---|---|---|
| U-1 | empty | "No tasks yet" + the one action that creates the first |
| U-1 | error | what failed in plain words, what to do next, how to retry |
| U-1 | unavailable | last known data marked as stale, actions disabled with the reason |

States: empty, loading, partial, error, unavailable, denied. Every surface has at least an `error` row.

## 5. Sketches and cards
A content sketch per key screen and per small or fixed display:
```
+---------------------+
|B3 05 WARM PAD    *  |  line 1: bank, number, name; * = unsaved edits
|CUT   RES   ATK  REL |  line 3: one column per encoder
|MIDI CH1   SAVED     |  line 8: status, messages for 3 s
+---------------------+
```
What changes, what is cut first when it does not fit. Cards for cli, config and controls (otherwise "not applicable"): the command grammar with exit codes, the config keys a person edits and their defaults, the control-to-function map.

## 6. Cross-cutting
Platforms and input devices, accessibility level and how it is checked, language and units, notification etiquette, destructive-action confirmation rule — one line each, with the requirement behind it.

## 7. Findings and consequences
Number the items plainly (`1.`, `2.`); id-like labels (`F-1`, `G-1`) belong to the id registry (`flow/scripts/ids.py`) and fail its check.
Requirement issues found (a budget below what resource math allows, an accessibility rule the platform cannot meet) with the decision taken or pending. What the surfaces need from the system, tagged `→ contracts: …`; constraints for the parts, tagged `→ architecture: …`; user-facing failure behaviour, tagged `→ resilience: …`.

## 8. Risks, assumptions and open questions
Ranked; every assumption about people has the cheapest way to validate it (a clickable prototype, five people, dogfooding, a spike for the roadmap).

## 9. Consistency check
Date; `check_ux.py` result (errors / warnings left and why); verdict of the independent reviewer; what was fixed; what stays open.

## Sources
Numbered URLs; delegated findings link to `[R-n]` reports with their confidence.
````
