from __future__ import annotations

import sys
import time
from datetime import datetime, timezone

from job_radar.config import DEFAULT_DB_PATH, DEFAULT_INTERVAL_MINUTES, DEFAULT_SUMMARY_DIR
from job_radar.db import JobStore
from job_radar.notify import send_telegram
from job_radar.sources.freelancer import fetch_freelancer_jobs
from job_radar.sources.hackernews import fetch_hn_jobs
from job_radar.summary import maybe_write_daily_summary


def run_once(db_path=DEFAULT_DB_PATH, summary_dir=DEFAULT_SUMMARY_DIR) -> int:
    store = JobStore(db_path)
    try:
        jobs = []
        errors: list[str] = []

        try:
            jobs.extend(fetch_freelancer_jobs())
        except Exception as exc:  # noqa: BLE001 — log and continue with other source
            errors.append(f"freelancer: {exc}")

        try:
            jobs.extend(fetch_hn_jobs())
        except Exception as exc:
            errors.append(f"hacker_news: {exc}")

        new_matches = store.insert_jobs(jobs)
        for job in new_matches:
            if send_telegram(job):
                store.mark_notified(job.platform, job.id)

        summary_path = maybe_write_daily_summary(store, summary_dir)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(
            f"[{ts}] fetched={len(jobs)} new_matches={len(new_matches)} "
            f"errors={len(errors)}"
        )
        for err in errors:
            print(f"  warning: {err}", file=sys.stderr)
        if summary_path:
            print(f"  daily summary: {summary_path}")
        return 0 if not errors else 1
    finally:
        store.close()


def run_loop(
    db_path=DEFAULT_DB_PATH,
    summary_dir=DEFAULT_SUMMARY_DIR,
    interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
) -> None:
    interval_seconds = max(1, interval_minutes) * 60
    while True:
        run_once(db_path=db_path, summary_dir=summary_dir)
        time.sleep(interval_seconds)
