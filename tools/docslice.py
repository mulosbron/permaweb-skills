"""Print documents from the bundled permaweb llms.txt snapshot.

Usage:
  python tools/docslice.py 27            # print document 27
  python tools/docslice.py 27 95 103     # print several documents
  python tools/docslice.py --find spawn  # list documents whose title or body mentions "spawn"
  python tools/docslice.py --list        # list every document number, title and source URL

Long single-line HTML extracts are wrapped at sentence-ish boundaries so they stay readable.
"""
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "_source" / "permaweb-docs-2026-10-13.llms.txt"
HEADER = re.compile(r"^# (\d+)\. (.*)$")


def load():
    lines = SRC.read_text(encoding="utf-8").split("\n")
    docs, cur = {}, None
    for i, line in enumerate(lines):
        m = HEADER.match(line)
        if m and i + 2 < len(lines) and lines[i + 2].startswith("Document Number:"):
            cur = int(m.group(1))
            docs[cur] = {"title": m.group(2).strip(), "body": []}
            continue
        if cur is not None:
            docs[cur]["body"].append(line)
    for d in docs.values():
        body = "\n".join(d["body"]).rstrip().rstrip("-").rstrip()
        src = re.search(r"^Source: (.*)$", body, re.M)
        d["src"] = src.group(1) if src else ""
        d["text"] = body
    return docs


def wrap(text, width=160):
    out = []
    for line in text.split("\n"):
        while len(line) > width:
            cut = max(line.rfind(". ", 0, width), line.rfind("; ", 0, width), line.rfind(" ", 0, width))
            cut = cut + 1 if cut > 40 else width
            out.append(line[:cut])
            line = line[cut:].lstrip()
        out.append(line)
    return "\n".join(out)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    docs = load()
    if argv[0] == "--list":
        for n, d in docs.items():
            print(f"{n:3}  {d['title'][:60]:60}  {d['src']}")
        return 0
    if argv[0] == "--find":
        needle = " ".join(argv[1:]).lower()
        for n, d in docs.items():
            hits = d["text"].lower().count(needle)
            if hits or needle in d["title"].lower():
                print(f"{n:3}  {hits:4} hits  {d['title'][:60]:60}  {d['src']}")
        return 0
    for arg in argv:
        d = docs.get(int(arg))
        if not d:
            print(f"# no document {arg}")
            continue
        print(f"# {arg}. {d['title']}\n")
        print(wrap(d["text"]))
        print()
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
