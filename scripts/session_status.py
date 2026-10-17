#!/usr/bin/env python3
"""SessionStart hook: if ./docs/zkit/<project>/ exists, print one line per project with the next zkit step. Silent otherwise."""
import glob, os, re
STEPS = [("concept", "concepting"), ("requirements", "requirements"), ("resource-math", "resource-math"), ("ux", "ux"), ("contracts", "contracts"),
         ("data", "data"), ("architecture", "architecture"), ("mechanics", "mechanics"), ("resilience", "resilience"), ("roadmap", "roadmap")]
for d in sorted(glob.glob("docs/zkit/*/")):
    state = {}
    for f, skill in STEPS:
        p = os.path.join(d, f + ".md")
        if os.path.exists(p):
            m = re.search(r"Status:\*{0,2}\s*(agreed|draft)", open(p, encoding="utf-8").read(3000), re.I)
            state[f] = (m.group(1).lower() if m else "draft")
    dec = os.path.join(d, "decisions.md")   # ux is optional: a decision "ux: not applicable" counts as done
    if "ux" not in state and os.path.exists(dec) and re.search(r"D-\d+:\s*ux:\s*not applicable", open(dec, encoding="utf-8").read(), re.I): state["ux"] = "agreed"
    nxt = next(((f, s) for f, s in STEPS if state.get(f) != "agreed"), None)
    name = os.path.basename(d.rstrip("/"))
    if nxt:
        print(f"zkit: project '{name}' - agreed: {', '.join(k for k, v in state.items() if v == 'agreed') or 'none'}; next: {nxt[1]}. Run /zkit:flow to continue.")
    else:
        print(f"zkit: project '{name}' - all steps agreed.")
