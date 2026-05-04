#!/usr/bin/env python3
"""Generate a search index JSON for Hugo docs."""

import json
import os
import re

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "static", "search-index.json")


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text


def extract_title(text):
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def build_index():
    entries = []
    for root, _, files in os.walk(CONTENT_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, CONTENT_DIR)
            with open(path, encoding="utf-8") as f:
                raw = f.read()
            body = strip_frontmatter(raw)
            title = extract_title(body) or fname.replace(".md", "")
            url = "/" + rel.replace("\\", "/").replace("_index.", "").replace(".md", "/")
            entries.append({"title": title, "url": url, "content": body[:500]})

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Search index written: {len(entries)} entries -> {OUTPUT_FILE}")


if __name__ == "__main__":
    build_index()
