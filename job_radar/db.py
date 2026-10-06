from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from job_radar.filters import is_match, matched_keywords
from job_radar.models import Job


class JobStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                platform TEXT NOT NULL,
                id TEXT NOT NULL,
                url TEXT,
                title TEXT,
                description TEXT,
                budget_min REAL,
                budget_max REAL,
                currency TEXT,
                job_type TEXT,
                bids_count INTEGER,
                posted_at INTEGER,
                tags TEXT,
                fetched_at INTEGER NOT NULL,
                matched INTEGER NOT NULL DEFAULT 0,
                matched_keywords TEXT,
                notified INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (platform, id)
            );

            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def insert_jobs(self, jobs: list[Job]) -> list[Job]:
        """Insert new jobs; return newly inserted jobs that pass match filters."""
        now = int(time.time())
        new_matches: list[Job] = []
        for job in jobs:
            matched = is_match(job)
            keywords = matched_keywords(job) if matched else []
            try:
                self._conn.execute(
                    """
                    INSERT INTO jobs (
                        platform, id, url, title, description,
                        budget_min, budget_max, currency, job_type,
                        bids_count, posted_at, tags, fetched_at,
                        matched, matched_keywords, notified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        job.platform,
                        job.id,
                        job.url,
                        job.title,
                        job.description,
                        job.budget_min,
                        job.budget_max,
                        job.currency,
                        job.job_type,
                        job.bids_count,
                        job.posted_at,
                        json.dumps(job.tags, ensure_ascii=False),
                        now,
                        1 if matched else 0,
                        json.dumps(keywords, ensure_ascii=False),
                    ),
                )
            except sqlite3.IntegrityError:
                continue
            if matched:
                new_matches.append(job)
        self._conn.commit()
        return new_matches

    def mark_notified(self, platform: str, job_id: str) -> None:
        self._conn.execute(
            "UPDATE jobs SET notified = 1 WHERE platform = ? AND id = ?",
            (platform, job_id),
        )
        self._conn.commit()

    def get_meta(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self._conn.commit()

    def jobs_matched_on_day(self, day: str) -> list[sqlite3.Row]:
        """day format: YYYY-MM-DD (UTC)."""
        start_dt = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        start = int(start_dt.timestamp())
        end = start + 86400
        return list(
            self._conn.execute(
                """
                SELECT * FROM jobs
                WHERE matched = 1 AND fetched_at >= ? AND fetched_at < ?
                ORDER BY fetched_at DESC
                """,
                (start, end),
            )
        )
