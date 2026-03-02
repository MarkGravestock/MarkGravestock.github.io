#!/usr/bin/env python3
"""
Fetches all bookmarks from the Raindrop.io API (paginated) and regenerates
bookmarks/index.md. Preserves the Jekyll frontmatter and CSS block at the top.
Entries are grouped by month in reverse-chronological order.

Requires env var: RAINDROP_TOKEN
"""

import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

API_BASE = "https://api.raindrop.io/rest/v1/raindrops/64296840"  # public collection
PER_PAGE = 50

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
.bookmark-note {
  font-size: 0.9em;
  color: #555;
  margin-top: 0.25em;
}
</style>

A collection of useful things I've found on the web.
"""


def fetch_all_bookmarks(token: str) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    items = []
    page = 0

    while True:
        url = f"{API_BASE}?perpage={PER_PAGE}&page={page}"
        print(f"  Fetching page {page}...")

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        page_items = data.get("items", [])
        items.extend(page_items)

        if len(page_items) < PER_PAGE:
            break
        page += 1

    return items


def parse_bookmarks(raw_items: list[dict]) -> list[dict]:
    bookmarks = []

    for item in raw_items:
        title = (item.get("title") or "").strip()
        link = item.get("link") or ""
        domain = item.get("domain") or ""
        tags = [t for t in (item.get("tags") or []) if t.lower() not in SKIP_TAGS]
        note = (item.get("note") or "").strip()

        created_str = item.get("created") or ""
        try:
            date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            date = datetime.now(tz=timezone.utc)

        bookmarks.append({
            "title": title,
            "link": link,
            "date": date,
            "tags": tags,
            "domain": domain,
            "note": note,
        })

    return sorted(bookmarks, key=lambda x: x["date"], reverse=True)


def render_entry(item: dict) -> str:
    tags_html = ""
    if item["tags"]:
        tag_spans = " ".join(
            f'<span class="tag">#{tag}</span>' for tag in item["tags"]
        )
        tags_html = f'  <div class="bookmark-tags">{tag_spans}</div>\n'

    note_html = ""
    if item["note"]:
        note_html = f'  <div class="bookmark-note">{item["note"]}</div>\n'

    date = item["date"]
    day = date.day
    date_str = f"{day} {date.strftime('%B')}"

    return (
        '<div class="bookmark">\n'
        f'  <div class="bookmark-title"><a href="{item["link"]}">{item["title"]}</a></div>\n'
        f"{tags_html}"
        f'  <div class="bookmark-meta">{item["domain"]} · {date_str}</div>\n'
        f"{note_html}"
        "</div>\n"
    )


def group_by_month(items: list[dict]) -> dict:
    groups = defaultdict(list)
    for item in items:
        key = item["date"].strftime("%B %Y")
        groups[key].append(item)
    return dict(
        sorted(groups.items(), key=lambda x: datetime.strptime(x[0], "%B %Y"), reverse=True)
    )


def render_file(items: list[dict]) -> str:
    groups = group_by_month(items)
    sections = []
    for month, month_items in groups.items():
        entries = "\n".join(render_entry(item) for item in month_items)
        sections.append(f"## {month}\n\n{entries}")
    return FRONTMATTER_AND_STYLES + "\n" + "\n---\n\n".join(sections) + "\n"


def main():
    token = os.environ.get("RAINDROP_TOKEN")
    if not token:
        print("Error: RAINDROP_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    print("Fetching bookmarks from Raindrop.io API...")
    raw_items = fetch_all_bookmarks(token)
    print(f"  Total fetched: {len(raw_items)}")

    bookmarks = parse_bookmarks(raw_items)
    new_content = render_file(bookmarks)

    existing_content = BOOKMARKS_FILE.read_text(encoding="utf-8") if BOOKMARKS_FILE.exists() else ""

    if new_content == existing_content:
        print("No changes — bookmarks/index.md is already up to date.")
        sys.exit(0)

    BOOKMARKS_FILE.write_text(new_content, encoding="utf-8")
    print(f"Updated {BOOKMARKS_FILE}")


if __name__ == "__main__":
    main()
