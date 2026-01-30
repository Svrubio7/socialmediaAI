"""
Branding (user assets) endpoints.
"""

import os
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.user_asset import UserAsset

router = APIRouter()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ASSET_TYPES = ["logo", "image", "watermark"]


class BrandingAssetResponse(BaseModel):
    """Branding asset response schema."""
    id: str
    type: str
    filename: str
    url: Optional[str] = None
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandingAssetListResponse(BaseModel):
    """Branding asset list response schema."""
    items: List[BrandingAssetResponse]
    total: int


def validate_asset_file(file: UploadFile, asset_type: str) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    if asset_type not in ASSET_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid type. Allowed: {', '.join(ASSET_TYPES)}",
        )


@router.get("", response_model=BrandingAssetListResponse)
async def list_branding_assets(
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user branding assets."""
    query = db.query(UserAsset).filter(UserAsset.user_id == current_user.id)
    if type_filter and type_filter in ASSET_TYPES:
        query = query.filter(UserAsset.type == type_filter)
    total = query.count()
    items = query.order_by(UserAsset.created_at.desc()).all()
    return BrandingAssetListResponse(
        items=[
            BrandingAssetResponse(
                id=str(a.id),
                type=a.type,
                filename=a.filename,
                url=a.url,
                metadata=a.metadata or {},
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in items
        ],
        total=total,
    )


@router.post("/upload", response_model=BrandingAssetResponse)
async def upload_branding_asset(
    file: UploadFile = File(...),
    asset_type: str = "image",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a branding asset (logo, image, watermark)."""
    validate_asset_file(file, asset_type)
    asset_id = uuid4()
    ext = os.path.splitext(file.filename or ".png")[1].lower()
    storage_filename = f"{asset_id}{ext}"
    storage_path = f"branding/{current_user.id}/{storage_filename}"

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    # TODO: Upload to Supabase Storage and set url
    # For now we only persist metadata; url can be derived or stored when storage is wired.
    url = None

    asset = UserAsset(
        id=asset_id,
        user_id=current_user.id,
        type=asset_type,
        filename=file.filename or storage_filename,
        storage_path=storage_path,
        url=url,
        metadata={"original_filename": file.filename},
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return BrandingAssetResponse(
        id=str(asset.id),
        type=asset.type,
        filename=asset.filename,
        url=asset.url,
        metadata=asset.metadata or {},
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.get("/{asset_id}", response_model=BrandingAssetResponse)
async def get_branding_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single branding asset by id."""
    asset = db.query(UserAsset).filter(
        UserAsset.id == UUID(asset_id),
        UserAsset.user_id == current_user.id,
    ).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branding asset not found")
    return BrandingAssetResponse(
        id=str(asset.id),
        type=asset.type,
        filename=asset.filename,
        url=asset.url,
        metadata=asset.metadata or {},
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.delete("/{asset_id}")
async def delete_branding_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a branding asset."""
    asset = db.query(UserAsset).filter(
        UserAsset.id == UUID(asset_id),
        UserAsset.user_id == current_user.id,
    ).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branding asset not found")
    db.delete(asset)
    db.commit()
    return {"ok": True}
