#!/usr/bin/env python3
"""Resource-math checker and model runner for one zkit project. Stdlib only.
Usage: check_resource_math.py <project-dir> [--update]
  runs <project-dir>/resource-math/model.py (best / expected / worst scenarios + sensitivity), compares the generated
  block between <!-- model:begin --> and <!-- model:end --> in resource-math.md with the fresh output
  (--update rewrites the block), and checks the document against requirements.md and the model. Exit 1 on ERROR.
Model contract (resource-math/model.py): ASSUMPTIONS = {"A-1": {"label","unit","best","expected","worst"}},
  compute(a: {"A-1": value}) -> {result_name: number}, LIMITS = [{"id":"L-1","metric":result_name,"op":"<=",
  "limit":number,"req":"NFR-3","label":"..."}], optional UNITS = {result_name: unit}."""
import re, sys, os, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flow", "scripts"))
try: from ids import rx
except ImportError: sys.exit("ERROR: zkit id registry flow/scripts/ids.py not found: run this script from the zkit plugin, not from a copied skill")

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
update = "--update" in sys.argv
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, req = rdp("resource-math.md"), rdp("requirements.md")
mp = os.path.join(d, "resource-math/model.py")
if not os.path.exists(mp) and os.path.exists(os.path.join(d, "resource_model.py")): mp = os.path.join(d, "resource_model.py")   # legacy layout, before the model moved into its step folder
if doc is None: sys.exit("ERROR: no resource-math.md in %s (pass the project folder)" % d)
if not os.path.exists(mp): sys.exit("ERROR: no resource-math/model.py in %s" % d)
out = []
err = lambda m: out.append("ERROR  " + m)
warn = lambda m: out.append("WARN   " + m)

spec = importlib.util.spec_from_file_location("resource_model", mp); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
A, LIM, UNITS = M.ASSUMPTIONS, M.LIMITS, getattr(M, "UNITS", {})
SC = ("best", "expected", "worst")
fmt = lambda v: "%.4g" % v
ok = lambda l, v: v <= l["limit"] if l["op"] == "<=" else v >= l["limit"]
def run(over=None, base="expected"):
    a = {k: v[base] for k, v in A.items()}; a.update(over or {}); return M.compute(a)
res = {s: run(base=s) for s in SC}
for l in LIM:
    if l["metric"] not in res["expected"]: err("limit %s: metric '%s' is not a result of compute()" % (l["id"], l["metric"]))
    if l["op"] not in ("<=", ">="): err("limit %s: op must be <= or >=" % l["id"])
bad = {s: [l["id"] for l in LIM if l["metric"] in res[s] and not ok(l, res[s][l["metric"]])] for s in SC}

# ---------- generated block
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
if not m: err("no %s ... %s block in resource-math.md (section Model)" % (B0, B1))
elif update:
    doc = doc[:m.start(1)] + "\n" + block + "\n" + doc[m.end(1):]; open(os.path.join(d, "resource-math.md"), "w", encoding="utf-8").write(doc); print("block updated")
elif m.group(1).strip() != block.strip(): err("the generated model block is stale: run with --update (the model or its assumptions changed)")

# ---------- document vs model
def tables(t, idpat):
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(idpat, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")
body = re.sub(re.escape(B0) + r".*?" + re.escape(B1), "", doc, flags=re.S)
dA, dL = tables(body, rx("A") + r"$"), tables(body, rx("L") + r"$")
for ids, rs, name in ((set(A), dA, "assumption"), (set(l["id"] for l in LIM), dL, "limit")):
    got = [r["_id"] for r in rs]
    for i in got:
        if got.count(i) > 1: err("duplicate %s row %s" % (name, i)); break
    for i in sorted(ids - set(got)): err("%s %s is in the model but not in the document tables" % (name, i))
    for i in sorted(set(got) - ids): err("%s %s is in the document but not in the model" % (name, i))
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
else: warn("no requirements.md: limits cannot be checked against requirements")
for r in dA:
    ev = col(r, r"evidence|уровень|достовер").lower()
    if not re.search(r"known|measured|assumed|известно|измерено|допущен", ev): err("%s: evidence level must be known / measured / assumed" % r["_id"])
    if not col(r, r"source|источник").strip(): err("%s has no source" % r["_id"])
    if re.search(r"assumed|допущен", ev) and not col(r, r"validation|проверк|валидац").strip(" —-"): warn("%s is assumed and has no validation" % r["_id"])
accepted = {}
for r in dL:
    rq = col(r, r"requirement|требован")
    if reqs and not any(x in reqs for x in re.findall(rx("FR", "NFR", "C"), rq)): err("%s cites no existing requirement" % r["_id"])
    accepted[r["_id"]] = bool(re.search(rx("D"), col(r, r"accepted|принят")))
for l in LIM:
    if l["id"] in bad["expected"] and not accepted.get(l["id"]): err("%s fails in the EXPECTED scenario and has no accepting decision (D-n): change the requirement or the design, or record the decision" % l["id"])
    elif l["id"] in bad["worst"] and not accepted.get(l["id"]): warn("%s fails in the WORST scenario: record the risk or an accepting decision" % l["id"])
covered = " ".join(col(r, r"requirement|требован") for r in dL)
miss = [k for k, (p, line) in reqs.items() if p == "Must" and k.startswith(("NFR", "C-")) and re.search(r"\d\s*(€|\$|%|ms|мс|s\b|с\b|GB|ГБ|MB|МБ|/)", line) and k not in covered and k not in body]
if miss: warn("numeric Must requirements never mentioned (resource-bound? add a limit or say why not): " + ", ".join(miss))
if "```" in body and re.search(r"```(?:json|yaml|sql|proto)", body): warn("schema-like block; data contracts belong to the contracts and data steps")

# ---------- counts, drift, status, clarity
head = doc.split("\n## ")[0]
cm = re.search(r"(\d+)\s*A\b.*?(\d+)\s*L\b", head)
if not cm or (int(cm.group(1)), int(cm.group(2))) != (len(A), len(LIM)): err("header Counts must read '%d A · %d L' to match the model" % (len(A), len(LIM)))
if req is not None:
    rd = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", req); bd = re.search(r"(?:Основа|Based on):\*\*[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on: requirements.md (date)'")
    elif rd and rd.group(1) > bd.group(1): err("requirements (%s) are newer than the date the math is based on (%s)" % (rd.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
vd = re.search(r"(?:Verdict|Вердикт):\*\*\s*([^\n]+)", head)
if not vd: err("header has no Verdict line (fits / fits with changes / does not fit)")
elif re.search(r"does not fit|не вмещ|не сход", vd.group(1), re.I) and agreed: err("status 'agreed' with the verdict 'does not fit': change requirements or design first")
loose = len([r for r in dA if re.search(r"assumed|допущен", col(r, r"evidence|уровень|достовер").lower()) and not col(r, r"validation|проверк|валидац").strip(" —-")])
unacc = [l["id"] for l in LIM if l["id"] in bad["expected"] and not accepted.get(l["id"])]
out.append("CLARITY %d limit(s) failing in the expected scenario without a decision: %s; %d assumption(s) without a validation" % (len(unacc), ", ".join(unacc) or "-", loose))
if agreed and (unacc or loose): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d assumptions, %d limits; failing: best %s | expected %s | worst %s" % (len(A), len(LIM), len(bad["best"]), len(bad["expected"]), len(bad["worst"])))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
