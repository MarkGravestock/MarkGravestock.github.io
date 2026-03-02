#!/usr/bin/env python3
"""
Fetches the Raindrop.io public RSS feed and regenerates bookmarks/index.md.
Preserves the Jekyll frontmatter and CSS block at the top of the file.
Entries are grouped by month in reverse-chronological order.
"""

import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

FEED_URL = "https://bg.raindrop.io/rss/public/64296840"

BOOKMARKS_FILE = Path(__file__).parent.parent / "bookmarks" / "index.md"

# Raindrop system tags to exclude from display
SKIP_TAGS = {"article", "link", "public", "video", "image", "document", "audio"}

FRONTMATTER_AND_STYLES = """\
---
layout: page
title: Bookmarks
---

<style>
.bookmark {
  margin-bottom: 1.5em;
}
.bookmark-title {
  font-weight: bold;
  margin-bottom: 0.25em;
}
.bookmark-title a {
  color: #333;
}
.bookmark-tags {
  margin-bottom: 0.25em;
  font-size: 0.85em;
}
.tag {
  margin-right: 8px;
  color: #3498db;
  font-weight: 500;
}
.bookmark-meta {
  font-size: 0.85em;
  color: #666;
}
</style>

A collection of useful things I've found on the web.
"""


def fetch_feed(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_feed(xml_content: str) -> list[dict]:
    root = ET.fromstring(xml_content)
    channel = root.find("channel")
    items = []

    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_str = item.findtext("pubDate") or ""
        categories = [c.text.strip() for c in item.findall("category") if c.text]

        try:
            pub_date = parsedate_to_datetime(pub_date_str)
        except Exception:
            pub_date = datetime.now()

        tags = [t for t in categories if t.lower() not in SKIP_TAGS]
        domain = urlparse(link).netloc.replace("www.", "")

        items.append({
            "title": title,
            "link": link,
            "date": pub_date,
            "tags": tags,
            "domain": domain,
        })

    return sorted(items, key=lambda x: x["date"], reverse=True)


def render_entry(item: dict) -> str:
    tags_html = ""
    if item["tags"]:
        tag_spans = " ".join(
            f'<span class="tag">#{tag}</span>' for tag in item["tags"]
        )
        tags_html = f'  <div class="bookmark-tags">{tag_spans}</div>\n'

    date_str = item["date"].strftime("%-d %B").lstrip("0")
    # Windows-compatible date formatting (%-d not supported on Windows)
    date_str = item["date"].strftime("%d %B").lstrip("0")

    return (
        '<div class="bookmark">\n'
        f'  <div class="bookmark-title"><a href="{item["link"]}">{item["title"]}</a></div>\n'
        f"{tags_html}"
        f'  <div class="bookmark-meta">{item["domain"]} · {date_str}</div>\n'
        "</div>\n"
    )


def group_by_month(items: list[dict]) -> dict:
    groups = defaultdict(list)
    for item in items:
        key = item["date"].strftime("%B %Y")
        groups[key].append(item)
    # Preserve reverse-chronological month order
    return dict(sorted(groups.items(), key=lambda x: datetime.strptime(x[0], "%B %Y"), reverse=True))


def render_file(items: list[dict]) -> str:
    groups = group_by_month(items)
    sections = []
    for month, month_items in groups.items():
        entries = "\n".join(render_entry(item) for item in month_items)
        sections.append(f"## {month}\n\n{entries}")
    return FRONTMATTER_AND_STYLES + "\n" + "\n---\n\n".join(sections) + "\n"


def main():
    print(f"Fetching {FEED_URL}...")
    xml_content = fetch_feed(FEED_URL)

    print("Parsing feed...")
    items = parse_feed(xml_content)
    print(f"  Found {len(items)} bookmarks")

    new_content = render_file(items)

    existing_content = BOOKMARKS_FILE.read_text(encoding="utf-8") if BOOKMARKS_FILE.exists() else ""

    if new_content == existing_content:
        print("No changes — bookmarks/index.md is already up to date.")
        sys.exit(0)

    BOOKMARKS_FILE.write_text(new_content, encoding="utf-8")
    print(f"Updated {BOOKMARKS_FILE}")
    sys.exit(0)


if __name__ == "__main__":
    main()
