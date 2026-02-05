"""
Local storage service used for videos/branding assets.
"""

from pathlib import Path
from typing import Optional

from fastapi import Request

from app.core.config import settings


class LocalStorageService:
    """Simple filesystem-backed storage with public URL helpers."""

    def __init__(self, root_dir: Optional[str] = None) -> None:
        self.root = Path(root_dir or settings.LOCAL_STORAGE_DIR).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _normalize_relative(self, storage_path: str) -> str:
        p = Path(storage_path.replace("\\", "/"))
        if p.is_absolute() or ".." in p.parts:
            raise ValueError("Invalid storage path")
        return p.as_posix().lstrip("/")

    def absolute_path(self, storage_path: str) -> Path:
        rel = self._normalize_relative(storage_path)
        return (self.root / rel).resolve()

    def save_bytes(self, storage_path: str, content: bytes) -> Path:
        dst = self.absolute_path(storage_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(content)
        return dst

    def delete(self, storage_path: str) -> None:
        try:
            path = self.absolute_path(storage_path)
        except ValueError:
            return
        if path.exists() and path.is_file():
            path.unlink()

    def exists(self, storage_path: str) -> bool:
        try:
            return self.absolute_path(storage_path).exists()
        except ValueError:
            return False

    def resolve_for_processing(self, storage_path: str) -> str:
        """
        Resolve DB storage path to a local filesystem path.
        Supports absolute paths and relative paths under the storage root.
        """
        raw = Path(storage_path)
        if raw.is_absolute():
            return str(raw)
        return str(self.absolute_path(storage_path))

    def build_public_url(self, storage_path: str, request: Optional[Request] = None) -> str:
        rel = self._normalize_relative(storage_path)
        if request is not None:
            base = str(request.base_url).rstrip("/")
        else:
            base = (settings.STORAGE_PUBLIC_BASE_URL or "").rstrip("/")
            if not base:
                base = "http://localhost:8000"
        return f"{base}/storage/{rel}"

