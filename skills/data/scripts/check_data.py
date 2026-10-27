#!/usr/bin/env python3
"""Mechanical check of data.md (logical data model) against requirements, resource-math and contracts of one zkit project.
Usage: check_data.py <project-dir>   (exit 1 on ERROR). Stdlib only (resource-math/model.py is imported when present)."""
import re, sys, os, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flow", "scripts"))
from ids import rx

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, req, rm, ct = rdp("data.md"), rdp("requirements.md"), rdp("resource-math.md"), rdp("contracts.md")
if doc is None: sys.exit("ERROR: no data.md in %s (pass the project folder)" % d)
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
        if c and c[0].lower() in ("id", "entity", "сущность"): hdr = [x.lower() for x in c]; continue
        if hdr and re.match(idpat, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")

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
assum = set(re.findall(r"\b" + rx("A") + r"\b", rm)) if rm else set()
rmp = next((q for q in (os.path.join(d, "resource-math/model.py"), os.path.join(d, "resource_model.py")) if os.path.exists(q)), None)   # second: legacy layout
if rmp:
    try:
        sp = importlib.util.spec_from_file_location("resource_model", rmp); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M); assum |= set(M.ASSUMPTIONS)
    except Exception as e: warn("resource-math/model.py could not be loaded: %s" % str(e)[:60])
limits = set(re.findall(r"\b" + rx("L") + r"\b", rm)) if rm else set()

E = tables(sec("сущност", "entit", "catalog"), rx("E") + r"$")
M_ = tables(sec("память", "memory"), rx("M") + r"$")
LC = tables(sec("жизненн", "lifecycle"), rx("E") + r"$")
if not E: err("no entity rows (E-n) in the entity catalog")
seen = set()
for r in E:
    if r["_id"] in seen: err("duplicate entity %s" % r["_id"])
    seen.add(r["_id"])
STORE = r"relational|document|file|blob|object|log|append|queue|cache|memory|ram|flash|nvm|register|static|stack|heap|реляц|документ|файл|журнал|очеред|кэш|памят|флеш|статич"
SENS = r"public|internal|personal|secret|публич|внутрен|персональн|секрет"
served = set()
for r in E:
    e = r["_id"]
    for k, pat in (("meaning", r"meaning|смысл|описан"), ("writers", r"writer|owner|актор|владел|кто пишет"), ("volume", r"volume|объ[её]м"), ("retention", r"retention|срок|жизн"), ("storage class", r"storage|класс|хранил"), ("sensitivity", r"sensitiv|чувств")):
        if not col(r, pat).strip(" —-"): err("%s has no %s" % (e, k))
    if not re.search(STORE, col(r, r"storage|класс|хранил"), re.I): warn("%s: storage class not from the usual set (relational, document, file/blob, log, queue, cache, memory, flash, register)" % e)
    if not re.search(SENS, col(r, r"sensitiv|чувств"), re.I): warn("%s: sensitivity should be public / internal / personal / secret" % e)
    vol = col(r, r"volume|объ[её]м") + " " + col(r, r"growth|рост")
    refs = re.findall(rx("A"), vol)
    for a in refs:
        if assum and a not in assum: err("%s cites %s, not in resource-math" % (e, a))
    if not refs and not re.search(r"\d", vol): warn("%s: volume has neither a number nor an assumption A-n from resource-math" % e)
    for s in re.findall(rx("FR", "NFR", "C"), col(r, r"serves|обслужив|требован")):
        served.add(s)
        if reqs and s not in reqs: err("%s serves %s, which is not in requirements" % (e, s))
    if not re.search(rx("FR", "NFR", "C"), col(r, r"serves|обслужив|требован")): err("%s serves no requirement" % e)
lc = {r["_id"]: r for r in LC}
for r in E:
    e = r["_id"]; sens = col(r, r"sensitiv|чувств").lower()
    if e not in lc: err("%s has no lifecycle row" % e); continue
    for k, pat in (("created by", r"created|создан"), ("deleted", r"delet|удал")):
        if not col(lc[e], pat).strip(" —-"): err("%s lifecycle has no '%s'" % (e, k))
    if re.search(r"personal|secret|персональн|секрет", sens) and not col(lc[e], r"cop|копи").strip(" —-"): err("%s is %s but its lifecycle lists no copies (backups, caches, derived data) and their lifetime" % (e, sens.strip()))
for e in lc:
    if e not in seen: err("lifecycle row %s has no entity" % e)
# ER diagram
er = re.search(r"```mermaid\s*\n\s*erDiagram(.*?)```", doc, re.S)
if not er: err("no Mermaid erDiagram")
else:
    names = set(re.findall(r"\b(E\d+)\b", er.group(1))) | set(re.findall(r"\bE-(\d+)\b", er.group(1)))
    nodes = set("E-" + re.sub(r"\D", "", n) for n in names)
    for n in sorted(nodes - seen): err("diagram entity %s is not in the catalog" % n)
    for n in sorted(seen - nodes): err("entity %s is not in the diagram" % n)
# memory regions
for r in M_:
    m = r["_id"]
    for k, pat in (("contents", r"content|содерж"), ("lifetime", r"lifetime|жизн"), ("size", r"size|размер"), ("allocation", r"alloc|размещ|выделен")):
        if not col(r, pat).strip(" —-"): err("%s has no %s" % (m, k))
    for l in re.findall(rx("L"), col(r, r"serves|обслужив|limit|лимит|предел")):
        if limits and l not in limits: err("%s cites %s, not in resource-math" % (m, l))
if not M_ and not re.search(r"(?i)not applicable|не применим|нет внутрипроцесс", sec("память", "memory")): warn("no memory regions (M-n) and no 'not applicable' line in the memory section")
# requirements about data covered
kw = r"(?i)хран|удал|экспорт|журнал|истори|аудит|резервн|копи|persist|stor|delet|retention|export|\blog|audit|backup|history|preset|пресет"
miss = [k for k, (p, l) in reqs.items() if p == "Must" and re.search(kw, l) and k not in served and k not in doc]
if miss: warn("Must requirements that mention data but are not served by any entity or mentioned: " + ", ".join(miss))
if re.search(r"(?i)create table|primary key|varchar|\bindex on\b|\b" + rx("B") + r"\b", doc): warn("table-level detail or architecture parts (B-n) found; they belong to later steps")
# header, drift, status, clarity
head = doc.split("\n## ")[0]
cm = re.search(r"(\d+)\s*E\b", head)
if not cm or int(cm.group(1)) != len(E): err("header Counts must read '%d E' to match the catalog" % len(E))
for nm, text in (("requirements", req), ("resource-math", rm), ("contracts", ct)):
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the data model is based on (%s)" % (nm, rdte.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
noamount = len([r for r in E if not re.findall(rx("A"), col(r, r"volume|объ[её]м") + col(r, r"growth|рост")) and not re.search(r"\d", col(r, r"volume|объ[её]м"))])
open_forks = len([l for l in doc.splitlines() if l.startswith("|") and re.search(r"(?i)\btbd\b|не решено", l)])
out.append("CLARITY %d entity(ies) without a volume figure or assumption; %d open fork(s)" % (noamount, open_forks))
if agreed and (noamount or open_forks): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d entities, %d memory regions" % (len(E), len(M_)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
