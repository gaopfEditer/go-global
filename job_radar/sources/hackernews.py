from __future__ import annotations

import html
import re
from collections import deque

from job_radar.config import HN_FIREBASE, HN_THREAD_AUTHOR, HN_THREAD_TITLE_RE
from job_radar.http_util import get_json
from job_radar.models import Job

_THREAD_TITLE_PATTERN = re.compile(HN_THREAD_TITLE_RE, re.IGNORECASE)


def fetch_hn_jobs(max_submissions_scan: int = 120) -> list[Job]:
    thread_id = find_latest_freelancer_thread(max_submissions_scan)
    if thread_id is None:
        return []
    story = get_json(f"{HN_FIREBASE}/item/{thread_id}.json")
    comment_ids: list[int] = list(story.get("kids") or [])
    return [_comment_to_job(item) for item in _fetch_items(comment_ids)]


def find_latest_freelancer_thread(max_submissions_scan: int) -> int | None:
    submitted = get_json(f"{HN_FIREBASE}/user/{HN_THREAD_AUTHOR}/submitted.json")
    if not isinstance(submitted, list):
        return None
    for story_id in submitted[:max_submissions_scan]:
        story = get_json(f"{HN_FIREBASE}/item/{story_id}.json")
        title = story.get("title") or ""
        if _THREAD_TITLE_PATTERN.search(title):
            return int(story_id)
    return None


def _fetch_items(ids: list[int]) -> list[dict]:
    items: list[dict] = []
    queue: deque[int] = deque(ids)
    seen: set[int] = set()
    while queue:
        item_id = queue.popleft()
        if item_id in seen:
            continue
        seen.add(item_id)
        item = get_json(f"{HN_FIREBASE}/item/{item_id}.json")
        if not item or item.get("type") != "comment" or item.get("deleted"):
            continue
        items.append(item)
        for child_id in item.get("kids") or []:
            queue.append(int(child_id))
    return items


def _comment_to_job(comment: dict) -> Job:
    text = _strip_html(comment.get("text") or "")
    title = _first_line(text) or f"HN comment {comment['id']}"
    return Job(
        platform="hacker_news",
        id=str(comment["id"]),
        url=f"https://news.ycombinator.com/item?id={comment['id']}",
        title=title[:200],
        description=text,
        budget_min=None,
        budget_max=None,
        currency=None,
        job_type="comment",
        bids_count=None,
        posted_at=comment.get("time"),
        tags=["ask_hn_freelancer"],
    )


def _strip_html(raw: str) -> str:
    unescaped = html.unescape(raw)
    text = re.sub(r"<p>", "\n", unescaped)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _first_line(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned
    return text[:120].strip()
