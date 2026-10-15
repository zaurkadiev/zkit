#!/usr/bin/env python3
"""Keep zkit documents linked. Idempotent; stdlib only.

Layout (zkit docs folder):
  index.md
  01-concept/concept.md
  02-requirements/requirements.md
  decisions/index.md, decisions/D-<n>.md      (one file per decision)
  research/R-<n>-<slug>.md

Usage:
  link_docs.py <dir>             make mentions of D-n, [R-n] and 'concept §n' real links in the stage
                                 documents; rebuild 'Связи' in decision files, 'Используется в' in research
                                 reports and decisions/index.md
  link_docs.py <dir> --migrate   first convert the old flat layout (01-concept.md, 02-requirements.md,
                                 decisions.md) into the layout above
"""
import os, re, sys, glob

d = sys.argv[1] if len(sys.argv) > 1 else "docs/zkit"
STAGES = [("concept", "01-concept"), ("requirements", "02-requirements")]  # later stages: add here
P = lambda *a: os.path.join(d, *a)
rd = lambda p: open(p, encoding="utf-8").read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8").write(s)

# ---------- migration of the flat layout
if "--migrate" in sys.argv:
    for name, folder in STAGES:
        old = P(folder + ".md")
        if os.path.exists(old):
            os.makedirs(P(folder), exist_ok=True); os.rename(old, P(folder, name + ".md"))
    old = P("decisions.md")
    if os.path.exists(old):
        txt = rd(old)
        for m in re.finditer(r"^###\s*D-(\d+)\s*(?:\(([^)]*)\))?\s*:\s*(.+?)\n(.*?)(?=^###\s*D-|\Z)", txt, re.M | re.S):
            n, note, title, body = m.groups()
            body = body.strip()
            date = re.search(r"Дата:\s*([\d-]+)", body)
            status = "принято"
            if note:
                nm = re.search(r"D-(\d+)", note)
                verb = "заменено" if re.search(r"заменено|superseded", note, re.I) else "уточнено"
                status = "%s [D-%s](D-%s.md)" % (verb, nm.group(1), nm.group(1)) if nm else note
            wr(P("decisions", "D-%s.md" % n), "# D-%s: %s\n\n> **Статус:** %s · **Дата:** %s\n\n%s\n" % (n, title.strip(), status, date.group(1) if date else "—", body))
        os.rename(old, old + ".migrated")
    # repair relative links of the moved documents and of research reports
    fix = [("](research/", "](../research/"), ("](../02-requirements.md)", "](../02-requirements/requirements.md)"),
           ("](../01-concept.md)", "](../01-concept/concept.md)"), ("](decisions.md)", "](../decisions/index.md)")]
    for f in glob.glob(P("0*", "*.md")) + glob.glob(P("research", "R-*.md")) + glob.glob(P("decisions", "*.md")):
        t = rd(f); u = t
        if os.sep + "research" + os.sep not in f:
            for x, y in fix[:1] + fix[3:]: u = u.replace(x, y)
        for x, y in fix[1:3]: u = u.replace(x, y)
        if f.endswith(os.path.join("02-requirements", "requirements.md")):
            u = re.sub(r"(?<![\[(])01-concept\.md", "[01-concept.md](../01-concept/concept.md)", u, count=1)
        if u != t: wr(f, u)
    ix = P("index.md")
    if os.path.exists(ix):
        t = rd(ix)
        for x, y in (("](01-concept.md)", "](01-concept/concept.md)"), ("](02-requirements.md)", "](02-requirements/requirements.md)"), ("](decisions.md)", "](decisions/index.md)")):
            t = t.replace(x, y)
        wr(ix, t)
    print("migrated")

def stage_path(name):
    folder = dict(STAGES)[name]
    p = P(folder, name + ".md")
    return p if os.path.exists(p) else None

def rel(frm, to): return os.path.relpath(to, os.path.dirname(frm)).replace(os.sep, "/")
rfiles = {re.match(r"R-\d+", os.path.basename(f)).group(0): f for f in glob.glob(P("research", "R-*.md"))}
dfiles = {re.match(r"D-(\d+)", os.path.basename(f)).group(0): f for f in glob.glob(P("decisions", "D-*.md"))}

# ---------- 1. linkify mentions in stage documents
def linkify(path):
    out, fence = [], False
    for line in rd(path).split("\n"):
        if line.startswith("```"): fence = not fence
        if fence or line.startswith("#") or line.startswith(">"):
            out.append(line); continue
        line = re.sub(r"(?<![\w\[/(-])(D-\d+)(?![\w\]-])(?!\]\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, dfiles[m.group(1)])) if m.group(1) in dfiles else m.group(0), line)
        line = re.sub(r"\[(R-\d+)\](?!\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, rfiles[m.group(1)])) if m.group(1) in rfiles else m.group(0), line)
        cp = stage_path("concept")
        if cp and path != cp:
            line = re.sub(r"(?<![\[\w])((?:concept|концепт)\s*§\s*\d+(?:[,\s]*§\s*\d+)*)(?!\]\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, cp)), line, flags=re.I)
        out.append(line)
    open(path, "w", encoding="utf-8").write("\n".join(out))
for name, _ in STAGES:
    p = stage_path(name)
    if p: linkify(p)

# ---------- 2. collect mentions: key -> {stage: set(labels)}
def labels(path):
    res, head = {}, ""
    for line in rd(path).split("\n"):
        h = re.match(r"#+\s*(.*)", line)
        if h: head = h.group(1).strip(); continue
        idm = re.match(r"\|\s*((?:FR|NFR|C)-\d+)\s*\|", line) or re.match(r"\s*(?:[-*]|\d+\.)\s*\*\*([PWК]-\d+)\.", line)
        label = idm.group(1) if idm else re.sub(r"\s+", " ", head)[:60] or "—"
        for k in set(re.findall(r"\b(D-\d+)\b", line)) | set("R-" + x for x in re.findall(r"\bR-(\d+)\b", line)):
            res.setdefault(k, []).append(label)
    return res
mentions = {}
for name, _ in STAGES:
    p = stage_path(name)
    if p:
        for k, labs in labels(p).items():
            mentions.setdefault(k, {}).setdefault(name, []).extend(labs)

def block(key, path, title):
    lines = []
    for name, _ in STAGES:
        labs = mentions.get(key, {}).get(name)
        if labs:
            seen = list(dict.fromkeys(labs))
            lines.append("- [%s](%s): %s" % (name, rel(path, stage_path(name)), ", ".join(seen)))
    for k, f in sorted(dfiles.items(), key=lambda x: int(x[0][2:])):
        if f != path and re.search(r"\b%s\b" % re.escape(key), rd(f).split("## Связи")[0]) and key.startswith("D-"):
            lines.append("- [%s](%s): упоминает" % (k, rel(path, f)))
    return "## %s\n<!-- собирается link_docs.py, не править вручную -->\n%s\n" % (title, "\n".join(lines) or "- пока нигде не используется")

for key, f in dfiles.items():
    body = rd(f).split("\n## Связи")[0].rstrip("\n")
    wr(f, body + "\n\n" + block(key, f, "Связи"))
for key, f in rfiles.items():
    body = re.split(r"\n## (?:Используется в|Used in)", rd(f))[0].rstrip("\n")
    wr(f, body + "\n\n" + block(key, f, "Используется в"))

# ---------- 3. decisions/index.md
rows = []
for k, f in sorted(dfiles.items(), key=lambda x: int(x[0][2:])):
    t = rd(f)
    title = re.match(r"#\s*D-\d+:\s*(.*)", t).group(1) if re.match(r"#\s*D-\d+:", t) else k
    st = re.search(r"Статус:\*\*\s*(.*?)\s*·", t)
    dt = re.search(r"Дата:\*\*\s*([\d-]+)", t)
    rows.append("| [%s](%s) | %s | %s | %s |" % (k, os.path.basename(f), title, st.group(1) if st else "—", dt.group(1) if dt else "—"))
if rows:
    wr(P("decisions", "index.md"), "# Решения\n\n| # | Решение | Статус | Дата |\n|---|---|---|---|\n" + "\n".join(rows) + "\n")
print("linked: %d decisions, %d reports" % (len(dfiles), len(rfiles)))
