#!/usr/bin/env python3
"""Resilience checker and model runner for one zkit project. Stdlib only.
Usage: check_resilience.py <project-dir> [--update]
  resilience.md (fault and threat register F-n/T-n, observability O-n, drills DR-n, numeric limits RL-n) +
  resilience_model.py (availability, RPO, RTO; best / expected / worst) vs architecture, data, contracts, requirements.
  --update rewrites the generated block between <!-- model:begin --> and <!-- model:end -->. Exit 1 on ERROR.
Model contract (resilience_model.py): ASSUMPTIONS = {"RA-1": {"label","unit","best","expected","worst"}},
  compute(a) -> {result: number}, LIMITS = [{"id":"RL-1","metric":result,"op":"<=|>=","limit":number,"req":"NFR-11","label":..}], optional UNITS."""
import re, sys, os, importlib.util

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
update = "--update" in sys.argv
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, req, arch, dt, ct = rdp("resilience.md"), rdp("requirements.md"), rdp("architecture.md"), rdp("data.md"), rdp("contracts.md")
mp = os.path.join(d, "resilience_model.py")
if doc is None: sys.exit("ERROR: no resilience.md in %s (pass the project folder)" % d)
out = []
err = lambda m: out.append("ERROR  " + m)
warn = lambda m: out.append("WARN   " + m)

# ---------- model, scenarios, generated block
A, LIM, UNITS, bad = {}, [], {}, {s: [] for s in ("best", "expected", "worst")}
SC = ("best", "expected", "worst")
fmt = lambda v: "%.4g" % v
ok = lambda l, v: v <= l["limit"] if l["op"] == "<=" else v >= l["limit"]
if not os.path.exists(mp): err("no resilience_model.py in %s" % d)
else:
    sp = importlib.util.spec_from_file_location("resilience_model", mp); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
    A, LIM, UNITS = M.ASSUMPTIONS, M.LIMITS, getattr(M, "UNITS", {})
    run = lambda over=None, base="expected": M.compute(dict({k: v[base] for k, v in A.items()}, **(over or {})))
    res = {s: run(base=s) for s in SC}
    for l in LIM:
        if l["metric"] not in res["expected"]: err("limit %s: metric '%s' is not a result of compute()" % (l["id"], l["metric"]))
        if l["op"] not in ("<=", ">="): err("limit %s: op must be <= or >=" % l["id"])
    bad = {s: [l["id"] for l in LIM if l["metric"] in res[s] and not ok(l, res[s][l["metric"]])] for s in SC}
    rows = ["**Results**", "", "| Result | Unit | Best | Expected | Worst |", "|---|---|---|---|---|"]
    for k in res["expected"]: rows.append("| %s | %s | %s |" % (k, UNITS.get(k, ""), " | ".join(fmt(res[s][k]) for s in SC)))
    rows += ["", "**Limits**", "", "| ID | Metric | Limit | Best | Expected | Worst |", "|---|---|---|---|---|---|"]
    for l in LIM:
        cells = ["%s %s" % (fmt(res[s][l["metric"]]), "✓" if ok(l, res[s][l["metric"]]) else "✗") for s in SC if l["metric"] in res[s]]
        rows.append("| %s | %s | %s %s | %s |" % (l["id"], l["metric"], l["op"], fmt(l["limit"]), " | ".join(cells)))
    sens = []
    for k in A:
        r = run({k: A[k]["worst"]})
        for l in LIM:
            b, v = res["expected"][l["metric"]], r[l["metric"]]
            if b: sens.append((abs(v - b) / abs(b), k, l["id"], (v - b) / b))
    sens.sort(reverse=True); seen, top = set(), []
    for s in sens:
        if s[1] not in seen and s[0] > 0: seen.add(s[1]); top.append(s)
    rows += ["", "**Sensitivity** (one assumption at its worst value, others expected; the limit it moves most)", "", "| Assumption | Limit | Change of the metric |", "|---|---|---|"]
    for s in top[:5]: rows.append("| %s | %s | %+.0f%% |" % (s[1], s[2], s[3] * 100))
    block = "\n".join(rows)
    B0, B1 = "<!-- model:begin -->", "<!-- model:end -->"
    m = re.search(re.escape(B0) + r"(.*?)" + re.escape(B1), doc, re.S)
    if not m: err("no %s ... %s block in resilience.md" % (B0, B1))
    elif update:
        doc = doc[:m.start(1)] + "\n" + block + "\n" + doc[m.end(1):]; open(os.path.join(d, "resilience.md"), "w", encoding="utf-8").write(doc); print("block updated")
    elif m.group(1).strip() != block.strip(): err("the generated model block is stale: run with --update")

# ---------- helpers
def tables(t, idpat):
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(idpat, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")
body = re.sub(r"<!-- model:begin -->.*?<!-- model:end -->", "", doc, flags=re.S)
F, T, O, DR = tables(body, r"F-\d+$"), tables(body, r"T-\d+$"), tables(body, r"O-\d+$"), tables(body, r"DR-\d+$")
dA, dL = tables(body, r"RA-\d+$"), tables(body, r"RL-\d+$")
reqs = {}
if req is not None:
    hdr = None
    for l in req.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(r"(FR|NFR|C)-\d+$", c[0]):
            i = next((n for n, h in enumerate(hdr) if re.search(r"приоритет|priority", h)), None)
            reqs[c[0]] = (c[i] if i is not None and i < len(c) else "", l)
else: warn("no requirements.md: serving requirements cannot be checked")

# ---------- register rows
if not F: err("no fault rows (F-n)")
if not T: err("no threat rows (T-n)")
ids = [r["_id"] for r in F + T + O + DR + dA + dL]
for i in set(ids):
    if ids.count(i) > 1: err("duplicate id %s" % i)
okeys = set(r["_id"] for r in O)
drills_for = set()
for r in DR: drills_for |= set(re.findall(r"[FT]-\d+", col(r, r"covers|проверя|регистр")))
targets = set()
for r in F + T:
    i = r["_id"]
    for k, pat in (("target", r"target|цел|объект"), ("failure/threat", r"fail|threat|отказ|угроз"), ("severity", r"severity|серьёз|тяжест"), ("response", r"response|реакц"), ("detection", r"detect|обнаруж")):
        if not col(r, pat).strip(" —-"): err("%s has no %s" % (i, k))
    tg = re.findall(r"\b(?:B|I|X|E)-\d+\b", col(r, r"target|цел|объект")); targets |= set(tg)
    if not tg: err("%s names no target (B-/I-/X-/E- id)" % i)
    sv = col(r, r"severity|серьёз|тяжест").strip()
    if not re.match(r"(H|M|L|выс|сред|низ)", sv, re.I): warn("%s: severity should be H / M / L" % i)
    for o in re.findall(r"O-\d+", col(r, r"detect|обнаруж")):
        if o not in okeys: err("%s cites detection %s, not in the observability table" % (i, o))
    if not re.search(r"O-\d+", col(r, r"detect|обнаруж")): warn("%s has no detection signal (O-n): it would fail silently" % i)
    sr = re.findall(r"(?:FR|NFR|C)-\d+", col(r, r"serves|обслужив|требован"))
    if not sr: warn("%s protects no requirement" % i)
    for s in sr:
        if reqs and s not in reqs: err("%s cites %s, not in requirements" % (i, s))
    if re.match(r"(H|выс)", sv, re.I) and i not in drills_for: err("%s is high severity and has no drill (DR-n covering it)" % i)
for r in O:
    if not re.search(r"B-\d+", col(r, r"where|emitted|источн|част")): warn("%s names no emitting part" % r["_id"])
for r in DR:
    for k, pat in (("how", r"how|как|способ"), ("success criterion", r"success|критер")):
        if not col(r, pat).strip(" —-"): err("%s has no %s" % (r["_id"], k))
    for x in re.findall(r"[FT]-\d+", col(r, r"covers|проверя|регистр")):
        if x not in set(q["_id"] for q in F + T): err("%s covers %s, which does not exist" % (r["_id"], x))

# ---------- coverage of the architecture, contracts and data
if arch is not None:
    allt = set(re.findall(r"^\|\s*((?:B|I)-\d+)\s*\|", arch, re.M))
else: allt = set(); warn("no architecture.md: coverage of parts and interfaces cannot be checked")
allt |= set(re.findall(r"^\|\s*(X-\d+)\s*\|", ct or "", re.M)) | set(re.findall(r"^\|\s*(E-\d+)\s*\|", dt or "", re.M))
na = set(re.findall(r"\b(?:B|I|X|E)-\d+\b", "\n".join(v for k, v in re.findall(r"(?ims)^## (\d*\.?\s*(?:not applicable|не применим|вне реестра)[^\n]*)\n(.*?)(?=^## |\Z)", doc))))
unc = sorted(t for t in allt if t not in targets and t not in na)
for t in unc: err("%s is not a target of any fault or threat row and is not listed as not applicable (with a reason)" % t)

# ---------- model vs document tables
if A:
    for ids_, rs, nm in ((set(A), dA, "assumption"), (set(l["id"] for l in LIM), dL, "limit")):
        got = [r["_id"] for r in rs]
        for i in sorted(ids_ - set(got)): err("%s %s is in the model but not in the document tables" % (nm, i))
        for i in sorted(set(got) - ids_): err("%s %s is in the document but not in the model" % (nm, i))
    for r in dA:
        ev = col(r, r"evidence|уровень|достовер").lower()
        if not re.search(r"known|measured|assumed|известно|измерено|допущен", ev): err("%s: evidence must be known / measured / assumed" % r["_id"])
        if not col(r, r"source|источник").strip(): err("%s has no source" % r["_id"])
accepted = {}
for r in dL:
    rq = col(r, r"requirement|требован")
    if reqs and not any(x in reqs for x in re.findall(r"(?:FR|NFR|C)-\d+", rq)): err("%s cites no existing requirement" % r["_id"])
    accepted[r["_id"]] = bool(re.search(r"D-\d+", col(r, r"accepted|принят")))
for l in LIM:
    if l["id"] in bad["expected"] and not accepted.get(l["id"]): err("%s fails in the EXPECTED scenario and has no accepting decision (D-n)" % l["id"])
    elif l["id"] in bad["worst"] and not accepted.get(l["id"]): warn("%s fails in the WORST scenario: record the risk or an accepting decision" % l["id"])
kw = r"(?i)доступн|availab|uptime|восстанов|recover|rpo|rto|резервн|backup|безопасн|security|изоляц|isolat|секрет|secret|приватн|privacy|утечк|leak|аудит|audit|отказ|fail|надёжн|reliab"
miss = [k for k, (p, l) in reqs.items() if p == "Must" and re.search(kw, l) and not k.startswith("C-") and k not in doc]
if miss: warn("Must requirements about reliability/security never mentioned (add a row, a limit, or say why not): " + ", ".join(miss))

# ---------- counts, drift, status, clarity
head = doc.split("\n## ")[0]
cm = re.search(r"(\d+)\s*F\b.*?(\d+)\s*T\b", head)
if not cm or (int(cm.group(1)), int(cm.group(2))) != (len(F), len(T)): err("header Counts must read '%d F · %d T' to match the register" % (len(F), len(T)))
for nm, text in (("requirements", req), ("architecture", arch), ("data", dt), ("contracts", ct)):
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the resilience is based on (%s)" % (nm, rdte.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
nodrill = [r["_id"] for r in F + T if re.match(r"(H|выс)", col(r, r"severity|серьёз|тяжест").strip(), re.I) and r["_id"] not in drills_for]
unacc = [l["id"] for l in LIM if l["id"] in bad["expected"] and not accepted.get(l["id"])]
out.append("CLARITY %d target(s) of architecture/contracts/data not covered; %d high-severity row(s) without a drill; %d limit(s) failing in the expected scenario without a decision: %s" % (len(unc), len(nodrill), len(unacc), ", ".join(unacc) or "-"))
if agreed and (unc or nodrill or unacc): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d faults, %d threats, %d signals, %d drills, %d assumptions, %d limits; failing: best %d | expected %d | worst %d" % (len(F), len(T), len(O), len(DR), len(A), len(LIM), len(bad["best"]), len(bad["expected"]), len(bad["worst"])))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
