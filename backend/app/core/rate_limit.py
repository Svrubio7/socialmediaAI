"""
Lightweight in-memory rate limiting helpers.

Intended for low-volume abuse protection (for example signed upload URL issuance).
This is process-local and best-effort; for distributed enforcement use Redis.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
import time
from typing import Deque, DefaultDict, Tuple


@dataclass
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._events: DefaultDict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, *, limit: int, window_seconds: int) -> RateLimitDecision:
        """
        Record an attempt and decide if it should be allowed.

        Args:
            key: Stable key (for example `signed_upload:user_id`).
            limit: Maximum number of allowed events within the window.
            window_seconds: Sliding window size in seconds.
        """
        now = time.monotonic()
        lower_bound = now - max(1, int(window_seconds))
        max_events = max(1, int(limit))

        with self._lock:
            events = self._events[key]
            while events and events[0] < lower_bound:
                events.popleft()

            if len(events) >= max_events:
                retry_after = max(1, int(events[0] + window_seconds - now))
                return RateLimitDecision(
                    allowed=False,
                    retry_after_seconds=retry_after,
                )

            events.append(now)
            return RateLimitDecision(allowed=True, retry_after_seconds=0)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


signed_upload_rate_limiter = InMemoryRateLimiter()

