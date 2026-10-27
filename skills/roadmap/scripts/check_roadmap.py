#!/usr/bin/env python3
"""Roadmap checker and scheduler for one zkit project. Stdlib only.
Usage: check_roadmap.py <project-dir> [--update]
  Parses roadmap.md (phases PH-n, gates G-n, tasks TK-n, epics EP-n, capacity) and the files roadmap/epics/EP-n-*/epic.md and
  roadmap/epics/EP-n-*/tasks/TK-n-*.md (one per epic and per task), schedules the work on one or more workers (Capacity column Workers) in
  best / expected / worst scenarios (dependencies, external waits), checks coverage of earlier documents, and with --update
  rewrites the generated block (table, critical path, lanes, Mermaid graph) between <!-- schedule:begin --> and <!-- schedule:end -->. Exit 1 on ERROR."""
import re, sys, os, math, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flow", "scripts"))
from ids import rx

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
update = "--update" in sys.argv
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, req, rs = rdp("roadmap.md"), rdp("requirements.md"), rdp("resilience.md")
if doc is None: sys.exit("ERROR: no roadmap.md in %s (pass the project folder)" % d)
out = []
err = lambda m: out.append("ERROR  " + m)
warn = lambda m: out.append("WARN   " + m)
B0, B1 = "<!-- schedule:begin -->", "<!-- schedule:end -->"
body = re.sub(re.escape(B0) + r".*?" + re.escape(B1), "", doc, flags=re.S)

def tables(t, idpat):
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() in ("id", "scenario", "сценарий"): hdr = [x.lower() for x in c]; continue
        if hdr and not re.match(r"[-: ]+$", c[0]) and re.match(idpat, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")
num = lambda s, default=0.0: float(m.group(0)) if (m := re.search(r"\d+(?:[.,]\d+)?", s.replace(",", "."))) else default

PH, G = tables(body, rx("PH") + r"$"), tables(body, rx("G") + r"$")
TK, EP = tables(body, rx("TK") + r"$"), tables(body, rx("EP") + r"$")
CAP = tables(body, r"(best|expected|worst|лучш|ожидаем|худш)")
# every task belongs to an epic; an epic that has tasks is a container (its hours are the tasks'), one without tasks is scheduled by its own range
epic_of = {r["_id"]: (re.search(rx("EP"), col(r, r"epic|эпик")) or re.search("", "")).group(0) for r in TK}
eps = {r["_id"] for r in EP}
for t_, e_ in epic_of.items():
    if not e_: err("%s names no epic (column Epic)" % t_)
    elif e_ not in eps: err("%s names epic %s, which does not exist" % (t_, e_))
containers = {e_ for e_ in epic_of.values() if e_ in eps}
kids = {e_: [t_ for t_, x in epic_of.items() if x == e_] for e_ in containers}
items = TK + [r for r in EP if r["_id"] not in containers]
ids = [r["_id"] for r in PH + G + TK + EP]
for i in set(ids):
    if ids.count(i) > 1: err("duplicate id %s" % i)
if not PH: err("no phases (PH-n)")
if not TK: err("no detailed tasks (TK-n)")
phases = {r["_id"] for r in PH}; known = {r["_id"] for r in items}

# ---------- items: hours, phase, dependencies, acceptance
H = {}
for r in items:
    i = r["_id"]; hrs = []
    for k in ("best", "expected", "worst"):
        v = col(r, k)
        if not re.search(r"\d", v): err("%s has no %s hours" % (i, k)); hrs.append(0.0)
        else: hrs.append(num(v))
    if not (hrs[0] <= hrs[1] <= hrs[2]): err("%s: hours must satisfy best <= expected <= worst" % i)
    H[i] = hrs
    ph = col(r, r"phase|фаз").strip()
    if ph not in phases: err("%s names phase '%s', which does not exist" % (i, ph))
    if i.startswith("TK") and hrs[1] > 16: warn("%s is %g h expected: split it (detailed tasks are 4-16 h)" % (i, hrs[1]))
    if i.startswith("TK") and not col(r, r"accept|приёмк|критер").strip(" —-"): err("%s has no acceptance criterion" % i)
    if not re.search((rx("FR", "NFR", "C", "L", "RL", "DR", "MC", "D", "E", "X", "I", "B", "S", "G") + r"|spike|" + rx("P", num=r"\d")), col(r, r"serves|source|обслужив|источник|requirement|требован"), re.I): warn("%s traces to no requirement, limit, drill or decision" % i)
dep = {}
for r in items:
    raw = re.findall(rx("TK", "EP"), col(r, r"depend|завис"))
    for x in raw:
        if x not in known and x not in containers: err("%s depends on %s, which does not exist" % (r["_id"], x))
    dep[r["_id"]] = [y for x in raw for y in (kids.get(x) or [x])]   # depending on an epic means depending on all its tasks
    if r["_id"] in dep[r["_id"]]: err("%s depends on itself" % r["_id"])
state, order = {}, []
def visit(n, stack):
    if state.get(n) == 2: return
    if state.get(n) == 1: err("dependency cycle through %s" % " -> ".join(stack + [n])); return
    state[n] = 1
    for x in dep.get(n, []):
        if x in known: visit(x, stack + [n])
    state[n] = 2; order.append(n)
phrank = {r["_id"]: i for i, r in enumerate(PH)}
phase_of = {r["_id"]: col(r, r"phase|фаз").strip() for r in items}
pos = {r["_id"]: i for i, r in enumerate(items)}   # document order breaks ties, so TK-10 does not sort before TK-2
for n in sorted(known, key=lambda k: (phrank.get(phase_of[k], 99), pos[k])): visit(n, [])
item = {r["_id"]: r for r in items}

# ---------- capacity and schedule
cap = {}
for r in CAP:
    k = "best" if re.match(r"(best|лучш)", r["_id"], re.I) else "expected" if re.match(r"(expected|ожидаем)", r["_id"], re.I) else "worst"
    cap[k] = (num(col(r, r"hours|час"), 0.0), col(r, r"deadline|срок"), max(1, int(num(col(r, r"worker|исполнит"), 1))))
for k in ("best", "expected", "worst"):
    if k not in cap or cap[k][0] <= 0: err("capacity table has no hours per week for the %s scenario" % k)
# a gate closes its phase: nothing in a later phase starts before every item of a gated phase is done
gated = {p for g in G for p in re.findall(rx("PH"), col(g, r"phase|after|фаз"))}
barrier = {n: [x for x in known if phase_of[x] in gated and phrank.get(phase_of[x], 99) < phrank.get(phase_of[n], 99)] for n in known}
def schedule(sc):
    """List scheduling on W workers: repeatedly start the ready item that can start earliest (document order breaks
    ties). Returns finish and start weeks, the lane of each item and why[n], the item whose finish set n's start."""
    hw, _, W = cap.get(sc, (1, "", 1)); hw = hw or 1; idx = ("best", "expected", "worst").index(sc)
    lfree, last = [0.0] * W, [None] * W
    fin, start, lane, why = {}, {}, {}, {}
    left = list(order)
    while left:
        ready = [n for n in left if all(x in fin for x in dep[n] + barrier[n] if x in known)] or left[:1]   # a cycle (already an ERROR) must not hang
        best = None
        for n in ready:
            wait = num(col(item[n], r"wait|ожидан"), 0.0)
            pre = max([(fin[x] + wait, x) for x in dep[n] if x in fin] + [(fin[x], x) for x in barrier[n] if x in fin] + [(0.0, None)], key=lambda t: t[0])
            w = min(range(W), key=lambda k: lfree[k])
            s = max(pre[0], lfree[w])
            if best is None or s < best[0] - 1e-9: best = (s, n, w, pre[1] if pre[0] >= lfree[w] else last[w])
        s, n, w, why[n] = best
        start[n], fin[n], lane[n] = s, s + H[n][idx] / hw, w
        lfree[w], last[w] = fin[n], n; left.remove(n)
    return fin, start, lane, why
plan = {sc: schedule(sc) for sc in ("best", "expected", "worst")}
fin = {sc: plan[sc][0] for sc in plan}
tot = {sc: (max(fin[sc].values()) if fin[sc] else 0.0) for sc in fin}
hsum = [sum(H[n][i] for n in H) for i in range(3)]
def when(sc, ph):
    xs = [fin[sc][n] for n in fin[sc] if col(item[n], r"phase|фаз").strip() == ph]
    return max(xs) if xs else 0.0
rows = ["**Schedule** (workers best / expected / worst: %s; hours per week per worker: %s; weeks from the start)" % (" / ".join("%d" % cap.get(k, (0, "", 1))[2] for k in ("best", "expected", "worst")), " / ".join("%g" % cap.get(k, (0,))[0] for k in ("best", "expected", "worst"))), "",
        "| Phase | Hours best | Hours expected | Hours worst | Done in week (best) | (expected) | (worst) |", "|---|---|---|---|---|---|---|"]
for p in PH:
    hs = [sum(H[n][i] for n in H if col(item[n], r"phase|фаз").strip() == p["_id"]) for i in range(3)]
    rows.append("| %s | %g | %g | %g | %.1f | %.1f | %.1f |" % (p["_id"], hs[0], hs[1], hs[2], when("best", p["_id"]), when("expected", p["_id"]), when("worst", p["_id"])))
rows.append("| **Total** | %g | %g | %g | %.1f | %.1f | %.1f |" % (hsum[0], hsum[1], hsum[2], tot["best"], tot["expected"], tot["worst"]))
verd = []
for sc in ("best", "expected", "worst"):
    cell = cap.get(sc, (0, ""))[1]
    dl = num(cell, 0.0) if re.search(r"\d", cell) else 0.0
    mp = re.search(rx("PH"), cell)          # a deadline may refer to the end of one phase, e.g. "52 @PH-3"
    end = when(sc, mp.group(0)) if mp else tot[sc]
    what = mp.group(0) if mp else "the whole plan"
    if dl: verd.append("%s: %s done in %.1f weeks vs deadline %g -> %s" % (sc, what, end, dl, "fits" if end <= dl else "DOES NOT FIT by %.1f weeks" % (end - dl)))
    if dl and end > dl and sc == "expected": verd.append("!expected")
rows += ["", "**Deadline check**", ""] + ["- " + v for v in verd if not v.startswith("!")]
_, st_e, lane_e, why_e = plan["expected"]
crit, n = [], max(fin["expected"], key=fin["expected"].get) if fin["expected"] else None
while n: crit.append(n); n = why_e.get(n)
rows += ["", "**Critical path (expected)**: " + " → ".join(reversed(crit))]
if cap.get("expected", (0, "", 1))[2] > 1:
    rows += ["", "**Lanes (expected; start–finish week)**", ""] + ["- Worker %d: " % (w + 1) + ", ".join("%s %.1f–%.1f" % (x, st_e[x], fin["expected"][x]) for x in sorted((x for x in lane_e if lane_e[x] == w), key=st_e.get)) for w in range(cap["expected"][2])]
# dependency graph: side-by-side branches run in parallel; colour = worker, thick border = critical path, hexagon = gate
W_e, mid = cap.get("expected", (0, "", 1))[2], lambda x: x.replace("-", "_")
g = ["", "**Graph (expected)**: arrows are dependencies, branches side by side run in parallel%s, thick border = critical path." % ("; colour = worker" if W_e > 1 else ""), "", "```mermaid", "flowchart LR"]
for p in PH:
    xs = sorted((x for x in known if phase_of[x] == p["_id"]), key=st_e.get)
    if not xs: continue
    g.append('  subgraph %s["%s"]' % (mid(p["_id"]), p["_id"]))
    g += ['    %s["%s%s<br/>wk %.1f–%.1f"]' % (mid(x), x, " · W%d" % (lane_e[x] + 1) if W_e > 1 else "", st_e[x], fin["expected"][x]) for x in xs]
    g.append("  end")
used = {phase_of[x] for x in known}
nxt = {p["_id"]: next((q["_id"] for q in PH[i + 1:] if q["_id"] in used), None) for i, p in enumerate(PH)}
for gt in G:
    for p in re.findall(rx("PH"), col(gt, r"phase|after|фаз"))[:1]:
        if p in used: g.append('  %s --> %s{{"%s"}}' % (mid(p), mid(gt["_id"]), gt["_id"]) + (" --> %s" % mid(nxt[p]) if nxt.get(p) else ""))
g += ["  %s --> %s" % (mid(x), mid(n)) for n in order for x in dict.fromkeys(dep[n]) if x in known]
if W_e > 1:
    pal = ["#dbeafe", "#dcfce7", "#fef3c7", "#fce7f3", "#ede9fe", "#ccfbf1", "#fee2e2", "#e5e7eb"]
    for w in range(W_e):
        xs = [mid(x) for x in order if lane_e[x] == w]
        if xs: g += ["  classDef w%d fill:%s,color:#111" % (w + 1, pal[w % len(pal)]), "  class %s w%d" % (",".join(xs), w + 1)]
if crit: g += ["  classDef crit stroke:#b91c1c,stroke-width:3px", "  class %s crit" % ",".join(mid(x) for x in crit)]
rows += g + ["```"]
block = "\n".join(rows)
m = re.search(re.escape(B0) + r"(.*?)" + re.escape(B1), doc, re.S)
if not m: err("no %s ... %s block in roadmap.md" % (B0, B1))
elif update:
    doc = doc[:m.start(1)] + "\n" + block + "\n" + doc[m.end(1):]; open(os.path.join(d, "roadmap.md"), "w", encoding="utf-8").write(doc); print("block updated")
elif m.group(1).strip() != block.strip(): err("the generated schedule block is stale: run with --update")
misses_deadline = "!expected" in verd

# ---------- epic and task files: roadmap/epics/EP-n-<slug>/epic.md and .../tasks/TK-n-<slug>.md
ROOT = os.path.join(d, "roadmap", "epics")
NEED = {"epic": [("goal", r"goal|цель"), ("boundaries", r"bound|scope|границ")],
        "task": [("goal", r"goal|цель"), ("what must be done", r"what must|to do|сделать|что нужно"), ("boundaries (in / out)", r"bound|scope|границ"), ("inputs", r"input|вход"), ("acceptance", r"accept|приёмк|критер")]}
def read_file(f, kind):
    t = open(f, encoding="utf-8").read(); rel = os.path.relpath(f, d)
    heads = [l.lstrip("#").strip().lower() for l in t.splitlines() if l.startswith("#")]
    for name, pat in NEED[kind]:
        if not any(re.search(pat, h) for h in heads): err("%s has no '%s' section" % (rel, name))
    if kind == "task" and len(t.split()) < 80: warn("%s is under 80 words: a task file must say what to do in enough detail to start without asking" % rel)
idof = lambda f, k: (re.match(k + r"-\d+", os.path.basename(f)) or re.match("", "")).group(0)
efile = {idof(os.path.dirname(f), "EP"): f for f in glob.glob(os.path.join(ROOT, "EP-*", "epic.md"))}
tfile = {idof(f, "TK"): f for f in glob.glob(os.path.join(ROOT, "EP-*", "tasks", "TK-*.md"))}
nofile = []
for e_ in sorted(eps):
    if e_ not in efile: err("%s has no file roadmap/epics/%s-<slug>/epic.md" % (e_, e_)); nofile.append(e_)
    else: read_file(efile[e_], "epic")
for r in TK:
    i = r["_id"]
    if i not in tfile: err("%s has no file roadmap/epics/%s-<slug>/tasks/%s-<slug>.md" % (i, epic_of[i] or "EP-n", i)); nofile.append(i); continue
    read_file(tfile[i], "task")
    if epic_of[i] and idof(os.path.dirname(os.path.dirname(tfile[i])), "EP") != epic_of[i]: err("%s lies in the folder of another epic than its table row says (%s)" % (i, epic_of[i]))
for x in sorted(set(tfile) - {r["_id"] for r in TK}): warn("task file %s has no row in the tasks table" % os.path.relpath(tfile[x], d))
for x in sorted(set(efile) - eps): warn("epic file %s has no row in the epics table" % os.path.relpath(efile[x], d))

# ---------- gates
for g in G:
    if not col(g, r"criteria|критер").strip(" —-"): err("%s has no exit criteria" % g["_id"])
    if not col(g, r"if fail|decision|решени|иначе").strip(" —-"): err("%s has no rule for what happens if the criteria fail (continue / change / stop)" % g["_id"])
    if col(g, r"phase|фаз").strip() not in phases and not re.search(rx("PH"), col(g, r"phase|after|фаз")): err("%s is not attached to a phase" % g["_id"])
if PH and not G: err("no gates (G-n): a plan without go / change / stop points is a list")
first = PH[0]["_id"] if PH else ""
if not any(re.search(r"spike|DR-|validat|measure|замер|провер|пилот|pilot", col(r, r"source|serves|источник|task|задач"), re.I) for r in items if col(r, r"phase|фаз").strip() == first): warn("first phase %s has no spike, drill or validation: risks should come first" % first)

# ---------- coverage of earlier documents
text_items = " ".join(" ".join(r.values()) for r in TK + EP)
reqs = {}
if req is not None:
    hdr = None
    for l in req.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(r"(FR|NFR)-\d+$", c[0]):
            i = next((n for n, h in enumerate(hdr) if re.search(r"приоритет|priority", h)), None)
            reqs[c[0]] = c[i] if i is not None and i < len(c) else ""
else: warn("no requirements.md: coverage cannot be checked")
def expand(s):
    ids = set(re.findall(r"\b" + rx("FR", "NFR") + r"\b", s))
    for a, b in re.findall((r"(" + rx("FR", "NFR") + r")\s*[…\-–]+\s*(?:" + rx("FR", "NFR", num=r"") + r")?(\d+)"), s):
        k, lo = a.split("-")
        if int(b) >= int(lo): ids |= set("%s-%d" % (k, i) for i in range(int(lo), int(b) + 1))
    return ids
served = expand(text_items)
unserved = sorted(r for r, p in reqs.items() if p == "Must" and r not in served)
for r in unserved: err("Must requirement %s is served by no task or epic" % r)
drills = sorted(set(re.findall(r"^\|\s*(" + rx("DR") + r")\s*\|", rs or "", re.M)))
undrilled = [x for x in drills if x not in text_items]
for x in undrilled: err("drill %s of resilience.md is planned by no task or epic" % x)
for x in sorted(set(re.findall(r"\b" + rx("FR", "NFR") + r"\b", text_items))):
    if reqs and x not in reqs: err("cites %s, not in requirements" % x)

# ---------- counts, drift, status, clarity
head = doc.split("\n## ")[0]
want = {"PH": len(PH), "G": len(G), "TK": len(TK), "EP": len(EP)}
for k, n in want.items():
    mm = re.search(r"(\d+)\s*%s\b" % k, head)
    if not mm or int(mm.group(1)) != n: err("header count for %s is '%s', actual %d" % (k, mm.group(1) if mm else "missing", n))
docs = [("requirements", req), ("resource-math", rdp("resource-math.md")), ("contracts", rdp("contracts.md")), ("data", rdp("data.md")), ("architecture", rdp("architecture.md")), ("mechanics", rdp("mechanics.md")), ("resilience", rs)]
for nm, text in docs:
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the roadmap is based on (%s)" % (nm, rdte.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
cuts = bool(re.search(rx("D"), " ".join(l for l in body.splitlines() if re.search(r"(?i)deadline|срок|cut|сокращ|accept|принят", l)))) or bool(re.search(r"(?im)^## .*(cut|сокращ)", body))
if misses_deadline and not cuts: err("the expected scenario misses the deadline and the document has neither a cuts section nor an accepting decision (D-n)")
out.append("CLARITY %d Must requirement(s) unserved; %d drill(s) unplanned; %d epic/task file(s) missing; expected scenario %s the deadline" % (len(unserved), len(undrilled), len(nofile), "misses" if misses_deadline else "meets or has no"))
if agreed and (unserved or undrilled or nofile or misses_deadline): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d phases, %d gates, %d tasks, %d epics; hours %g / %g / %g; weeks %.1f / %.1f / %.1f" % (len(PH), len(G), len(TK), len(EP), hsum[0], hsum[1], hsum[2], tot["best"], tot["expected"], tot["worst"]))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
