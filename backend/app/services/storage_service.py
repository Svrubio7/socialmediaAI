"""
Storage services used for videos/branding assets.
Supports local filesystem and Supabase Storage.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import Request
from supabase import create_client
from storage3.types import CreateSignedUploadUrlOptions

from app.core.config import settings

logger = logging.getLogger(__name__)


def _supabase_role_from_jwt(token: str) -> Optional[str]:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload = parts[1]
        padded = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
        role = data.get("role")
        return role if isinstance(role, str) else None
    except Exception:
        return None


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

    def save_bytes(self, storage_path: str, content: bytes, content_type: Optional[str] = None) -> Path:
        dst = self.absolute_path(storage_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(content)
        return dst

    def save_file(self, storage_path: str, local_path: str, content_type: Optional[str] = None) -> Path:
        dst = self.absolute_path(storage_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, dst)
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

    def get_write_path(self, storage_path: str) -> str:
        """Return local path to write output files directly into storage."""
        return str(self.absolute_path(storage_path))

    def finalize_write(self, storage_path: str, local_path: str, content_type: Optional[str] = None) -> None:
        """No-op for local storage (already written to storage path)."""
        _ = storage_path, local_path, content_type

    def build_public_url(self, storage_path: str, request: Optional[Request] = None) -> Optional[str]:
        rel = self._normalize_relative(storage_path)
        base = (settings.STORAGE_PUBLIC_BASE_URL or "").rstrip("/")
        if not base:
            if request is not None:
                base = str(request.base_url).rstrip("/")
            else:
                base = "http://localhost:8000"
        return f"{base}/storage/{rel}"

    def create_signed_upload_url(
        self,
        storage_path: str,
        *,
        content_type: Optional[str] = None,
        upsert: bool = False,
    ) -> dict:
        _ = storage_path, content_type, upsert
        raise RuntimeError("Signed upload URLs require STORAGE_BACKEND=supabase")


class SupabaseStorageService:
    """
    Supabase Storage backed service (private by default).
    Uses one bucket for all paths: videos/, thumbnails/, editor/outputs/, branding/
    """

    def __init__(self, bucket: Optional[str] = None) -> None:
        supabase_url = (settings.SUPABASE_URL or "").strip()
        supabase_key = (settings.SUPABASE_KEY or "").strip()
        if not supabase_url or not supabase_key:
            raise RuntimeError("Supabase storage requires SUPABASE_URL and SUPABASE_KEY")
        self.bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
        self.client = create_client(supabase_url, supabase_key)
        self.private = bool(settings.SUPABASE_STORAGE_PRIVATE)
        self.signed_ttl = int(settings.SUPABASE_STORAGE_SIGNED_URL_TTL or 3600)
        self.temp_dir = Path(settings.TEMP_PROCESSING_DIR or tempfile.gettempdir()).resolve()
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        role = _supabase_role_from_jwt(supabase_key)
        if self.private and role == "anon":
            logger.warning(
                "SUPABASE_KEY appears to be an anon key; signed URLs may fail for private buckets. "
                "Use a service role key or set SUPABASE_STORAGE_PRIVATE=false for public buckets."
            )

    def _normalize_relative(self, storage_path: str) -> str:
        p = Path(storage_path.replace("\\", "/"))
        if p.is_absolute() or ".." in p.parts:
            raise ValueError("Invalid storage path")
        return p.as_posix().lstrip("/")

    def _bucket_client(self):
        return self.client.storage.from_(self.bucket)

    def save_bytes(self, storage_path: str, content: bytes, content_type: Optional[str] = None) -> Path:
        rel = self._normalize_relative(storage_path)
        options = {"content-type": content_type or "application/octet-stream", "upsert": True}
        res = self._bucket_client().upload(rel, content, file_options=options)
        if isinstance(res, dict) and res.get("error"):
            raise RuntimeError(str(res["error"]))
        return Path(rel)

    def save_file(self, storage_path: str, local_path: str, content_type: Optional[str] = None) -> Path:
        rel = self._normalize_relative(storage_path)
        options = {"content-type": content_type or "application/octet-stream", "upsert": True}
        with open(local_path, "rb") as handle:
            res = self._bucket_client().upload(rel, handle, file_options=options)
        if isinstance(res, dict) and res.get("error"):
            raise RuntimeError(str(res["error"]))
        return Path(rel)

    def delete(self, storage_path: str) -> None:
        try:
            rel = self._normalize_relative(storage_path)
        except ValueError:
            return
        res = self._bucket_client().remove([rel])
        if isinstance(res, dict) and res.get("error"):
            raise RuntimeError(str(res["error"]))

    def exists(self, storage_path: str) -> bool:
        try:
            rel = self._normalize_relative(storage_path)
        except ValueError:
            return False
        parent = str(Path(rel).parent).replace("\\", "/")
        if parent == ".":
            parent = ""
        name = Path(rel).name
        res = self._bucket_client().list(parent)
        if isinstance(res, dict):
            data = res.get("data") if "data" in res else res.get("result")
            if isinstance(data, list):
                return any(entry.get("name") == name for entry in data)
            if isinstance(res.get("error"), Exception):
                return False
            if isinstance(res.get("error"), str):
                return False
        if isinstance(res, list):
            return any(entry.get("name") == name for entry in res)
        return False

    def resolve_for_processing(self, storage_path: str) -> str:
        """
        Download Supabase object to temp and return local path.
        """
        raw = Path(storage_path)
        if raw.is_absolute() and raw.exists():
            return str(raw)
        rel = self._normalize_relative(storage_path)
        tmp_path = self.temp_dir / f"{uuid4()}_{Path(rel).name}"
        res = self._bucket_client().download(rel)
        data = None
        if isinstance(res, dict):
            if res.get("error"):
                raise RuntimeError(str(res["error"]))
            data = res.get("data")
        else:
            data = res
        if data is None:
            raise RuntimeError("Failed to download storage object")
        tmp_path.write_bytes(data)
        return str(tmp_path)

    def get_write_path(self, storage_path: str) -> str:
        """Return a temp path to write output files before upload."""
        rel = self._normalize_relative(storage_path)
        return str(self.temp_dir / f"{uuid4()}_{Path(rel).name}")

    def finalize_write(self, storage_path: str, local_path: str, content_type: Optional[str] = None) -> None:
        self.save_file(storage_path, local_path, content_type=content_type)
        try:
            os.remove(local_path)
        except OSError:
            pass

    def build_public_url(self, storage_path: str, request: Optional[Request] = None) -> Optional[str]:
        rel = self._normalize_relative(storage_path)
        if self.private:
            try:
                res = self._bucket_client().create_signed_url(rel, self.signed_ttl)
            except Exception as exc:
                logger.warning("Failed to create signed URL for %s: %s", rel, exc)
                return None
            if isinstance(res, dict):
                for key in ("signedURL", "signedUrl", "signed_url"):
                    if key in res and res[key]:
                        return res[key]
                data = res.get("data")
                if isinstance(data, dict):
                    for key in ("signedURL", "signedUrl", "signed_url"):
                        if key in data and data[key]:
                            return data[key]
            logger.warning("Signed URL response missing url for %s", rel)
            return None

        try:
            res = self._bucket_client().get_public_url(rel)
        except Exception as exc:
            logger.warning("Failed to get public URL for %s: %s", rel, exc)
            return None
        if isinstance(res, dict):
            data = res.get("data") if "data" in res else res
            if isinstance(data, dict):
                url = data.get("publicUrl") or data.get("publicURL")
                if url:
                    return url
        if isinstance(res, str):
            return res
        logger.warning("Public URL response missing url for %s", rel)
        return None

    def create_signed_upload_url(
        self,
        storage_path: str,
        *,
        content_type: Optional[str] = None,
        upsert: bool = False,
    ) -> dict:
        rel = self._normalize_relative(storage_path)
        options = CreateSignedUploadUrlOptions(upsert="true") if upsert else None
        response = self._bucket_client().create_signed_upload_url(rel, options=options)

        signed_url = None
        token = None
        if isinstance(response, dict):
            signed_url = (
                response.get("signed_url")
                or response.get("signedUrl")
                or response.get("signedURL")
            )
            token = response.get("token")

        if not signed_url:
            raise RuntimeError("Supabase signed upload URL response missing URL")

        return {
            "bucket": self.bucket,
            "storage_path": rel,
            "signed_url": signed_url,
            "token": token,
            "content_type": content_type or "application/octet-stream",
            "expires_in": self.signed_ttl,
        }


def get_storage_service():
    if (settings.STORAGE_BACKEND or "").lower() == "supabase":
        return SupabaseStorageService()
    return LocalStorageService()
