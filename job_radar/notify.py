from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from job_radar.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from job_radar.filters import matched_keywords
from job_radar.models import Job


def send_telegram(job: Job) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    keywords = ", ".join(matched_keywords(job)) or "—"
    budget = _format_budget(job)
    snippet = job.description[:500]
    if len(job.description) > 500:
        snippet += "…"
    text = (
        f"[{job.platform}] {job.title}\n"
        f"{job.url}\n"
        f"Budget: {budget}\n"
        f"Keywords: {keywords}\n\n"
        f"{snippet}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = urllib.parse.urlencode(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return bool(payload.get("ok"))
    except urllib.error.HTTPError:
        return False


def _format_budget(job: Job) -> str:
    if job.budget_min is None and job.budget_max is None:
        return "n/a"
    cur = job.currency or ""
    if job.budget_min is not None and job.budget_max is not None:
        return f"{cur} {job.budget_min:g}–{job.budget_max:g}".strip()
    if job.budget_max is not None:
        return f"{cur} ≤ {job.budget_max:g}".strip()
    return f"{cur} ≥ {job.budget_min:g}".strip()
