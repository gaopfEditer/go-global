from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from job_radar.db import JobStore


def maybe_write_daily_summary(store: JobStore, summary_dir: Path) -> Path | None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last = store.get_meta("last_summary_date")
    if last == today:
        return None
    path = write_daily_summary(store, summary_dir, today)
    store.set_meta("last_summary_date", today)
    return path


def write_daily_summary(store: JobStore, summary_dir: Path, day: str) -> Path:
    summary_dir.mkdir(parents=True, exist_ok=True)
    rows = store.jobs_matched_on_day(day)
    lines = [
        f"# Job radar summary — {day} (UTC)",
        "",
        f"Matched jobs fetched on this day: **{len(rows)}**",
        "",
    ]
    if not rows:
        lines.append("_No matching jobs recorded today._")
    else:
        by_platform: dict[str, list] = {}
        for row in rows:
            by_platform.setdefault(row["platform"], []).append(row)
        for platform in sorted(by_platform):
            lines.append(f"## {platform}")
            lines.append("")
            for row in by_platform[platform]:
                keywords = json.loads(row["matched_keywords"] or "[]")
                kw = ", ".join(keywords) if keywords else "—"
                budget = _row_budget(row)
                lines.append(f"- [{row['title']}]({row['url']}) — {budget} — {kw}")
            lines.append("")
    path = summary_dir / f"summary-{day}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _row_budget(row) -> str:
    cur = row["currency"] or ""
    lo, hi = row["budget_min"], row["budget_max"]
    if lo is None and hi is None:
        return "budget n/a"
    if lo is not None and hi is not None:
        return f"{cur} {lo:g}–{hi:g}".strip()
    if hi is not None:
        return f"{cur} ≤ {hi:g}".strip()
    return f"{cur} ≥ {lo:g}".strip()
