#!/usr/bin/env python3
"""Mechanics checker for one zkit project: mechanics.md (+ mechanics/model_*.py executable checks) vs architecture, requirements, contracts.
Usage: check_mechanics.py <project-dir>   (exit 1 on ERROR). Stdlib only.
Executable model contract: mechanics/model_<slug>.py defines run(broken=False) -> list of violation strings (empty = invariants hold);
run(broken=True) must return at least one violation (a check that cannot fail proves nothing)."""
import re, sys, os, glob, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flow", "scripts"))
try: from ids import rx
except ImportError: sys.exit("ERROR: zkit id registry flow/scripts/ids.py not found: run this script from the zkit plugin, not from a copied skill")

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, arch, req, rm, ct = rdp("mechanics.md"), rdp("architecture.md"), rdp("requirements.md"), rdp("resource-math.md"), rdp("contracts.md")
if doc is None: sys.exit("ERROR: no mechanics.md in %s (pass the project folder)" % d)
out = []
err = lambda m: out.append("ERROR  " + m)
warn = lambda m: out.append("WARN   " + m)

def sections(t): return {re.sub(r"^\d+\.\s*", "", p.split("\n")[0]).strip().lower(): p for p in re.split(r"(?m)^## ", t)[1:]}
S = sections(doc)
def sec(*names):
    for k, v in S.items():
        if any(re.search(n, k) for n in names): return v
    return ""
def rows_of(t, first):
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and re.match(r"(id|state|состояние)$", c[0].lower()): hdr = [x.lower() for x in c]; continue
        if hdr and not re.match(r"[-: ]+$", c[0]) and re.match(first, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")

reqs = set(re.findall(r"^\|\s*(" + rx("FR", "NFR", "C") + r")\s*\|", req or "", re.M))
parts = set(re.findall(r"^\|\s*(" + rx("B") + r")\s*\|", arch or "", re.M))
ifaces = set(re.findall(r"^\|\s*(" + rx("I") + r")\s*\|", arch or "", re.M))
if arch is None: warn("no architecture.md: parts cannot be checked")
MC = rows_of(sec("механизм", "mechanism"), rx("MC") + r"$")
if not MC: err("no mechanism rows (MC-n)")
seen = set()
for r in MC:
    m = r["_id"]
    if m in seen: err("duplicate mechanism %s" % m)
    seen.add(m)
    for k, pat in (("part", r"part|част"), ("kind", r"kind|вид|тип"), ("verified by", r"verified|провер"), ("risk", r"risk|риск")): 
        if not col(r, pat).strip(" —-"): err("%s has no %s" % (m, k))
    for b in re.findall(rx("B"), col(r, r"part|част")):
        if parts and b not in parts: err("%s names %s, not a part of the architecture" % (m, b))
    sv = re.findall(rx("FR", "NFR", "C"), col(r, r"serves|обслужив|требован"))
    if not sv: err("%s serves no requirement" % m)
    for s in sv:
        if reqs and s not in reqs: err("%s serves %s, which is not in requirements" % (m, s))
    if not re.search(r"^(H|M|L|высок|средн|низк)", col(r, r"risk|риск").strip(), re.I): warn("%s: risk should be H / M / L" % m)

# every part has a mechanism or a stated reason it is trivial
covered = set(b for r in MC for b in re.findall(rx("B"), col(r, r"part|част")))
triv = sec("тривиальн", "trivial")
for b in sorted(parts):
    if b not in covered and not re.search(r"\b%s\b" % b, triv): err("part %s has neither a mechanism nor a line in 'trivial parts' saying why" % b)

# executable models
models = sorted(glob.glob(os.path.join(d, "mechanics", "model_*.py")))
modres = {}
for mp in models:
    nm = os.path.relpath(mp, d).replace(os.sep, "/")
    try:
        sp = importlib.util.spec_from_file_location("mdl_" + os.path.basename(mp)[:-3], mp); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
        good, bad = M.run(), M.run(broken=True)
    except Exception as e: err("%s failed to run: %s" % (nm, str(e).splitlines()[0][:100] if str(e) else type(e).__name__)); continue
    modres[nm] = (good, bad)
    if good: err("%s: invariants VIOLATED: %s" % (nm, "; ".join(good[:3])))
    if not bad: err("%s: run(broken=True) found no violation - the check cannot fail, so it proves nothing" % nm)
for r in MC:
    ver, risk = col(r, r"verified|провер"), col(r, r"risk|риск").strip()
    files = re.findall(r"mechanics/model_[\w.-]+\.py", ver)
    for f in files:
        if f not in modres and not os.path.exists(os.path.join(d, f)): err("%s: verified-by file %s does not exist" % (r["_id"], f))
    if re.match(r"(H|высок)", risk, re.I) and not files: err("%s is high risk and has no executable model (mechanics/model_*.py)" % r["_id"])
for nm in modres:
    if nm not in doc: warn("%s is not referenced in mechanics.md" % nm)

# state machines: tables with State | Event | ... | Next state
nstate = 0
for m in re.finditer(r"(?ms)^#{2,4}[^\n]*?(" + rx("MC") + r")[^\n]*\n(.*?)(?=^#{2,4} |\Z)", doc):
    tid, body = m.group(1), m.group(2)
    trs = rows_of(body, r".+")
    trs = [r for r in trs if any("next" in h or "следующ" in h for h in r)]
    if not trs: continue
    nstate += 1
    states = []
    for r in trs:
        s = r["_id"].replace("(final)", "").replace("(начальное)", "").replace("(initial)", "").strip("* `")
        if s not in states: states.append(s)
    finals = set(r["_id"].replace("(final)", "").strip("* `") for r in trs if "(final)" in r["_id"] or "(конечн" in r["_id"])
    edges = {}
    for r in trs:
        s = r["_id"].replace("(final)", "").replace("(начальное)", "").replace("(initial)", "").strip("* `")
        n = col(r, r"next|следующ").strip("* `")
        if n in ("—", "-", "", "stay", "остаётся"): n = s
        edges.setdefault(s, set()).add(n)
        if n not in states and n not in finals: err("%s: transition goes to '%s', which has no row (declare it, mark (final) if terminal)" % (tid, n))
    reach, todo = {states[0]}, [states[0]]
    while todo:
        for n in edges.get(todo.pop(), ()):
            if n not in reach: reach.add(n); todo.append(n)
    for s in states:
        if s not in reach: err("%s: state '%s' is unreachable from the initial state '%s'" % (tid, s, states[0]))
        if s not in finals and all(n == s for n in edges.get(s, {s})) and not re.search(r"(?i)wait|ожида", " ".join(str(v) for r in trs if r["_id"].startswith(s) for v in r.values())):
            warn("%s: state '%s' has no way out (dead end that is not marked final or waiting)" % (tid, s))
    if not any(re.search(r"(?i)timeout|crash|restart|fail|таймаут|сбой|рестарт|отказ|ошибк", r.get("event", "") + r.get("событие", "")) for r in trs): warn("%s: no timeout / crash / failure event in the state machine" % tid)

# internal contracts specs listed
isec = sec("внутренн", "internal")
for i in sorted(set(re.findall(r"\b" + rx("I") + r"\b", isec))):
    if ifaces and i not in ifaces: err("internal contract list names %s, which is not an interface of the architecture" % i)
for f in re.findall(r"contracts/[\w.-]+\.(?:yaml|yml|md)", isec):
    if not os.path.exists(os.path.join(d, f)): err("internal contract spec %s does not exist" % f)

# counts, drift, status, clarity
head = doc.split("\n## ")[0]
cm = re.search(r"(\d+)\s*MC\b", head)
if not cm or int(cm.group(1)) != len(MC): err("header Counts must read '%d MC' to match the mechanism table" % len(MC))
for nm, text in (("requirements", req), ("resource-math", rm), ("contracts", ct), ("architecture", arch)):
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the mechanics are based on (%s)" % (nm, rdte.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
nomodel = [r["_id"] for r in MC if re.match(r"(H|высок)", col(r, r"risk|риск").strip(), re.I) and not re.findall(r"mechanics/model_", col(r, r"verified|провер"))]
open_forks = len([l for l in doc.splitlines() if l.startswith("|") and re.search(r"(?i)\btbd\b|не решено|open question", l)])
out.append("CLARITY %d high-risk mechanism(s) without an executable model: %s; %d open fork(s)" % (len(nomodel), ", ".join(nomodel) or "-", open_forks))
if agreed and (nomodel or open_forks): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d mechanisms, %d state machines, %d executable models" % (len(MC), nstate, len(modres)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
