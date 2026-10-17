#!/usr/bin/env python3
"""Roadmap checker and scheduler for one zkit project. Stdlib only.
Usage: check_roadmap.py <project-dir> [--update]
  Parses roadmap.md (phases PH-n, gates G-n, tasks TK-n, epics EP-n, capacity), schedules the work for one developer in
  best / expected / worst scenarios (dependencies, external waits), checks coverage of earlier documents, and with --update
  rewrites the generated block between <!-- schedule:begin --> and <!-- schedule:end -->. Exit 1 on ERROR."""
import re, sys, os, math

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

PH, G = tables(body, r"PH-\d+$"), tables(body, r"G-\d+$")
TK, EP = tables(body, r"TK-\d+$"), tables(body, r"EP-\d+$")
CAP = tables(body, r"(best|expected|worst|лучш|ожидаем|худш)")
items = TK + EP
ids = [r["_id"] for r in PH + G + items]
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
    if not re.search(r"(?:FR|NFR|C|L|RL|DR|MC|D|E|X|I|B|S|G)-\d+|spike|P-\d", col(r, r"serves|source|обслужив|источник|requirement|требован"), re.I): warn("%s traces to no requirement, limit, drill or decision" % i)
dep = {}
for r in items:
    dep[r["_id"]] = re.findall(r"(?:TK|EP)-\d+", col(r, r"depend|завис"))
    for x in dep[r["_id"]]:
        if x not in known: err("%s depends on %s, which does not exist" % (r["_id"], x))
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
    cap[k] = (num(col(r, r"hours|час"), 0.0), col(r, r"deadline|срок"))
for k in ("best", "expected", "worst"):
    if k not in cap or cap[k][0] <= 0: err("capacity table has no hours per week for the %s scenario" % k)
def schedule(sc):
    hw = cap.get(sc, (1, ""))[0] or 1; idx = ("best", "expected", "worst").index(sc)
    free, fin, start = 0.0, {}, {}
    for n in order:
        wait = num(col(item[n], r"wait|ожидан"), 0.0)
        s = max([free] + [fin[x] + wait for x in dep[n] if x in fin])
        start[n] = s; fin[n] = s + H[n][idx] / hw; free = fin[n]
    return fin
fin = {sc: schedule(sc) for sc in ("best", "expected", "worst")}
tot = {sc: (max(fin[sc].values()) if fin[sc] else 0.0) for sc in fin}
hsum = [sum(H[n][i] for n in H) for i in range(3)]
def when(sc, ph):
    xs = [fin[sc][n] for n in fin[sc] if col(item[n], r"phase|фаз").strip() == ph]
    return max(xs) if xs else 0.0
rows = ["**Schedule** (one developer; weeks from the start; hours per week best / expected / worst: %s)" % " / ".join("%g" % cap.get(k, (0,))[0] for k in ("best", "expected", "worst")), "",
        "| Phase | Hours best | Hours expected | Hours worst | Done in week (best) | (expected) | (worst) |", "|---|---|---|---|---|---|---|"]
for p in PH:
    hs = [sum(H[n][i] for n in H if col(item[n], r"phase|фаз").strip() == p["_id"]) for i in range(3)]
    rows.append("| %s | %g | %g | %g | %.1f | %.1f | %.1f |" % (p["_id"], hs[0], hs[1], hs[2], when("best", p["_id"]), when("expected", p["_id"]), when("worst", p["_id"])))
rows.append("| **Total** | %g | %g | %g | %.1f | %.1f | %.1f |" % (hsum[0], hsum[1], hsum[2], tot["best"], tot["expected"], tot["worst"]))
verd = []
for sc in ("best", "expected", "worst"):
    cell = cap.get(sc, (0, ""))[1]
    dl = num(cell, 0.0) if re.search(r"\d", cell) else 0.0
    mp = re.search(r"PH-\d+", cell)          # a deadline may refer to the end of one phase, e.g. "52 @PH-3"
    end = when(sc, mp.group(0)) if mp else tot[sc]
    what = mp.group(0) if mp else "the whole plan"
    if dl: verd.append("%s: %s done in %.1f weeks vs deadline %g -> %s" % (sc, what, end, dl, "fits" if end <= dl else "DOES NOT FIT by %.1f weeks" % (end - dl)))
    if dl and end > dl and sc == "expected": verd.append("!expected")
rows += ["", "**Deadline check**", ""] + ["- " + v for v in verd if not v.startswith("!")]
crit = [n for n in order if abs(fin["expected"][n] - tot["expected"]) < 1e-9]
rows += ["", "**Critical path (expected, last items)**: " + ", ".join(order[-6:]) if order else ""]
block = "\n".join(rows)
m = re.search(re.escape(B0) + r"(.*?)" + re.escape(B1), doc, re.S)
if not m: err("no %s ... %s block in roadmap.md" % (B0, B1))
elif update:
    doc = doc[:m.start(1)] + "\n" + block + "\n" + doc[m.end(1):]; open(os.path.join(d, "roadmap.md"), "w", encoding="utf-8").write(doc); print("block updated")
elif m.group(1).strip() != block.strip(): err("the generated schedule block is stale: run with --update")
misses_deadline = "!expected" in verd

# ---------- gates
for g in G:
    if not col(g, r"criteria|критер").strip(" —-"): err("%s has no exit criteria" % g["_id"])
    if not col(g, r"if fail|decision|решени|иначе").strip(" —-"): err("%s has no rule for what happens if the criteria fail (continue / change / stop)" % g["_id"])
    if col(g, r"phase|фаз").strip() not in phases and not re.search(r"PH-\d+", col(g, r"phase|after|фаз")): err("%s is not attached to a phase" % g["_id"])
if PH and not G: err("no gates (G-n): a plan without go / change / stop points is a list")
first = PH[0]["_id"] if PH else ""
if not any(re.search(r"spike|DR-|validat|measure|замер|провер|пилот|pilot", col(r, r"source|serves|источник|task|задач"), re.I) for r in items if col(r, r"phase|фаз").strip() == first): warn("first phase %s has no spike, drill or validation: risks should come first" % first)

# ---------- coverage of earlier documents
text_items = " ".join(" ".join(r.values()) for r in items)
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
    ids = set(re.findall(r"\b(?:FR|NFR)-\d+\b", s))
    for a, b in re.findall(r"((?:FR|NFR)-\d+)\s*[…\-–]+\s*(?:(?:FR|NFR)-)?(\d+)", s):
        k, lo = a.split("-")
        if int(b) >= int(lo): ids |= set("%s-%d" % (k, i) for i in range(int(lo), int(b) + 1))
    return ids
served = expand(text_items)
unserved = sorted(r for r, p in reqs.items() if p == "Must" and r not in served)
for r in unserved: err("Must requirement %s is served by no task or epic" % r)
drills = sorted(set(re.findall(r"^\|\s*(DR-\d+)\s*\|", rs or "", re.M)))
undrilled = [x for x in drills if x not in text_items]
for x in undrilled: err("drill %s of resilience.md is planned by no task or epic" % x)
for x in sorted(set(re.findall(r"\b(?:FR|NFR)-\d+\b", text_items))):
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
cuts = bool(re.search(r"D-\d+", " ".join(l for l in body.splitlines() if re.search(r"(?i)deadline|срок|cut|сокращ|accept|принят", l)))) or bool(re.search(r"(?im)^## .*(cut|сокращ)", body))
if misses_deadline and not cuts: err("the expected scenario misses the deadline and the document has neither a cuts section nor an accepting decision (D-n)")
out.append("CLARITY %d Must requirement(s) unserved; %d drill(s) unplanned; expected scenario %s the deadline" % (len(unserved), len(undrilled), "misses" if misses_deadline else "meets or has no"))
if agreed and (unserved or undrilled or misses_deadline): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d phases, %d gates, %d tasks, %d epics; hours %g / %g / %g; weeks %.1f / %.1f / %.1f" % (len(PH), len(G), len(TK), len(EP), hsum[0], hsum[1], hsum[2], tot["best"], tot["expected"], tot["worst"]))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
