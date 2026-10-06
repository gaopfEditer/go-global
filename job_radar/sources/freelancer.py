from __future__ import annotations

import urllib.parse

from job_radar.config import DEFAULT_FREELANCER_LIMIT, FREELANCER_API
from job_radar.http_util import get_json
from job_radar.models import Job


def fetch_freelancer_jobs(limit: int | None = None) -> list[Job]:
    limit = limit or DEFAULT_FREELANCER_LIMIT
    params = urllib.parse.urlencode(
        {
            "limit": limit,
            "sort_field": "time_updated",
            "sort_order": "desc",
            "full_description": "true",
            "job_details": "true",
        }
    )
    payload = get_json(f"{FREELANCER_API}?{params}")
    projects = payload.get("result", {}).get("projects") or []
    jobs: list[Job] = []
    for project in projects:
        currency = (project.get("currency") or {}).get("code")
        budget = project.get("budget") or {}
        bid_stats = project.get("bid_stats") or {}
        seo_url = project.get("seo_url") or str(project.get("id"))
        skill_tags = [j.get("name") for j in (project.get("jobs") or []) if j.get("name")]
        description = project.get("description") or project.get("preview_description") or ""
        jobs.append(
            Job(
                platform="freelancer",
                id=str(project["id"]),
                url=f"https://www.freelancer.com/projects/{seo_url}",
                title=project.get("title") or "",
                description=description,
                budget_min=_float_or_none(budget.get("minimum")),
                budget_max=_float_or_none(budget.get("maximum")),
                currency=currency,
                job_type=project.get("type"),
                bids_count=bid_stats.get("bid_count"),
                posted_at=project.get("time_submitted") or project.get("submitdate"),
                tags=skill_tags,
            )
        )
    return jobs


def _float_or_none(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
