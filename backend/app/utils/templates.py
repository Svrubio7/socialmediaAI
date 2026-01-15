"""
Template system for caching LLM responses.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import json


class TemplateCache:
    """
    Cache for LLM response templates to reduce API costs.
    """

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize template cache.
        
        Args:
            similarity_threshold: Minimum similarity score to use cached response
        """
        self.similarity_threshold = similarity_threshold
        self._cache: Dict[str, Dict[str, Any]] = {}  # In production, use Redis or DB
        self._hit_count: Dict[str, int] = {}
        self._miss_count: int = 0

    def _generate_key(self, params: Dict[str, Any]) -> str:
        """Generate a cache key from request parameters."""
        # Sort and serialize params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()

    def _calculate_similarity(
        self,
        params1: Dict[str, Any],
        params2: Dict[str, Any],
    ) -> float:
        """
        Calculate similarity between two request parameter sets.
        
        Simple keyword-based similarity for MVP.
        """
        # Convert to sets of key-value pairs
        set1 = set(str(v) for v in params1.values() if v is not None)
        set2 = set(str(v) for v in params2.values() if v is not None)
        
        if not set1 or not set2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    def get(
        self,
        template_type: str,
        params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Get a cached template response if available.
        
        Args:
            template_type: Type of template (strategy, script, etc.)
            params: Request parameters
            
        Returns:
            Cached response or None
        """
        # Check for exact match first
        key = self._generate_key({"type": template_type, **params})
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                self._hit_count[key] = self._hit_count.get(key, 0) + 1
                return entry["response"]
        
        # Check for similar cached responses
        for cached_key, entry in self._cache.items():
            if entry.get("type") != template_type:
                continue
            if datetime.utcnow() >= entry["expires_at"]:
                continue
            
            similarity = self._calculate_similarity(params, entry["params"])
            if similarity >= self.similarity_threshold:
                self._hit_count[cached_key] = self._hit_count.get(cached_key, 0) + 1
                return entry["response"]
        
        self._miss_count += 1
        return None

    def set(
        self,
        template_type: str,
        params: Dict[str, Any],
        response: Dict[str, Any],
        ttl_hours: int = 24,
    ) -> None:
        """
        Cache a template response.
        
        Args:
            template_type: Type of template
            params: Request parameters
            response: Response to cache
            ttl_hours: Time to live in hours
        """
        key = self._generate_key({"type": template_type, **params})
        self._cache[key] = {
            "type": template_type,
            "params": params,
            "response": response,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=ttl_hours),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = sum(self._hit_count.values())
        total_requests = total_hits + self._miss_count
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_entries": len(self._cache),
            "total_hits": total_hits,
            "total_misses": self._miss_count,
            "hit_rate": f"{hit_rate:.2f}%",
        }

    def clear_expired(self) -> int:
        """Clear expired entries and return count of removed entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry["expires_at"] <= now
        ]
        for key in expired_keys:
            del self._cache[key]
            if key in self._hit_count:
                del self._hit_count[key]
        return len(expired_keys)


# Global template cache instance
template_cache = TemplateCache()


def get_cached_response(
    template_type: str,
    params: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Get a cached template response."""
    return template_cache.get(template_type, params)


def cache_response(
    template_type: str,
    params: Dict[str, Any],
    response: Dict[str, Any],
    ttl_hours: int = 24,
) -> None:
    """Cache a template response."""
    template_cache.set(template_type, params, response, ttl_hours)
