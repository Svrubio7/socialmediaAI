from __future__ import annotations

import logging
from collections import defaultdict, deque
from threading import Lock
from time import time
from typing import Any, Deque, Dict, Optional

logger = logging.getLogger(__name__)


class MetricsLiteStore:
    def __init__(self, sample_size: int = 120) -> None:
        self._sample_size = sample_size
        self._durations: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=self._sample_size)
        )
        self._counts: Dict[str, int] = defaultdict(int)
        self._last_update_ts: float = time()
        self._lock = Lock()

    def observe_duration(
        self,
        metric_name: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        safe_name = (metric_name or "").strip()
        if not safe_name:
            return
        if duration_ms < 0:
            return
        value = float(duration_ms)

        with self._lock:
            self._durations[safe_name].append(value)
            self._counts[safe_name] += 1
            self._last_update_ts = time()

        if metadata:
            logger.warning(
                "metrics-lite %s duration_ms=%.2f metadata=%s",
                safe_name,
                value,
                metadata,
            )
        else:
            logger.warning("metrics-lite %s duration_ms=%.2f", safe_name, value)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            metrics: Dict[str, Any] = {}
            for metric_name, samples in self._durations.items():
                values = list(samples)
                if not values:
                    continue
                sorted_values = sorted(values)
                p95_index = max(0, int(round((len(sorted_values) - 1) * 0.95)))
                metrics[metric_name] = {
                    "count": self._counts.get(metric_name, len(values)),
                    "window_size": len(values),
                    "avg_ms": round(sum(values) / len(values), 2),
                    "min_ms": round(min(values), 2),
                    "max_ms": round(max(values), 2),
                    "p95_ms": round(sorted_values[p95_index], 2),
                }

            return {
                "updated_at_unix": self._last_update_ts,
                "metrics": metrics,
            }


metrics_lite_store = MetricsLiteStore()


def observe_duration(
    metric_name: str,
    duration_ms: float,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    metrics_lite_store.observe_duration(metric_name, duration_ms, metadata=metadata)


def get_metrics_snapshot() -> Dict[str, Any]:
    return metrics_lite_store.snapshot()
