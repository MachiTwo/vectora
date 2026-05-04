#!/usr/bin/env python3
"""Generate sitemap.xml for Vectora docs."""

import os
import re
from datetime import date

BASE_URL = "https://vectora.github.io"
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "static", "sitemap.xml")
TODAY = date.today().isoformat()


def collect_urls():
    urls = [BASE_URL + "/"]
    for root, _, files in os.walk(CONTENT_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, fname), CONTENT_DIR)
            slug = rel.replace("\\", "/").replace("_index.", "").replace(".md", "/")
            url = BASE_URL + "/" + slug
            if url not in urls:
                urls.append(url)
    return urls


def build_sitemap():
    urls = collect_urls()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append(f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>")
    lines.append("</urlset>")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Sitemap written: {len(urls)} URLs -> {OUTPUT_FILE}")


if __name__ == "__main__":
    build_sitemap()
