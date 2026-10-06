from __future__ import annotations

import os
from pathlib import Path

KEYWORDS: tuple[str, ...] = (
    "Next.js",
    "Supabase",
    "Lovable",
    "Bolt",
    "deploy",
    "production",
    "Telegram bot",
    "dashboard",
    "scraper",
    "crypto data",
)

FREELANCER_CURRENCIES: frozenset[str] = frozenset({"USD", "EUR", "GBP"})
FREELANCER_MIN_BUDGET_MAX: float = 300.0

DEFAULT_DB_PATH = Path(os.environ.get("JOB_RADAR_DB", "job_radar.db"))
DEFAULT_SUMMARY_DIR = Path(os.environ.get("JOB_RADAR_SUMMARY_DIR", "summaries"))
DEFAULT_INTERVAL_MINUTES = int(os.environ.get("JOB_RADAR_INTERVAL_MINUTES", "30"))
DEFAULT_FREELANCER_LIMIT = int(os.environ.get("JOB_RADAR_FREELANCER_LIMIT", "100"))

FREELANCER_API = "https://www.freelancer.com/api/projects/0.1/projects/active/"
HN_FIREBASE = "https://hacker-news.firebaseio.com/v0"
HN_THREAD_AUTHOR = "whoishiring"
HN_THREAD_TITLE_RE = r"ask hn:\s*freelancer\?\s*seeking freelancer"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
