#!/usr/bin/env python3
"""Mechanical check of ux.md (human-facing surfaces and journeys) against requirements and resource-math of one zkit project.
Usage: check_ux.py <project-dir>   (exit 1 on ERROR). Stdlib only."""
import re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flow", "scripts"))
try: from ids import rx
except ImportError: sys.exit("ERROR: zkit id registry flow/scripts/ids.py not found: run this script from the zkit plugin, not from a copied skill")

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, req, rm = rdp("ux.md"), rdp("requirements.md"), rdp("resource-math.md")
if doc is None: sys.exit("ERROR: no ux.md in %s (pass the project folder)" % d)
out = []
err = lambda m: out.append("ERROR  " + m)
warn = lambda m: out.append("WARN   " + m)

def sections(t):
    return {re.sub(r"^\d+\.\s*", "", p.split("\n")[0]).strip().lower(): p for p in re.split(r"(?m)^## ", t)[1:]}
S = sections(doc)
def sec(*names):
    for k, v in S.items():
        if any(re.search(n, k) for n in names): return v
    return ""
def tables(t, idpat):
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() in ("id", "surface", "поверхность"): hdr = [x.lower() for x in c]; continue
        if hdr and re.match(idpat, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")
empty = lambda v: not v.strip(" —-")

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
limits = set(re.findall(r"\b" + rx("L") + r"\b", rm)) if rm else set()

U = tables(sec("поверхност", "surface"), rx("U") + r"$")
J = tables(sec("сценари", "journey"), rx("J") + r"$")
ST = tables(sec("состояни", "states"), rx("U") + r"$")
if not U: err("no surface rows (U-n)")
if not J: err("no journey rows (J-n)")
uids, used, served = set(), set(), set()
KINDS = r"screen|page|cli|command|console|tui|chat|notification|config|voice|controls|экран|страниц|консол|чат|уведомл|конфиг|голос|управлени"
INTERACTIVE = r"screen|page|cli|command|console|tui|chat|voice|controls|экран|страниц|консол|чат|голос|управлени"
for r in U:
    u = r["_id"]
    if u in uids: err("duplicate surface %s" % u)
    uids.add(u)
    if not re.search(KINDS, col(r, r"kind|вид|тип"), re.I): err("%s: kind must be screen / cli / console / chat / notification / config / voice / controls" % u)
    if empty(col(r, r"actor|актор")): err("%s has no actor" % u)
    sv = col(r, r"serves|обслужив|требован")
    if not re.search(rx("FR", "NFR", "C"), sv): err("%s serves no requirement" % u)
    for s in re.findall(rx("FR", "NFR", "C"), sv):
        served.add(s)
        if reqs and s not in reqs: err("%s serves %s, which is not in requirements" % (u, s))
    b = col(r, r"budget|бюджет")
    if re.search(INTERACTIVE, col(r, r"kind|вид|тип"), re.I) and not (re.search(r"\d", b) or re.search(rx("L"), b)): warn("%s: interactive surface without a feedback budget (a figure or a resource-math L-n)" % u)
    for l in re.findall(rx("L"), b):
        if limits and l not in limits: err("%s cites %s, not in resource-math" % (u, l))
jids = set()
for r in J:
    j = r["_id"]
    if j in jids: err("duplicate journey %s" % j)
    jids.add(j)
    refs = re.findall(rx("U"), col(r, r"surface|поверхност"))
    if not refs: err("%s uses no surface" % j)
    for u in refs:
        used.add(u)
        if u not in uids: err("%s cites %s, which is not in the surface table" % (j, u))
    for k, pat in (("actor", r"actor|актор"), ("happy path", r"happy|основн|путь"), ("failure and empty cases", r"fail|empty|отказ|пуст")):
        if empty(col(r, pat)): err("%s has no %s" % (j, k))
    sv = col(r, r"serves|обслужив|требован")
    if not re.search(rx("FR", "NFR", "C"), sv): err("%s serves no requirement" % j)
    for s in re.findall(rx("FR", "NFR", "C"), sv):
        served.add(s)
        if reqs and s not in reqs: err("%s serves %s, which is not in requirements" % (j, s))
for u in sorted(uids - used): err("surface %s is in no journey" % u)
# states: every surface has an error row
st_err = {r["_id"] for r in ST if re.search(r"error|ошибк|отказ", col(r, r"state|состояни"), re.I)}
st_all = {r["_id"] for r in ST}
for u in sorted(uids - st_err): err("%s has no error state row" % u)
for u in sorted(st_all - uids): err("state row cites %s, which is not a surface" % u)
for r in ST:
    if empty(col(r, r"sees|what|видит|делать")): err("%s state '%s' says nothing about what the person sees and can do" % (r["_id"], col(r, r"state|состояни")))
# Must requirements that touch people are served
kw = r"(?i)пользоват|владел|оператор|экран|интерфейс|команд|уведомл|кнопк|ручк|user|owner|operator|screen|interface|command|notif|button|knob|display|usab|accessib|доступн|удобств"
miss = [k for k, (p, l) in reqs.items() if p == "Must" and re.search(kw, l) and k not in served and k not in doc]
if miss: warn("Must requirements that touch people but are not served by any surface or journey: " + ", ".join(miss))
# design leaks
if re.search(r"(?i)#[0-9a-f]{6}\b|\brgb\(|\bfont-(?:family|size|weight)|\b" + rx("B") + r"\b|openapi|\bendpoint\b", doc): warn("colours, fonts, endpoints or architecture parts (B-n) found; they belong to visual design, contracts or architecture")
# header, drift, status, clarity
head = doc.split("\n## ")[0]
cm = re.search(r"(\d+)\s*U\b.*?(\d+)\s*J\b", head)
if not cm or int(cm.group(1)) != len(U) or int(cm.group(2)) != len(J): err("header Counts must read '%d U · %d J' to match the tables" % (len(U), len(J)))
for nm, text in (("requirements", req), ("resource-math", rm)):
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the ux document is based on (%s)" % (nm, rdte.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
nobudget = len([r for r in U if re.search(INTERACTIVE, col(r, r"kind|вид|тип"), re.I) and not (re.search(r"\d", col(r, r"budget|бюджет")) or re.search(rx("L"), col(r, r"budget|бюджет")))])
open_forks = len([l for l in doc.splitlines() if l.startswith("|") and re.search(r"(?i)\btbd\b|не решено", l)])
out.append("CLARITY %d interactive surface(s) without a budget; %d open fork(s)" % (nobudget, open_forks))
if agreed and (nobudget or open_forks): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d surfaces, %d journeys" % (len(U), len(J)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
