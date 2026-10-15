#!/usr/bin/env python3
"""Mechanical consistency check: 02-requirements.md vs 01-concept.md and decisions.md.
Usage: check_requirements.py <zkit-docs-dir>   (exit 1 if any ERROR). Stdlib only."""
import re, sys, os

d = sys.argv[1] if len(sys.argv) > 1 else "docs/zkit"
def rd(n):
    p = os.path.join(d, n)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None
req, con, dec = rd("02-requirements.md"), rd("01-concept.md"), rd("decisions.md")
if req is None:
    sys.exit("ERROR: no 02-requirements.md in %s" % d)
out = []
def err(m): out.append("ERROR  " + m)
def warn(m): out.append("WARN   " + m)

# --- parse requirement rows by column name
col = {"priority": r"приоритет|priority", "source": r"источник|source",
       "basis": r"основа|basis", "check": r"критерий|измеря|acceptance|measured"}
rows, hdr = {}, None
for l in req.splitlines():
    if not l.startswith("|"): hdr = None; continue
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
    m = re.match(r"(FR|NFR|C)-(\d+)$", c[0]) if hdr else None
    if not m: continue
    r = {"id": c[0], "kind": m.group(1), "text": " ".join(c)}
    for k, pat in col.items():
        i = next((n for n, h in enumerate(hdr) if re.search(pat, h)), None)
        r[k] = c[i] if i is not None and i < len(c) else None
    if r["id"] in rows: err("duplicate ID " + r["id"])
    rows[r["id"]] = r
reqs = [r for r in rows.values() if r["kind"] != "C"]

# --- row completeness
missing = set()
for r in rows.values():
    if r["kind"] == "C":
        if r["source"] == "": err("%s has no source" % r["id"])
        continue
    if r["priority"] not in ("Must", "Should", "Could"): err("%s: priority '%s' is not Must/Should/Could" % (r["id"], r["priority"]))
    for k in ("check", "source", "basis"):
        if r[k] is None: missing.add(k)
        elif not r[k]: err("%s has empty %s" % (r["id"], k))
    if r["kind"] == "NFR" and not re.search(r"\d", r["text"].split("|")[0] + (r["check"] or "") + r["text"]): warn("%s has no number" % r["id"])

for k in sorted(missing): warn("some requirement table has no %s column (template: ID, requirement, priority, acceptance, source, basis)" % k)

# --- header counts and Must share
head = req.split("\n## ")[0]
for kind in ("FR", "NFR", "C"):
    n = len([r for r in rows.values() if r["kind"] == kind])
    m = re.search(r"(\d+)\s*%s\b" % kind, head)
    if not m or int(m.group(1)) != n: err("header count for %s is '%s', actual %d" % (kind, m.group(1) if m else "missing", n))
cnt = dict((p, len([r for r in reqs if r["priority"] == p])) for p in ("Must", "Should", "Could"))
for p, n in cnt.items():
    m = re.search(r"%s\s*(\d+)" % p, head)
    if not m or int(m.group(1)) != n: err("header %s count is '%s', actual %d" % (p, m.group(1) if m else "missing", n))
if reqs and cnt["Must"] * 100 / len(reqs) > 40:
    warn("Must is %d%% (%d of %d); say why in the doc or cut" % (cnt["Must"] * 100 / len(reqs), cnt["Must"], len(reqs)))

# --- decisions cited exist and are not superseded
if dec is not None:
    known = set(re.findall(r"^###\s*(D-\d+)", dec, re.M))
    dead = set(re.findall(r"^###\s*(D-\d+)\s*\((?:заменено|superseded)", dec, re.M | re.I))
    for dn in sorted(set(re.findall(r"\bD-\d+\b", req))):
        if dn not in known: err("cites %s, not in decisions.md" % dn)
        elif dn in dead: err("cites %s, which is superseded" % dn)

# --- research reports: cited ones exist and are real links; asked-for ones are linked both ways
rdir = os.path.join(d, "research")
files = sorted(os.listdir(rdir)) if os.path.isdir(rdir) else []
for rn in sorted(set(re.findall(r"\[(R-\d+)\]", req))):
    if not any(f.startswith(rn + "-") for f in files): err("cites %s, no such report in research/" % rn)
    elif re.search(r"\[%s\](?!\()" % rn, req): err("%s is cited without a link to research/%s-*.md" % (rn, rn))
for f in files:
    rn = f.split("-")[0] + "-" + f.split("-")[1]
    head_r = open(os.path.join(rdir, f), encoding="utf-8").read().split("\n## ")[0]
    if re.search(r"requirements", head_r, re.I):
        if f not in req: warn("%s was asked by requirements but 02-requirements.md does not link it" % f)
        if "02-requirements.md" not in open(os.path.join(rdir, f), encoding="utf-8").read(): warn("%s has no back-link to 02-requirements.md (Used in)" % f)

# --- cited concept sections exist
if con is not None:
    secs = set(re.findall(r"^##\s*(\d+)\.", con, re.M))
    for s in sorted(set(re.findall(r"(?:concept|концепт)\s*§\s*(\d+)", req, re.I))):
        if s not in secs: err("cites concept §%s, no such section" % s)

# --- traceability: every requirement id appears in the traceability section
tr = re.split(r"(?im)^##\s*\d*\.?\s*(?:трассировка|traceability)", req)
if len(tr) < 2: (err if con is not None else warn)("no traceability section")
else:
    body = re.split(r"(?m)^## ", tr[1])[0]
    # expand ranges like FR-13…FR-16
    ids = set(re.findall(r"(?:FR|NFR|C)-\d+", body))
    for a, b in re.findall(r"((?:FR|NFR)-\d+)\s*[…\-–]+\s*(?:(?:FR|NFR)-)?(\d+)", body):
        k, lo = a.split("-"); ids |= set("%s-%d" % (k, i) for i in range(int(lo), int(b) + 1))
    for i in rows:
        if i.startswith(("FR", "NFR")) and i not in ids: warn("%s is not mentioned in traceability" % i)
    for i in ids:
        if i not in rows: err("traceability mentions %s, which does not exist" % i)

# --- drift and verdict
if con is not None:
    cd = re.search(r"\*\*Дата:\*\*\s*([\d-]+)|\*\*Date:\*\*\s*([\d-]+)", con)
    bd = re.search(r"Основа:\*\*[^\n]*?(\d{4}-\d{2}-\d{2})|Based on:\*\*[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if cd and bd and (cd.group(1) or cd.group(2)) > (bd.group(1) or bd.group(2)): err("concept (%s) is newer than the date the requirements are based on (%s)" % (cd.group(1) or cd.group(2), bd.group(1) or bd.group(2)))
    if not bd: warn("header has no 'Based on: 01-concept.md (date)'")
    v = re.search(r"(Validate first|Build smaller|Buy or reuse|Don't build|Build)\b", con.split("\n## ")[0])
    if v and v.group(1) in ("Validate first",) and not re.search(r"(?i)предусловия?|precondition", req): err("concept verdict is Validate first, but no preconditions")
    if v and not v.group(1) in re.sub(r"\*", "", head): warn("header does not repeat the concept verdict (%s)" % v.group(1))

# --- solution words outside constraints
body = re.split(r"(?im)^##\s*\d*\.?\s*(?:ограничения|constraints)", req)[0]
tech = re.findall(r"(?i)\b(postgres\w*|redis|kafka|rabbitmq|kubernetes|k8s|mongodb|graphql|docker|микросервис\w*)\b", body)
if tech: warn("solution words outside constraints: " + ", ".join(sorted(set(t.lower() for t in tech))))

# --- clarity gate: how much still rests on unconfirmed assumptions
agreed = bool(re.search(r"Status:\*\*\s*(согласовано|agreed)", head, re.I))
loose = [r["id"] for r in reqs if r["priority"] == "Must" and r["basis"] and re.search(r"assumed", r["basis"], re.I) and not re.search(r"confirmed|подтвержд|P-\d", r["basis"], re.I)]
openq = len(re.findall(r"\|\s*open\s*\|?\s*$|\bopen\)?\s*\|?\s*$", req.split("Журнал вопросов")[-1].split("\n## ")[0], re.M | re.I)) if re.search(r"Журнал вопросов|Interview log", req) else 0
out.append("CLARITY %d Must requirement(s) rest on unconfirmed assumptions: %s; %d open question(s) in the log" % (len(loose), ", ".join(loose) or "-", openq))
if agreed and (loose or openq): err("status is 'agreed' but clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d requirements, %d constraints checked" % (len(reqs), len(rows) - len(reqs)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
