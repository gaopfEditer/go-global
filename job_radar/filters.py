from __future__ import annotations

import re

from job_radar.config import (
    FREELANCER_CURRENCIES,
    FREELANCER_MIN_BUDGET_MAX,
    KEYWORDS,
)
from job_radar.models import Job

_KEYWORD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (kw, re.compile(re.escape(kw), re.IGNORECASE)) for kw in KEYWORDS
]


def matched_keywords(job: Job) -> list[str]:
    haystack = " ".join(
        part for part in (job.title, job.description, " ".join(job.tags)) if part
    )
    return [label for label, pattern in _KEYWORD_PATTERNS if pattern.search(haystack)]


def passes_keyword_filter(job: Job) -> bool:
    return bool(matched_keywords(job))


def passes_freelancer_filter(job: Job) -> bool:
    if job.platform != "freelancer":
        return True
    if job.currency not in FREELANCER_CURRENCIES:
        return False
    if job.budget_max is None:
        return False
    return job.budget_max >= FREELANCER_MIN_BUDGET_MAX


def is_match(job: Job) -> bool:
    return passes_freelancer_filter(job) and passes_keyword_filter(job)
