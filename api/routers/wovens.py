"""
API router for woven-related endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import math

from api.database import get_db
from api.models import WovenInfo
from api.schemas import WovenListItem, WovenListResponse, WovenDetail, SimilarWovenItem
from api.config import get_settings

router = APIRouter(prefix="/wovens", tags=["Wovens"])
settings = get_settings()


@router.get("", response_model=WovenListResponse)
def list_wovens(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(None, ge=1, description="Number of items per page"),
    color_name: Optional[str] = Query(None, description="Filter by color name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of wovens with optional filters.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **color_name**: Filter by color name (case-insensitive, partial match)
    - **category**: Filter by category (case-insensitive, exact match)
    """
    # Set default and max page size
    if page_size is None:
        page_size = settings.default_page_size
    page_size = min(page_size, settings.max_page_size)
    
    # Build query with filters
    query = db.query(WovenInfo)
    
    if color_name:
        # Filter by color name (case-insensitive, checking if any element in array matches)
        query = query.filter(
            WovenInfo.color_name.any(color_name.lower())
        )
    
    if category:
        query = query.filter(WovenInfo.category.ilike(category))
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get paginated results
    items = query.order_by(WovenInfo.id).offset(offset).limit(page_size).all()
    
    return WovenListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{woven_id}", response_model=WovenDetail)
def get_woven(
    woven_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific woven including similar wovens with filenames.
    
    - **woven_id**: ID of the woven to retrieve
    """
    # Get the main woven
    woven = db.query(WovenInfo).filter(WovenInfo.id == woven_id).first()
    
    if not woven:
        raise HTTPException(status_code=404, detail=f"Woven with ID {woven_id} not found")
    
    # Process similarity data to include filenames
    similar_wovens = []
    if woven.similarity:
        # Extract IDs from similarity array
        similar_ids = [item['id'] for item in woven.similarity]
        
        # Fetch all similar wovens in one query
        similar_woven_objs = db.query(WovenInfo).filter(WovenInfo.id.in_(similar_ids)).all()
        
        # Create a mapping of id -> filename
        id_to_filename = {w.id: w.filename for w in similar_woven_objs}
        
        # Build response with filenames
        for item in woven.similarity:
            similar_wovens.append(SimilarWovenItem(
                id=item['id'],
                score_percent=item['score_percent'],
                filename=id_to_filename.get(item['id'], "Unknown")
            ))
    
    return WovenDetail(
        id=woven.id,
        filename=woven.filename,
        category=woven.category,
        color_name=woven.color_name,
        color_hex=woven.color_hex,
        similarity=similar_wovens
    )
