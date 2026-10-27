#!/usr/bin/env python3
"""Contracts checker for one zkit project: contracts.md (index) + contracts/*.yaml (OpenAPI / AsyncAPI / JSON Schema) or
contracts/*.md (cards for other paradigms: registers, frames, files). Usage: check_contracts.py <project-dir> (exit 1 on ERROR).
Needs PyYAML to read the specs and jsonschema to validate examples; without them it says so (WARN) and checks the index only.
Spec extensions: x-boundary (X-n), x-direction (consumed|published), x-verified {status: verified|unverified, source},
x-limits [L-n of resource-math], x-serves [FR/NFR/C ids]; non-GET operations carry x-idempotency."""
import re, sys, os, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flow", "scripts"))
try: from ids import rx
except ImportError: sys.exit("ERROR: zkit id registry flow/scripts/ids.py not found: run this script from the zkit plugin, not from a copied skill")

d = next((a for a in sys.argv[1:] if not a.startswith("--")), "docs/zkit")
rdp = lambda n: open(os.path.join(d, n), encoding="utf-8").read() if os.path.exists(os.path.join(d, n)) else None
doc, req, rm, ifc = rdp("contracts.md"), rdp("requirements.md"), rdp("resource-math.md"), rdp("ux.md")   # ux.md: optional step
if doc is None: sys.exit("ERROR: no contracts.md in %s (pass the project folder)" % d)
out = []
err = lambda m: out.append("ERROR  " + m)
warn = lambda m: out.append("WARN   " + m)
try: import yaml
except ImportError: yaml = None; warn("PyYAML is not installed: spec files are NOT checked (pip install pyyaml)")
try: import jsonschema
except ImportError: jsonschema = None; warn("jsonschema is not installed: examples are NOT validated against their schemas (pip install jsonschema)")

def tables(t, idpat):
    rows, hdr = [], None
    for l in t.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(idpat, c[0]): rows.append(dict({h: (c[i] if i < len(c) else "") for i, h in enumerate(hdr)}, _id=c[0]))
    return rows
col = lambda r, pat: next((v for h, v in r.items() if re.search(pat, h)), "")
ids_of = lambda s: set(re.findall(rx("FR", "NFR", "C"), s))

reqs = {}
if req is not None:
    hdr = None
    for l in req.splitlines():
        if not l.startswith("|"): hdr = None; continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c and c[0].lower() == "id": hdr = [x.lower() for x in c]; continue
        if hdr and re.match(r"(FR|NFR|C)-\d+$", c[0]):
            i = next((n for n, h in enumerate(hdr) if re.search(r"приоритет|priority", h)), None)
            reqs[c[0]] = c[i] if i is not None and i < len(c) else ""
else: warn("no requirements.md: serving requirements cannot be checked")
limits = set(re.findall(r"\b" + rx("L") + r"\b", rm)) if rm else set()

rows = tables(doc, r"[XI]-\d+$")
if not rows: err("no boundary rows (X-n) in contracts.md")
seen = set()
for r in rows:
    if r["_id"] in seen: err("duplicate boundary %s" % r["_id"])
    seen.add(r["_id"])
unver_must = []
for r in rows:
    x = r["_id"]; direction = col(r, r"direction|направл").lower(); spec = re.sub(r"[\[\]`]|\(.*?\)", "", col(r, r"spec|файл|спецификац")).strip()
    serves = ids_of(col(r, r"serves|обслужив|требован"))
    if not re.search(r"consumed|published|internal|потребл|публик|внутренн", direction): err("%s: direction must be consumed, published or internal (I-n, written by mechanics)" % x)
    if not serves: err("%s serves no requirement" % x)
    for s in serves:
        if reqs and s not in reqs: err("%s serves %s, which is not in requirements" % (x, s))
    path = os.path.join(d, spec) if spec else None
    if not spec or not os.path.exists(path): err("%s: spec file '%s' does not exist" % (x, spec)); continue
    consumed = bool(re.search(r"consumed|потребл", direction)); internal = bool(re.search(r"internal|внутренн", direction))
    ver = col(r, r"verif|провер")
    if consumed and (not re.search(r"verified|проверен|" + rx("R"), ver, re.I) or re.search(r"unverified|не провер", ver, re.I)):
        warn("%s is consumed and not verified against the counterparty's documentation" % x)
        if any(reqs.get(s) == "Must" for s in serves): unver_must.append(x)
    if path.endswith(".md"):
        t = open(path, encoding="utf-8").read()
        for need in (r"layout|формат|структур", r"timing|limit|предел|лимит", r"error|ошиб"):
            if not re.search(need, t, re.I): err("%s: card %s lacks a section matching /%s/" % (x, spec, need))
        continue
    if yaml is None: continue
    try: S = yaml.safe_load(open(path, encoding="utf-8"))
    except Exception as e: err("%s: %s does not parse: %s" % (x, spec, str(e).splitlines()[0])); continue
    if not isinstance(S, dict): err("%s: %s is not a mapping" % (x, spec)); continue
    if S.get("x-boundary") != x: err("%s: %s has x-boundary '%s'" % (x, spec, S.get("x-boundary")))
    dd = str(S.get("x-direction", "")).lower()
    if dd and dd.startswith("cons") != consumed and not (internal and dd.startswith("int")): err("%s: x-direction in %s disagrees with the index" % (x, spec))
    for l in S.get("x-limits") or []:
        if rm is not None and l not in limits: err("%s: x-limits cites %s, not in resource-math" % (x, l))
    if consumed and not S.get("x-limits") and rm is not None: warn("%s: consumed boundary with no x-limits (quota, rate, price, latency of the counterparty)" % x)
    for s in S.get("x-serves") or []:
        if reqs and s not in reqs: err("%s: x-serves cites %s, not in requirements" % (x, s))
    if re.search(r"\b" + rx("B") + r"\b", json.dumps(S, default=str)): warn("%s: %s mentions architecture parts (B-n); contracts are written before them" % (x, spec))
    # structure per standard
    if "openapi" in S:
        if not (S.get("info") or {}).get("version"): err("%s: info.version missing" % x)
        if not S.get("paths"): err("%s: no paths" % x)
        sec = bool(S.get("security") or (S.get("components") or {}).get("securitySchemes"))
        for p, ops in (S.get("paths") or {}).items():
            for m, op in (ops or {}).items():
                if m not in ("get", "post", "put", "patch", "delete") or not isinstance(op, dict): continue
                w = "%s %s %s" % (x, m.upper(), p)
                if not op.get("operationId"): err("%s: no operationId" % w)
                if not any(re.match(r"[45]\d\d|default", str(k)) for k in (op.get("responses") or {})): err("%s: no error response (4xx/5xx/default)" % w)
                if not (sec or op.get("security") is not None) and not consumed: warn("%s: no security defined" % w)
                if m != "get" and "x-idempotency" not in op: warn("%s: mutating operation without x-idempotency" % w)
    elif "asyncapi" in S:
        if not S.get("channels"): err("%s: no channels" % x)
        def msgs(o):
            if isinstance(o, dict):
                if "payload" in o or "messageId" in o: yield o
                for v in o.values(): yield from msgs(v)
            elif isinstance(o, list):
                for v in o: yield from msgs(v)
        ms = list(msgs(S.get("channels")) ) + list(msgs((S.get("components") or {}).get("messages")))
        if not ms: err("%s: no messages with payload" % x)
    elif not ("$schema" in S or "type" in S or "properties" in S): err("%s: %s is not OpenAPI, AsyncAPI or JSON Schema" % (x, spec))
    # examples against schemas
    if jsonschema:
        def check(schema, inst, where):
            try: jsonschema.validate(inst, dict(schema, components=S.get("components", {})))
            except jsonschema.ValidationError as e: err("%s: example at %s violates its schema: %s" % (x, where, e.message[:100]))
            except Exception as e: warn("%s: cannot validate example at %s (%s)" % (x, where, str(e)[:80]))
        def walk(o, path):
            if isinstance(o, dict):
                if isinstance(o.get("schema"), dict):
                    exs = [o["example"]] if "example" in o else []
                    if isinstance(o.get("examples"), dict): exs += [v.get("value") for v in o["examples"].values() if isinstance(v, dict)]
                    for e in exs: check(o["schema"], e, path)
                if isinstance(o.get("payload"), dict) and isinstance(o.get("examples"), list):
                    for e in o["examples"]:
                        if isinstance(e, dict) and "payload" in e: check(o["payload"], e["payload"], path)
                for k, v in o.items(): walk(v, path + "/" + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o): walk(v, path + "/%d" % i)
        walk(S, spec)
files = {os.path.relpath(f, d).replace(os.sep, "/") for f in glob.glob(os.path.join(d, "contracts", "*")) if os.path.isfile(f)}
listed = {re.sub(r"[\[\]`]|\(.*?\)", "", col(r, r"spec|файл|спецификац")).strip() for r in rows}
for f in sorted(files - listed): warn("%s is not listed in the index" % f)

# ---------- requirements coverage, counts, drift, status, clarity
head = doc.split("\n## ")[0]
cm = re.search(r"(\d+)\s*X\b", head)
nx = len([r for r in rows if r["_id"].startswith("X")])
if not cm or int(cm.group(1)) != nx: err("header Counts must read '%d X' to match the index (I-n rows are not counted)" % nx)
for nm, text in (("requirements", req), ("resource-math", rm), ("ux", ifc)):
    if text is None: continue
    rdte = re.search(r"(?:Дата|Date):\*\*\s*([\d-]+)", text); bd = re.search(nm + r"[^\n]*?(\d{4}-\d{2}-\d{2})", head)
    if not bd: warn("header has no 'Based on' date for %s" % nm)
    elif rdte and rdte.group(1) > bd.group(1): err("%s (%s) is newer than the date the contracts are based on (%s)" % (nm, rdte.group(1), bd.group(1)))
agreed = bool(re.search(r"(?:Status|Статус):\*\*\s*(agreed|согласовано)", head, re.I))
open_forks = len([l for l in doc.splitlines() if l.startswith("|") and re.search(r"(?i)\btbd\b|не решено", l)])
out.append("CLARITY %d consumed contract(s) serving a Must requirement and not verified: %s; %d open fork(s)" % (len(unver_must), ", ".join(unver_must) or "-", open_forks))
if agreed and (unver_must or open_forks): err("status is 'agreed' but the clarity gate is not passed (see CLARITY line)")
print("\n".join(out) if out else "OK: no findings")
print("%d boundaries, %d spec files" % (len(rows), len(files)))
sys.exit(1 if any(o.startswith("ERROR") for o in out) else 0)
