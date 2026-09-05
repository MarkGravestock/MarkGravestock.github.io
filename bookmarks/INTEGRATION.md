# Bookmarks Integration

`bookmarks/index.md` is automatically regenerated from a Raindrop.io RSS feed.
**Do not edit it by hand** — changes will be overwritten on the next run.

## How It Works

```
Raindrop.io (public collection)
        │
        │  RSS feed (XML)
        ▼
_scripts/update_bookmarks.py
        │
        │  parses items: title, link, date, tags, domain
        │  groups by month (reverse-chronological)
        │  renders HTML div entries
        ▼
bookmarks/index.md  (regenerated)
        │
        ▼
GitHub Actions commits + pushes (if changed)
        │
        ▼
GitHub Pages serves the updated page
```

## Trigger

The workflow runs:
- **Daily at 08:00 UTC** (via cron schedule)
- **On demand** via the Actions tab → "Update Bookmarks" → "Run workflow"

## Files

| File | Purpose |
|---|---|
| `.github/workflows/update-bookmarks.yml` | GitHub Actions workflow |
| `_scripts/update_bookmarks.py` | Fetch, parse and render the feed |
| `bookmarks/index.md` | Generated output — do not edit manually |

## Data Source

- **Service:** Raindrop.io API
- **Endpoint:** `https://api.raindrop.io/rest/v1/raindrops/0` (all collections)
- **Pagination:** 50 items per page, fetches all pages
- **Auth:** Bearer token stored as GitHub Secret `RAINDROP_TOKEN`

Tags with system values (`article`, `link`, `public`, `video`, `image`, `document`, `audio`)
are filtered out and not shown on the page.

Personal notes added in Raindrop are included when present.

## One-time Setup

1. Go to https://app.raindrop.io/settings/integrations
2. Create a test token
3. Add it to your GitHub repo: Settings → Secrets → Actions → `RAINDROP_TOKEN`
