# Freelance Job Radar

Minimal Python job radar that polls public APIs (no login, no scraping behind auth or Cloudflare bypass) and notifies you on Telegram when new jobs match your filters.

## Sources

| Platform | API |
|----------|-----|
| Freelancer.com | [Public active projects API](https://www.freelancer.com/api/projects/0.1/projects/active/) |
| Hacker News | [Official Firebase API](https://github.com/HackerNews/API) — latest monthly *Ask HN: Freelancer? Seeking freelancer?* thread from [@whoishiring](https://news.ycombinator.com/user?id=whoishiring) |

## Filters

**Keywords** (case-insensitive, title + description + tags): Next.js, Supabase, Lovable, Bolt, deploy, production, Telegram bot, dashboard, scraper, crypto data.

**Freelancer-only:** currency ∈ {USD, EUR, GBP} and `budget_max >= 300`.

All fetched jobs are stored in SQLite. Deduplication uses `(platform, id)`. Telegram alerts are sent only for **new** jobs that pass all filters.

## Setup

```bash
cd go-global
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
```

## Run

**Single fetch:**

```bash
python -m job_radar once
```

**Loop every 30 minutes (default):**

```bash
python -m job_radar loop
```

Custom interval:

```bash
python -m job_radar loop --interval-minutes 30
```

## Outputs

- **SQLite:** `job_radar.db` (override with `JOB_RADAR_DB`)
- **Daily Markdown summary:** `summaries/summary-YYYY-MM-DD.md` (UTC, one file per day after the first run that day)

## Environment variables

See `.env.example`. Telegram vars are optional; if unset, matching jobs are still stored but not pushed.

## Compliance

- Uses documented public JSON APIs only
- Does not log in, submit proposals, or bypass captcha / Cloudflare
- Does not scrape pages that require authentication

## Project layout

```
job_radar/
  config.py          # keywords, thresholds, env
  db.py              # SQLite storage
  filters.py         # match logic
  notify.py          # Telegram
  summary.py         # daily Markdown
  sources/
    freelancer.py
    hackernews.py
  runner.py
  __main__.py        # CLI entry
```
