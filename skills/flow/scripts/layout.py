#!/usr/bin/env python3
"""Layout check and migration for one zkit project folder. Stdlib only.
Usage: layout.py <project-dir> [--migrate [--apply]]
  Check: WARN for root entries that are not a step document or a known folder, and for step documents over twice their target length.
  --migrate: print the deterministic moves from the old layout to the current one (models into their step folder, validation/<step>-* into
  checks/<step>/); --apply performs them and fixes links to moved models. Everything else is listed as manual. Exit 1 on WARN."""
import os, re, sys, shutil

d = next((a for a in sys.argv[1:] if not a.startswith("--")), ".")
STEPS = ["concept", "requirements", "resource-math", "ux", "contracts", "data", "architecture", "mechanics", "resilience", "roadmap"]
FILES = {s + ".md" for s in STEPS} | {"decisions.md"}
DIRS = {"resource-math", "contracts", "mechanics", "resilience", "roadmap", "diagrams", "research", "checks", "appendix"}
TARGET = {"concept": 2500, "requirements": 3500, "resource-math": 3000, "ux": 2500, "contracts": 5000, "data": 3000, "architecture": 4500, "mechanics": 4500, "resilience": 5000, "roadmap": 4500}
MOVES = {"resource_model.py": "resource-math/model.py", "resilience_model.py": "resilience/model.py"}
HINT = {"tasks": "roadmap/epics/EP-n-<slug>/tasks/", "measurements": "research/R-n-<slug>/", "reference": "research/R-n-<slug>/",
        "validation": "checks/<step>/", "task-template.md": "delete (the template lives in the plugin)"}
if not os.path.isdir(d): sys.exit("ERROR: %s is not a folder" % d)
warns = []

for name in sorted(os.listdir(d)):
    if name.startswith(".") or name in FILES or name in DIRS: continue
    warns.append("root entry '%s' is outside the layout; suggested: %s" % (name, MOVES.get(name) or HINT.get(name) or "appendix/" + name))
for s in STEPS:
    p = os.path.join(d, s + ".md")
    if os.path.exists(p):
        n = len(open(p, encoding="utf-8").read().split())
        if n > 2 * TARGET[s]: warns.append("%s.md has %d words, target %d: keep the summary and tables here, details in %s/ or research/" % (s, n, TARGET[s], s))

plan = [(k, v) for k, v in MOVES.items() if os.path.exists(os.path.join(d, k))]
val = os.path.join(d, "validation")
if os.path.isdir(val):
    for f in sorted(os.listdir(val)):
        m = re.match(r"(%s)[-_]" % "|".join(sorted(STEPS, key=len, reverse=True)), f)
        step = m.group(1) if m else "roadmap" if f.startswith("task-cards") else None
        if step: plan.append(("validation/" + f, "checks/%s/%s" % (step, f)))
if "--migrate" in sys.argv:
    apply = "--apply" in sys.argv
    for a, b in plan:
        print("%s %s -> %s" % ("MOVE" if apply else "would move", a, b))
        if apply:
            os.makedirs(os.path.dirname(os.path.join(d, b)), exist_ok=True); shutil.move(os.path.join(d, a), os.path.join(d, b))
    if apply:
        for k, v in MOVES.items():   # links and mentions of the moved models
            for f in os.listdir(d):
                if f.endswith(".md"):
                    t = open(os.path.join(d, f), encoding="utf-8").read()
                    if k in t: open(os.path.join(d, f), "w", encoding="utf-8").write(t.replace(k, v))
        if os.path.isdir(val) and not os.listdir(val): os.rmdir(val)
    left = [w for w in warns if not any(w.startswith("root entry '%s'" % a.split("/")[0]) and "/" not in a for a, _ in plan) and "'validation'" not in w]
    rest = [f for f in sorted(os.listdir(val)) if "validation/" + f not in {a for a, _ in plan}] if os.path.isdir(val) and not apply else []
    if rest: left.append("validation/ keeps %d file(s) with no step prefix (%s ...): move them to checks/<step>/ by hand" % (len(rest), ", ".join(rest[:3])))
    print("manual:" if left else "nothing manual left")
    for w in left: print("  " + w)
    sys.exit(0)
print("\n".join("WARN   " + w for w in warns) if warns else "OK: layout matches")
sys.exit(1 if warns else 0)
