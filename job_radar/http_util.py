from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def get_json(url: str, timeout: float = 30.0) -> Any:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "freelance-job-radar/1.0 (+https://github.com/local/job-radar)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))
