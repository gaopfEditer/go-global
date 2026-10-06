from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Job:
    platform: str
    id: str
    url: str
    title: str
    description: str
    budget_min: float | None
    budget_max: float | None
    currency: str | None
    job_type: str | None
    bids_count: int | None
    posted_at: int | None
    tags: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, Any]:
        return asdict(self)
