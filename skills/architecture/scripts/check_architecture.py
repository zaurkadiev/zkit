#!/usr/bin/env python3
"""Mechanical consistency check: architecture.md vs requirements, concept, decisions, resource-math, contracts and data of one project.
Usage: check_architecture.py <project-dir>   (e.g. docs/zkit/mvp; exit 1 if any ERROR). Stdlib only.
Documents of the project: architecture.md (older name: high-level-design.md), requirements.md, concept.md, decisions.md, resource-math.md,
contracts.md, data.md, research/R-<n>-<slug>.md."""
import re, sys, os

d = sys.argv[1] if len(sys.argv) > 1 else "docs/zkit"
def rdp(n): p = os.path.join(d, n); return open(p, encoding="utf-8").read() if os.path.exists(p) else None
hld, req, con, dec = rdp("architecture.md"), rdp("requirements.md"), rdp("concept.md"), rdp("decisions.md")
rm, ct, dt = rdp("resource-math.md"), rdp("contracts.md"), rdp("data.md")
legacy = hld is None and rdp("high-level-design.md") is not None
if legacy: hld = rdp("high-level-design.md")
if hld is None: sys.exit("ERROR: no architecture.md in %s (pass the project folder, e.g. docs/zkit/mvp)" % d)
out = []
def err(m): out.append("ERROR  " + m)
def warn(m): out.append("WARN   " + m)
if legacy: warn("high-level-design.md is the older name of this document: rename it to architecture.md")

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

# ---------- C4 diagrams (Mermaid): level 1 context, level 2 containers (all parts), level 3 for risky parts
blocks = []
for m in re.finditer(r"(?m)^(#+[^\n]*)\n(?:(?!^#)[^\n]*\n)*?```mermaid\n(.*?)```", hld, re.S): blocks.append((m.group(1).lower(), m.group(2)))
if not blocks:
    mm = re.search(r"```mermaid\n(.*?)```", hld, re.S)
    if mm: blocks.append(("level 2", mm.group(1)))
lv = lambda pat: [b for h, b in blocks if re.search(pat, h)]
l1, l2, l3 = lv(r"level 1|уровень 1|context|контекст"), lv(r"level 2|уровень 2|container|контейнер|структур|structure"), lv(r"level 3|уровень 3|component|компонент")
if not blocks: err("no Mermaid diagram")
else:
    if not l1: err("no C4 level 1 (context) diagram: people and external systems around the system")
    if not l2: err("no C4 level 2 (containers) diagram: all parts, infrastructure nodes, links labelled with interfaces")
    if not l3: warn("no C4 level 3 diagram: draw components for the 1-2 parts whose internal structure carries a requirement")
    dg = "\n".join(l2) if l2 else blocks[0][1]
    nodes = set("B-" + x for x in re.findall(r"\bB(\d+)\b", dg)) | set(re.findall(r"B-\d+", dg))
    for b in B:
        if b not in nodes: err("%s is not in the level 2 diagram" % b)
    for b in nodes:
        if b not in B: err("diagram node %s has no row in the parts table" % b)
    labels = set(re.findall(r"I-\d+", dg))
    for i in I:
        if i not in labels: warn("%s is not shown as a labelled arrow in the level 2 diagram" % i)
    for i in labels:
        if i not in I: err("diagram arrow %s has no row in the interfaces table" % i)
    for b in l3:
        for n in set("B-" + x for x in re.findall(r"\bB(\d+)\b", b)) | set(re.findall(r"B-\d+", b)):
            if n not in B: err("level 3 diagram mentions %s, which is not a part" % n)
    xs_known = set(re.findall(r"\bX-\d+\b", ct)) if ct else set()
    for x in sorted(set(re.findall(r"\bX(?:-|)(\d+)\b", "\n".join(l1 + l2)))):
        if xs_known and "X-" + x not in xs_known: err("diagram mentions X-%s, which is not a boundary in contracts.md" % x)

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
    if re.search(r"high-level|hld", rt.split("\n## ")[0], re.I) and f not in hld: warn("%s was asked by architecture but the document does not link it" % f)
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
skip = ("стек", "stack", "technology", "ключевые решения", "key decisions", "ограничен", "constraint", "источники", "sources", "отложено", "deferred", "риск", "risk")
body = "\n".join(v for k, v in S.items() if not any(s in k for s in skip))
body = re.sub(r"```.*?```", "", body, flags=re.S)
tech = sorted(set(t.lower() for t in re.findall(tech_re, body)))
if tech: warn("technology words outside decisions and constraints (contracts or mechanics?): " + ", ".join(tech))
if re.search(r"```(?:json|yaml|yml|sql|proto|graphql)\b", hld): warn("schema-like code block; field-level contracts belong to contracts")

# ---------- inputs of the earlier steps: boundaries handled, data owned once, limits carried
body_struct = "\n".join(v for k, v in S.items() if re.search(r"част|parts|интерфейс|interface|c4|структур|structure|контейнер|container|контекст|context", k))
unhandled, unowned = [], []
if ct:
    for x in sorted(set(r for r in re.findall(r"^\|\s*(X-\d+)\s*\|", ct, re.M))):
        if x not in body_struct: unhandled.append(x); err("boundary %s of contracts.md is not handled by any part or interface (name it in the parts, interfaces or C4 diagrams)" % x)
if dt:
    ents = sorted(set(re.findall(r"^\|\s*(E-\d+)\s*\|", dt, re.M)))
    owns = {e: [b for b, r in B.items() if re.search(r"\b%s\b" % e, pick(r, r"owns|владеет|состоян|state") or "") or e in expand(pick(r, r"owns|владеет|состоян|state") or "")] for e in ents}
    for e, bs in owns.items():
        if not bs: unowned.append(e); err("entity %s of data.md has no owning part (put it in a part's 'Owns' cell)" % e)
        elif len(bs) > 1: err("entity %s has several owners: %s (exactly one part owns each piece of state)" % (e, ", ".join(bs)))
if rm:
    for l in sorted(set(re.findall(r"^\|\s*(L-\d+)\s*\|", rm, re.M))):
        if not re.search(r"\b%s\b" % l, hld): warn("limit %s of resource-math is not carried by any part or scenario (cite it where the structure serves it)" % l)
for nm, text in (("resource-math", rm), ("contracts", ct), ("data", dt)):
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the architecture is based on (%s)" % (nm, rdte.group(1), bd.group(1)))

# ---------- clarity gate
agreed = bool(re.search(r"Status:\*\*\s*(согласовано|agreed)|Статус:\*\*\s*(согласовано|agreed)", head, re.I))
uncovered = sorted(r for r, p in reqs.items() if p == "Must" and (r not in covered or not covered[r]))
kd = sec("ключевые решения", "key decisions")
open_forks = len([l for l in kd.splitlines() if l.startswith("|") and re.search(r"(?i)\btbd\b|\bopen (question|fork)\b|не решено|открыт(ый|ая|ое) (вопрос|развилк)|развилка открыта", l)])
risks = "\n".join(sec("риски", "risks").split("\n")[1:])   # skip the heading line
loose = len([l for l in risks.splitlines() if re.search(r"(?i)assumed|допущени", l) and not re.search(r"(?i)validat|валидир|проверк|spike|замер|измер|P-\d|пилот|pilot", l)])
out.append("CLARITY %d Must requirement(s) without a covering part: %s; %d open fork(s); %d architectural assumption(s) without a validation; %d boundary(ies) unhandled; %d entity(ies) unowned" % (len(uncovered), ", ".join(uncovered) or "-", open_forks, loose, len(unhandled), len(unowned)))
if agreed and (uncovered or open_forks or loose or unhandled or unowned): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d parts, %d interfaces, %d scenarios, %d requirements known" % (len(B), len(I), len(Sc), len(reqs)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
