#!/usr/bin/env python3
"""Keep the documents of one zkit project linked. Idempotent; stdlib only.

Layout:
  docs/zkit/<project>/               a project: 'mvp', a big feature, ... (kebab-case name)
      concept.md
      requirements.md                (later stages: high-level-design.md, design-details.md, ...: add to STAGES)
      decisions.md                   ONE file: entries '### D-<n>: title', each with an <a id="D-<n>"> anchor
      research/R-<n>-<slug>.md       one file per research question; ids unique inside the project

Usage:
  link_docs.py <project-dir>          turn mentions of D-n, [R-n] and 'concept §n' into links; rebuild the
                                      back-links under each decision, 'Используется в' in research reports and
                                      the summary table at the top of decisions.md
  link_docs.py <zkit-root> --migrate --project <name>
                                      move an older layout (flat files, numbered files or folders, one file per
                                      decision) into <zkit-root>/<name>/ and repair the links
"""
import os, re, sys, glob, shutil

STAGES = ["concept", "requirements", "high-level-design"]   # later stages: add here and to stage_docs below
rd = lambda p: open(p, encoding="utf-8").read()
def wr(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True); open(p, "w", encoding="utf-8").write(s)
def rel(frm, to): return os.path.relpath(to, os.path.dirname(frm)).replace(os.sep, "/")
ENTRY = re.compile(r'(?:<a id="D-\d+"></a>\n)?^###\s*D-(\d+)\s*(?:\(([^)]*)\))?\s*:\s*(.+?)\n(.*?)(?=^(?:<a id="D-\d+"></a>\n)?###\s*D-|\Z)', re.M | re.S)
def entry_text(n, title, status, date, body):
    return '<a id="D-%s"></a>\n### D-%s: %s\n> **Статус:** %s · **Дата:** %s\n\n%s\n' % (n, n, title.strip(), status, date, body.strip())

arg = sys.argv[1] if len(sys.argv) > 1 else "docs/zkit"

# ---------- migration of older layouts into <root>/<project>/
if "--migrate" in sys.argv:
    root = arg
    name = sys.argv[sys.argv.index("--project") + 1] if "--project" in sys.argv else "mvp"
    d = os.path.join(root, name); os.makedirs(d, exist_ok=True)
    def grab(dest, *patterns):
        for pat in patterns:
            hit = sorted(glob.glob(os.path.join(root, pat)))
            if hit:
                shutil.move(hit[0], os.path.join(d, dest)); return True
    grab("concept.md", "concept/[0-9][0-9]-*.md", "01-concept/concept.md", "01-concept.md")
    grab("requirements.md", "requirements/[0-9][0-9]-*.md", "02-requirements/requirements.md", "02-requirements.md")
    if os.path.isdir(os.path.join(root, "research")): shutil.move(os.path.join(root, "research"), os.path.join(d, "research"))
    entries = {}
    srcs = sorted(glob.glob(os.path.join(root, "decisions", "[0-9][0-9]-*.md")))
    if srcs:
        for m in ENTRY.finditer(rd(srcs[0])): entries[int(m.group(1))] = m.group(0).strip() + "\n"
        shutil.rmtree(os.path.join(root, "decisions"))
    elif os.path.exists(os.path.join(root, "decisions.md")):       # flat journal
        for m in ENTRY.finditer(rd(os.path.join(root, "decisions.md"))):
            n, note, title, body = m.groups(); body = body.strip()
            date = (re.search(r"Дата:\s*([\d-]+)", body) or [None, "—"])[1]
            status = "принято"
            if note:
                nm = re.search(r"D-(\d+)", note)
                verb = "заменено" if re.search(r"заменено|superseded", note, re.I) else "уточнено"
                status = "%s [D-%s](#D-%s)" % (verb, nm.group(1), nm.group(1)) if nm else note
            entries[int(n)] = entry_text(n, title, status, date, body)
        os.rename(os.path.join(root, "decisions.md"), os.path.join(root, "decisions.md.migrated"))
    elif glob.glob(os.path.join(root, "decisions", "D-*.md")):     # one file per decision
        for f in glob.glob(os.path.join(root, "decisions", "D-*.md")):
            t = rd(f).split("\n## Связи")[0]
            m = re.match(r"#\s*D-(\d+):\s*(.*?)\n+> \*\*Статус:\*\*\s*(.*?)\s*·\s*\*\*Дата:\*\*\s*([\d—-]+)\n+(.*)", t, re.S)
            if m:
                n, title, status, date, body = m.groups()
                entries[int(n)] = entry_text(n, title, re.sub(r"\[(D-\d+)\]\(D-(\d+)\.md\)", r"[\1](#D-\2)", status), date, body)
        shutil.rmtree(os.path.join(root, "decisions"))
    if entries:
        wr(os.path.join(d, "decisions.md"), "# Решения: %s\n\n" % name + "\n".join(entries[k] for k in sorted(entries)))
    for ix in (os.path.join(root, "index.md"), os.path.join(root, "decisions", "index.md")):   # indexes are gone
        if os.path.exists(ix): os.remove(ix)
    arg = d
    print("migrated into", d)

d = arg
P = lambda *a: os.path.join(d, *a)
concept_p, req_p, dec_p = P("concept.md"), P("requirements.md"), P("decisions.md")
hld_p = P("high-level-design.md")
rfiles = {re.match(r"R-\d+", os.path.basename(f)).group(0): f for f in glob.glob(P("research", "R-*.md"))}
stage_docs = [p for p in (concept_p, req_p, hld_p) if os.path.exists(p)]

# ---------- repair links that no longer resolve (after a migration or a rename)
def repair(f):
    t = rd(f)
    def fix(m):
        tgt, frag = m.group(2), m.group(3) or ""
        if tgt.startswith("http") or os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), tgt))): return m.group(0)
        b = os.path.basename(tgt)
        dm = re.match(r"D-(\d+)\.md$", b)
        new = (dec_p, "#D-" + dm.group(1)) if dm else None
        for key, path in (("decisions", dec_p), ("concept", concept_p), ("requirements", req_p)):
            if new is None and key in tgt: new = (path, frag)
        rm = re.search(r"R-\d+", b)
        if new is None and rm and rm.group(0) in rfiles: new = (rfiles[rm.group(0)], frag)
        if new is None or not os.path.exists(new[0]): return m.group(0)
        return "%s(%s%s)" % (m.group(1), rel(f, new[0]), new[1])
    u = re.sub(r"(\[[^\]]*\])\(([^)#\s]+\.md)(#[^)\s]*)?\)", fix, t)
    if u != t: wr(f, u)
for f in glob.glob(P("**", "*.md"), recursive=True):
    repair(f)
    t = rd(f)                                                   # drop leftovers of the retired index.md files
    u = re.sub(r"[ \t]*·[ \t]*\[[^\]]*\]\([^)]*index\.md\)|\[[^\]]*\]\([^)]*index\.md\)[ \t]*·[ \t]*|\[[^\]]*\]\([^)]*index\.md\)", "", t)
    if u != t: wr(f, u)

def d_ids(): return set("D-" + x for x in re.findall(r"^###\s*D-(\d+)", rd(dec_p), re.M)) if os.path.exists(dec_p) else set()

# ---------- 1. linkify mentions in concept and requirements
def linkify(path):
    out, fence, ids = [], False, d_ids()
    for line in rd(path).split("\n"):
        if line.startswith("```"): fence = not fence
        if fence or line.startswith("#") or line.startswith(">") or line.startswith("<a id"):
            out.append(line); continue
        line = re.sub(r"(?<![\w\[/(#-])(D-\d+)(?![\w\]-])(?!\]\()", lambda m: "[%s](%s#%s)" % (m.group(1), rel(path, dec_p), m.group(1)) if m.group(1) in ids else m.group(0), line)
        line = re.sub(r"\[(R-\d+)\](?!\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, rfiles[m.group(1)])) if m.group(1) in rfiles else m.group(0), line)
        if path != concept_p and os.path.exists(concept_p):
            line = re.sub(r"(?<![\[\w])((?:concept|концепт)\s*§\s*\d+(?:[,\s]*§\s*\d+)*)(?!\]\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, concept_p)), line, flags=re.I)
        out.append(line)
    open(path, "w", encoding="utf-8").write("\n".join(out))
for f in stage_docs: linkify(f)

# ---------- 2. mentions: key -> {doc: [labels]}
def labels(path):
    res, head = {}, ""
    for line in rd(path).split("\n"):
        h = re.match(r"#+\s*(.*)", line)
        if h: head = h.group(1).strip(); continue
        idm = re.match(r"\|\s*((?:FR|NFR|C|B|I|S)-\d+)\s*\|", line) or re.match(r"\s*(?:[-*]|\d+\.)\s*\*\*([PWК]-\d+)\.", line)
        label = idm.group(1) if idm else re.sub(r"\s+", " ", head)[:60] or "—"
        for k in set(re.findall(r"\b(D-\d+)\b", line)) | set("R-" + x for x in re.findall(r"\bR-(\d+)\b", line)):
            res.setdefault(k, []).append(label)
    return res
mentions = {}
for f in stage_docs:
    for k, labs in labels(f).items(): mentions.setdefault(k, {}).setdefault(f, []).extend(labs)
def links_for(key, own):
    return ["[%s](%s): %s" % (os.path.basename(f), rel(own, f), ", ".join(dict.fromkeys(mentions[key][f]))) for f in stage_docs if f in mentions.get(key, {})]

# ---------- 3. decisions.md: back-links per entry and a summary table
if os.path.exists(dec_p):
    t = rd(dec_p); ents = list(ENTRY.finditer(t))
    head = re.split(r"\n## Сводка", t[:ents[0].start()] if ents else t)[0].rstrip("\n") + "\n"
    rows, body = [], []
    for m in ents:
        n, note, title, b = m.groups(); key = "D-" + n
        b = re.sub(r"\n?<!-- links -->.*?<!-- /links -->\n?", "\n", b, flags=re.S).rstrip("\n")
        st = (re.search(r"Статус:\*\*\s*(.*?)\s*·", b) or [None, note or "принято"])[1]
        rows.append("| [%s](#%s) | %s | %s |" % (key, key, title.strip(), st))
        refs = links_for(key, dec_p)
        for o in ents:
            ob = re.sub(r"<!-- links -->.*?<!-- /links -->", "", o.group(4), flags=re.S)
            if o is not m and re.search(r"\b%s\b" % key, ob): refs.append("[D-%s](#D-%s): упоминает" % (o.group(1), o.group(1)))
        body.append(('<a id="D-%s"></a>\n### D-%s: %s\n' % (n, n, title.strip())) + b + "\n\n<!-- links -->\n**Связи:** " + ("; ".join(refs) if refs else "пока нигде не используется") + "\n<!-- /links -->\n")
    wr(dec_p, head + "\n## Сводка\n\n| # | Решение | Статус |\n|---|---|---|\n" + "\n".join(rows) + "\n\n## Решения\n\n" + "\n".join(body))

# ---------- 4. research reports: used in
for key, f in rfiles.items():
    body = re.split(r"\n## (?:Используется в|Used in)", rd(f))[0].rstrip("\n")
    refs = links_for(key, f)
    wr(f, body + "\n\n## Используется в\n<!-- собирается link_docs.py, не править вручную -->\n" + ("\n".join("- " + r for r in refs) or "- пока нигде не используется") + "\n")
print("linked: %s — %d stage documents, %d decisions, %d reports" % (os.path.basename(os.path.abspath(d)), len(stage_docs), len(d_ids()), len(rfiles)))
