"""The zkit id registry: one owner document per id prefix. Stdlib only; imported by link_docs.py and every check_<step>.py.

An id is defined as the first cell of a table row in its owner, except D (heading '### D-n' in decisions.md),
R (file research/R-n-<slug>.md), P and Q (list items '**P-n.**', '**Q-n.**' in requirements.md).
To add a prefix: add it here, to its step's template, and to the list in flow/SKILL.md.
"""

IDS = {   # prefix: (owner document, what it names)
    "FR": ("requirements.md", "functional requirement"), "NFR": ("requirements.md", "non-functional requirement"),
    "C": ("requirements.md", "constraint"), "P": ("requirements.md", "precondition or deferred validation"),
    "Q": ("requirements.md", "conflict, risk or open question"),
    "A": ("resource-math.md", "assumption"), "L": ("resource-math.md", "limit"),
    "U": ("ux.md", "surface"), "J": ("ux.md", "journey"),
    "X": ("contracts.md", "external boundary"),
    "E": ("data.md", "entity"), "M": ("data.md", "in-memory state"),
    "B": ("architecture.md", "part"), "I": ("architecture.md", "interface"), "S": ("architecture.md", "scenario"),
    "MC": ("mechanics.md", "mechanism"),
    "F": ("resilience.md", "failure"), "T": ("resilience.md", "threat"), "O": ("resilience.md", "observability signal"),
    "DR": ("resilience.md", "drill"), "RA": ("resilience.md", "resilience assumption"), "RL": ("resilience.md", "resilience limit"),
    "PH": ("roadmap.md", "phase"), "G": ("roadmap.md", "gate"), "EP": ("roadmap.md", "epic"), "TK": ("roadmap.md", "task"),
    "D": ("decisions.md", "decision"), "R": ("research/", "research report"),
}


def rx(*prefixes, num=r"\d+"):
    """Regex for ids with these prefixes: rx("FR", "NFR") -> (?:FR|NFR)-\\d+. An unregistered prefix raises."""
    bad = [p for p in prefixes if p not in IDS]
    if bad: raise KeyError("not in the id registry (flow/scripts/ids.py): " + ", ".join(bad))
    return "(?:%s)-%s" % ("|".join(prefixes), num)


if __name__ == "__main__":
    import re
    assert rx("FR", "NFR") == r"(?:FR|NFR)-\d+" and re.fullmatch(rx("B"), "B-12") and not re.fullmatch(rx("B"), "MB-1")
    try: rx("К"); raise SystemExit("unregistered prefix accepted")
    except KeyError: pass
    for p, (own, what) in IDS.items(): print("%-4s %-17s %s" % (p, own, what))
