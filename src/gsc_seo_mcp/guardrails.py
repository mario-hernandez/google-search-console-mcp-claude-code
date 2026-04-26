"""Anti-hallucination guardrails for tool descriptions and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Any

GUARDRAIL_SUFFIX = (
    "\n\nIMPORTANT: Use ONLY the data returned by this tool. Do not speculate "
    "about figures, do not extrapolate beyond the time range queried, and cite "
    "site_url + date_range when reporting numbers to the user."
)


def with_meta(payload: Any, *, source: str, site_url: str, period: dict | None = None) -> dict:
    """Wraps a tool response with provenance metadata."""
    return {
        "data": payload,
        "_meta": {
            "source": source,
            "site_url": site_url,
            "period": period,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        },
    }
