#!/usr/bin/env python3
"""Mechanical consistency check: high-level-design.md vs requirements.md, concept.md and decisions.md of one project.
Usage: check_hld.py <project-dir>   (e.g. docs/zkit/mvp; exit 1 if any ERROR). Stdlib only.
Documents of the project: high-level-design.md, requirements.md, concept.md, decisions.md, research/R-<n>-<slug>.md."""
import re, sys, os

d = sys.argv[1] if len(sys.argv) > 1 else "docs/zkit"
def rdp(n): p = os.path.join(d, n); return open(p, encoding="utf-8").read() if os.path.exists(p) else None
hld, req, con, dec = rdp("high-level-design.md"), rdp("requirements.md"), rdp("concept.md"), rdp("decisions.md")
if hld is None: sys.exit("ERROR: no high-level-design.md in %s (pass the project folder, e.g. docs/zkit/mvp)" % d)
out = []
def err(m): out.append("ERROR  " + m)
def warn(m): out.append("WARN   " + m)

def sections(t):
    parts = re.split(r"(?m)^## ", t)
    return {re.sub(r"^\d+\.\s*", "", p.split("\n")[0]).strip().lower(): p for p in parts[1:]}
S = sections(hld)
def sec(*names):
    for k, v in S.items():
        if any(re.search(n, k) for n in names): return v
    return ""

def expand(text):
    ids = set(re.findall(r"\b(?:FR|NFR|C|B|I|S)-\d+\b", text))
    for a, b in re.findall(r"((?:FR|NFR|B|I|S)-\d+)\s*[…\-–]+\s*(?:(?:FR|NFR|B|I|S)-)?(\d+)", text):
        k, lo = a.split("-")
        if int(b) >= int(lo): ids |= set("%s-%d" % (k, i) for i in range(int(lo), int(b) + 1))
    return ids

def tables(t, idpat):
    """rows of every table whose first column matches idpat: list of (dict by lowercase header, cells)"""
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(idpat, c[0]): rows.append(({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, c))
    return rows
def pick(row, pat):
    for h, v in row[0].items():
        if re.search(pat, h): return v
    return None

# ---------- requirements: ids and priorities
reqs = {}
if req is not None:
    rh = None
    for l in req.splitlines():
        if not l.startswith("|"): rh = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": rh = [x.lower() for x in c]; continue
        if rh and re.match(r"(FR|NFR|C)-\d+$", c[0]):
            i = next((n for n, h in enumerate(rh) if re.search(r"приоритет|priority", h)), None)
            reqs[c[0]] = c[i] if i is not None and i < len(c) else ""
else:
    warn("no requirements.md: traceability cannot be checked against requirements")

# ---------- parts, interfaces, scenarios
B = {r[1][0]: r for r in tables(sec("части", "parts", "building"), r"B-\d+$")}
I = {r[1][0]: r for r in tables(sec("интерфейс", "interface"), r"I-\d+$")}
Sc = {r[1][0]: r for r in tables(sec("сценари", "scenario"), r"S-\d+$")}
for name, kind, rr in (("part", "B", B), ("interface", "I", I), ("scenario", "S", Sc)):
    allrows = tables(sec({"B": "части|parts|building", "I": "интерфейс|interface", "S": "сценари|scenario"}[kind]), r"%s-\d+$" % kind)
    seen = set()
    for r in allrows:
        if r[1][0] in seen: err("duplicate %s ID %s" % (name, r[1][0]))
        seen.add(r[1][0])
if not B: err("no parts table (B-n rows)")

for bid, r in B.items():
    if not (pick(r, r"ответственн|responsib") or "").strip(): err("%s has no responsibility" % bid)
    serves = pick(r, r"обслужив|покрыва|serves|требован") or ""
    if not re.search(r"(FR|NFR|C)-\d+", serves): err("%s serves no requirement (orphan part: justify in the document or cut)" % bid)
    for x in expand(serves):
        if reqs and x.split("-")[0] in ("FR", "NFR", "C") and x not in reqs: err("%s serves %s, which is not in requirements" % (bid, x))
for iid, r in I.items():
    ends = re.findall(r"B-\d+", pick(r, r"от|from") or "")
    if len(ends) < 2: err("%s: 'from → to' must name two parts (B-n)" % iid)
    for e in ends:
        if e not in B: err("%s refers to %s, which does not exist" % (iid, e))
    serves = pick(r, r"обслужив|покрыва|serves|требован") or ""
    if not re.search(r"(FR|NFR|C)-\d+", serves): warn("%s serves no requirement" % iid)
    for x in expand(serves):
        if reqs and x.split("-")[0] in ("FR", "NFR", "C") and x not in reqs: err("%s serves %s, which is not in requirements" % (iid, x))
for sid, r in Sc.items():
    steps = pick(r, r"шаги|steps") or ""
    for x in re.findall(r"[BI]-\d+", steps):
        if x not in B and x not in I: err("%s step uses %s, which does not exist" % (sid, x))
    if not re.search(r"[BI]-\d+", steps): err("%s has no steps through parts or interfaces" % sid)
    if not (pick(r, r"итог|outcome") or "").strip(): err("%s has no outcome against requirements" % sid)
if Sc:
    if not 3 <= len(Sc) <= 6: warn("%d scenarios; 3-5 are expected" % len(Sc))
    if not any(re.search(r"(?i)сбой|отказ|рестарт|перезапуск|исчерпан|вредонос|недоступн|failure|restart|exhaust|hostile|unavailab|crash", " ".join(r[1])) for r in Sc.values()):
        warn("no failure or hard-requirement scenario among the scenarios")
else:
    err("no scenarios (S-n rows)")

# ---------- header counts
head = hld.split("\n## ")[0]
for kind, n in (("B", len(B)), ("I", len(I)), ("S", len(Sc))):
    m = re.search(r"(\d+)\s*%s\b" % kind, head)
    if not m or int(m.group(1)) != n: err("header count for %s is '%s', actual %d" % (kind, m.group(1) if m else "missing", n))

# ---------- diagram
mm = re.search(r"```mermaid\n(.*?)```", hld, re.S)
if not mm: err("no Mermaid diagram")
else:
    dg = mm.group(1)
    nodes = set("B-" + x for x in re.findall(r"\bB(\d+)\b", dg)) | set(re.findall(r"B-\d+", dg))
    for b in B:
        if b not in nodes: err("%s is not in the diagram" % b)
    for b in nodes:
        if b not in B: err("diagram node %s has no row in the parts table" % b)
    labels = set(re.findall(r"I-\d+", dg))
    for i in I:
        if i not in labels: warn("%s is not shown as a labelled arrow in the diagram" % i)
    for i in labels:
        if i not in I: err("diagram arrow %s has no row in the interfaces table" % i)

# ---------- traceability
tr = sec("трассировка", "traceability")
covered = {}
if not tr: err("no traceability section")
else:
    for l in tr.splitlines():
        if not l.startswith("|"): continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) < 2 or re.match(r"[-: ]+$", c[0]) or c[0].lower().startswith(("requirement", "требован")): continue
        left, right = expand(c[0]), c[1]
        for rid in left:
            if reqs and rid not in reqs and rid.split("-")[0] in ("FR", "NFR", "C"): err("traceability mentions %s, which is not in requirements" % rid)
            covered.setdefault(rid, set()).update(re.findall(r"\b[BID]-\d+\b", right))
            if re.search(r"(?i)uncovered|не покрыт|вне v1|later|позже", right) and not re.search(r"\b[BI]-\d+", right): covered[rid] = set()
        for x in re.findall(r"\b[BI]-\d+\b", right):
            if x not in B and x not in I: err("traceability points to %s, which does not exist" % x)
    for rid, targets in covered.items():
        for b in [t for t in targets if t.startswith("B-") and t in B]:
            serves = expand(pick(B[b], r"обслужив|покрыва|serves|требован") or "")
            if rid.split("-")[0] != "C" and rid not in serves and not any(rid in expand(pick(i, r"обслужив|покрыва|serves|требован") or "") for i in I.values()):
                warn("traceability says %s covers %s, but the part's own row does not list it" % (b, rid))
    for rid, p in reqs.items():
        if rid.startswith("C-"): continue
        if p == "Must" and rid not in covered: err("Must requirement %s is not in the traceability table" % rid)
        elif p != "Must" and rid not in covered: warn("%s is not mentioned in traceability" % rid)
    for b in B:
        if not any(b in t for t in covered.values()): warn("%s is not used in any traceability row" % b)

# ---------- decisions: exist, not superseded, links
known = set(re.findall(r"^###\s*(D-\d+)", dec or "", re.M))
anchors = set(re.findall(r'<a id="(D-\d+)"></a>', dec or ""))
dead = set()
if dec:
    for m in re.finditer(r"^###\s*(D-\d+)[^\n]*\n(?:> \*\*Статус:\*\*\s*([^\n]*))?", dec, re.M):
        if re.search(r"заменено|superseded", (m.group(2) or "") + m.group(0).split("\n")[0], re.I): dead.add(m.group(1))
    for dn in sorted(set(re.findall(r"\bD-\d+\b", hld))):
        if dn not in known: err("cites %s, not in decisions" % dn)
        elif dn in dead: err("cites %s, which is superseded" % dn)
    text = re.sub(r"```.*?```", "", "\n".join(l for l in hld.split("\n") if not l.startswith(("#", ">"))), flags=re.S)
    bare = sorted(set(re.findall(r"(?<![\w\[/(#-])(D-\d+)(?![\w\]-])(?!\]\()", text)))
    if bare: err("decisions cited without a link: " + ", ".join(bare) + " (run link_docs.py)")
    for dn, frag in re.findall(r"\[(D-\d+)\]\([^)#]*#([^)]*)\)", hld):
        if frag != dn or dn not in anchors: err("link for %s points to a missing anchor #%s" % (dn, frag))
    kd = sec("ключевые решения", "key decisions")
    if kd and not re.search(r"\bD-\d+\b", kd): warn("key decisions section cites no D-n")
elif re.search(r"\bD-\d+\b", hld): warn("cites decisions, but there is no decisions.md")

# ---------- research reports and relative links
rdir = os.path.join(d, "research")
files = sorted(os.listdir(rdir)) if os.path.isdir(rdir) else []
for rn in sorted(set(re.findall(r"\[(R-\d+)\]", hld))):
    if not any(f.startswith(rn + "-") for f in files): err("cites %s, no such report in research/" % rn)
    elif re.search(r"\[%s\](?!\()" % rn, hld): err("%s is cited without a link to research/%s-*.md" % (rn, rn))
for f in files:
    rt = open(os.path.join(rdir, f), encoding="utf-8").read()
    if re.search(r"high-level|hld", rt.split("\n## ")[0], re.I) and f not in hld: warn("%s was asked by high-level design but the document does not link it" % f)
for tgt in re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", hld):
    if not tgt.startswith("http") and not os.path.exists(os.path.normpath(os.path.join(d, tgt))): err("broken link: " + tgt)

# ---------- requirement ids and concept sections cited exist
if reqs:
    for x in sorted(set(re.findall(r"\b(?:FR|NFR)-\d+\b", hld))):
        if x not in reqs: err("cites %s, which is not in requirements" % x)
if con is not None:
    secs = set(re.findall(r"^##\s*(\d+)\.", con, re.M))
    for s in sorted(set(re.findall(r"(?:concept|концепт)\s*§\s*(\d+)", hld, re.I))):
        if s not in secs: err("cites concept §%s, no such section" % s)

# ---------- drift and status of the base
if req is not None:
    rd = re.search(r"\*\*Дата:\*\*\s*([\d-]+)|\*\*Date:\*\*\s*([\d-]+)", req)
    bd = re.search(r"Основа:\*\*[^\n]*?(\d{4}-\d{2}-\d{2})|Based on:\*\*[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on: requirements.md (date)'")
    elif rd and (rd.group(1) or rd.group(2)) > (bd.group(1) or bd.group(2)):
        err("requirements (%s) are newer than the date the design is based on (%s)" % (rd.group(1) or rd.group(2), bd.group(1) or bd.group(2)))
    if not re.search(r"Status:\*\*\s*(согласовано|agreed)|Статус:\*\*\s*(согласовано|agreed)", req.split("\n## ")[0], re.I):
        warn("requirements are not marked agreed; the design rests on a draft")

# ---------- details that belong to later stages
tech_re = r"(?i)\b(postgres\w*|mysql|sqlite|mongodb|redis|kafka|rabbitmq|nats|python|golang|typescript|node\.?js|rust|java|kubernetes|k8s|docker|graphql|grpc|protobuf|terraform|aws|gcp|azure)\b"
skip = ("ключевые решения", "key decisions", "ограничен", "constraint", "источники", "sources", "отложено", "deferred", "риск", "risk")
body = "\n".join(v for k, v in S.items() if not any(s in k for s in skip))
body = re.sub(r"```.*?```", "", body, flags=re.S)
tech = sorted(set(t.lower() for t in re.findall(tech_re, body)))
if tech: warn("technology words outside decisions and constraints (design-details?): " + ", ".join(tech))
if re.search(r"```(?:json|yaml|yml|sql|proto|graphql)\b", hld): warn("schema-like code block; field-level contracts belong to design-details")

# ---------- clarity gate
agreed = bool(re.search(r"Status:\*\*\s*(согласовано|agreed)|Статус:\*\*\s*(согласовано|agreed)", head, re.I))
uncovered = sorted(r for r, p in reqs.items() if p == "Must" and (r not in covered or not covered[r]))
kd = sec("ключевые решения", "key decisions")
open_forks = len([l for l in kd.splitlines() if l.startswith("|") and re.search(r"(?i)\b(tbd|open)\b|не решено|открыт", l)])
risks = "\n".join(sec("риски", "risks").split("\n")[1:])   # skip the heading line
loose = len([l for l in risks.splitlines() if re.search(r"(?i)assumed|допущени", l) and not re.search(r"(?i)validat|валидир|проверк|spike|замер|измер|P-\d|пилот|pilot", l)])
out.append("CLARITY %d Must requirement(s) without a covering part: %s; %d open fork(s); %d architectural assumption(s) without a validation" % (len(uncovered), ", ".join(uncovered) or "-", open_forks, loose))
if agreed and (uncovered or open_forks or loose): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d parts, %d interfaces, %d scenarios, %d requirements known" % (len(B), len(I), len(Sc), len(reqs)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
