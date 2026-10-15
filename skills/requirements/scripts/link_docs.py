#!/usr/bin/env python3
"""Keep zkit documents linked. Idempotent; stdlib only.

Layout (zkit docs folder): folders are named by stage, files are numbered by pass through the chain
(NN is the same in every stage folder for one pass; a new initiative gets the next NN):
  index.md
  concept/NN-<slug>.md
  requirements/NN-<slug>.md          (later stages: high-level-design/NN-<slug>.md, ... add to STAGES)
  decisions/index.md, decisions/D-<n>.md      (one file per decision, numbered across all passes)
  research/R-<n>-<slug>.md

Usage:
  link_docs.py <dir>        make mentions of D-n, [R-n] and 'concept §n' real links in the stage documents;
                            rebuild 'Связи' in decision files, 'Используется в' in research reports and
                            decisions/index.md
  link_docs.py <dir> --migrate [--slug name]
                            first convert an old layout (flat 01-concept.md / 02-requirements.md / decisions.md,
                            or 01-concept/concept.md) into the layout above; --slug names the pass
"""
import os, re, sys, glob

d = sys.argv[1] if len(sys.argv) > 1 else "docs/zkit"
STAGES = ["concept", "requirements"]
P = lambda *a: os.path.join(d, *a)
rd = lambda p: open(p, encoding="utf-8").read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8").write(s)
def rel(frm, to): return os.path.relpath(to, os.path.dirname(frm)).replace(os.sep, "/")

# ---------- migration of old layouts
if "--migrate" in sys.argv:
    slug = sys.argv[sys.argv.index("--slug") + 1] if "--slug" in sys.argv else (os.path.basename(os.path.dirname(os.path.abspath(d))) or "project")
    OLD = {"concept": ("01-concept.md", "01-concept/concept.md"), "requirements": ("02-requirements.md", "02-requirements/requirements.md")}
    for name in STAGES:
        for old in OLD[name]:
            if os.path.exists(P(old)):
                os.makedirs(P(name), exist_ok=True); os.rename(P(old), P(name, "01-%s.md" % slug))
                if "/" in old and not os.listdir(os.path.dirname(P(old))): os.rmdir(os.path.dirname(P(old)))
    if os.path.exists(P("decisions.md")):
        txt = rd(P("decisions.md"))
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
        os.rename(P("decisions.md"), P("decisions.md.migrated"))
    # repair links in every document
    C, R = "concept/01-%s.md" % slug, "requirements/01-%s.md" % slug
    for f in glob.glob(P("**", "*.md"), recursive=True):
        t = rd(f); u = t
        top = os.path.dirname(os.path.abspath(f)) == os.path.abspath(d)
        pre = "" if top else "../"
        if not top:
            u = u.replace("](research/", "](../research/").replace("](decisions.md)", "](../decisions/index.md)")
        else:
            u = u.replace("](decisions.md)", "](decisions/index.md)")
        for old, new in (("01-concept/concept.md", C), ("02-requirements/requirements.md", R), ("01-concept.md", C), ("02-requirements.md", R)):
            u = re.sub(r"\]\((?:\.\./)?%s\)" % re.escape(old), "](" + pre + new + ")", u)
        if os.path.basename(os.path.dirname(f)) == "requirements":
            u = re.sub(r"(?<![\[(/])01-concept\.md", "[01-concept.md](../%s)" % C, u, count=1)
        if u != t: wr(f, u)
    print("migrated")

def stage_files(name): return sorted(glob.glob(P(name, "[0-9][0-9]-*.md")))
def concept_for(path):
    c = glob.glob(P("concept", os.path.basename(path)[:2] + "-*.md"))
    return c[0] if c else None

rfiles = {re.match(r"R-\d+", os.path.basename(f)).group(0): f for f in glob.glob(P("research", "R-*.md"))}
dfiles = {re.match(r"D-(\d+)", os.path.basename(f)).group(0): f for f in glob.glob(P("decisions", "D-*.md"))}
stage_docs = [f for name in STAGES for f in stage_files(name)]

# ---------- 1. linkify mentions in stage documents
def linkify(path):
    out, fence = [], False
    cp = concept_for(path) if os.path.basename(os.path.dirname(path)) != "concept" else None
    for line in rd(path).split("\n"):
        if line.startswith("```"): fence = not fence
        if fence or line.startswith("#") or line.startswith(">"):
            out.append(line); continue
        line = re.sub(r"(?<![\w\[/(-])(D-\d+)(?![\w\]-])(?!\]\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, dfiles[m.group(1)])) if m.group(1) in dfiles else m.group(0), line)
        line = re.sub(r"\[(R-\d+)\](?!\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, rfiles[m.group(1)])) if m.group(1) in rfiles else m.group(0), line)
        if cp:
            line = re.sub(r"(?<![\[\w])((?:concept|концепт)\s*§\s*\d+(?:[,\s]*§\s*\d+)*)(?!\]\()", lambda m: "[%s](%s)" % (m.group(1), rel(path, cp)), line, flags=re.I)
        out.append(line)
    open(path, "w", encoding="utf-8").write("\n".join(out))
for f in stage_docs: linkify(f)

# ---------- 2. collect mentions: key -> {doc path: [labels]}
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
for f in stage_docs:
    for k, labs in labels(f).items():
        mentions.setdefault(k, {}).setdefault(f, []).extend(labs)

def block(key, path, title):
    lines = []
    for f in stage_docs:
        labs = mentions.get(key, {}).get(f)
        if labs:
            lines.append("- [%s/%s](%s): %s" % (os.path.basename(os.path.dirname(f)), os.path.basename(f), rel(path, f), ", ".join(dict.fromkeys(labs))))
    if key.startswith("D-"):
        for k, f in sorted(dfiles.items(), key=lambda x: int(x[0][2:])):
            if f != path and re.search(r"\b%s\b" % re.escape(key), rd(f).split("## Связи")[0]):
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
print("linked: %d decisions, %d reports, %d stage documents" % (len(dfiles), len(rfiles), len(stage_docs)))
