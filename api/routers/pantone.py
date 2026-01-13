"""
API router for Pantone color-related endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import PantoneColor, WovenInfo
from api.schemas import PantoneColorListItem, PantoneColorListResponse, PantoneColorDetail, NearestWovenItem

router = APIRouter(prefix="/pantone-colors", tags=["Pantone Colors"])


@router.get("", response_model=PantoneColorListResponse)
def list_pantone_colors(
    db: Session = Depends(get_db)
):
    """
    Get list of all Pantone colors with their hex values and names.
    """
    colors = db.query(PantoneColor).order_by(PantoneColor.name).all()
    
    return PantoneColorListResponse(
        items=colors,
        total=len(colors)
    )


@router.get("/detail", response_model=PantoneColorDetail)
def get_pantone_color(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific Pantone color including nearest wovens with filenames.
    
    - **name**: Name of the Pantone color (e.g., "PANTONE Yellow C")
    """
    color_name = name
    # Get the Pantone color
    pantone_color = db.query(PantoneColor).filter(PantoneColor.name == color_name).first()
    
    if not pantone_color:
        raise HTTPException(status_code=404, detail=f"Pantone color '{color_name}' not found")
    
    # Process nearest data to include filenames
    nearest_wovens = []
    if pantone_color.nearest:
        # Fetch all nearest wovens in one query
        nearest_woven_objs = db.query(WovenInfo).filter(WovenInfo.id.in_(pantone_color.nearest)).all()
        
        # Create a mapping of id -> filename
        id_to_filename = {w.id: w.filename for w in nearest_woven_objs}
        
        # Build response with filenames (maintain order from nearest array)
        for woven_id in pantone_color.nearest:
            nearest_wovens.append(NearestWovenItem(
                id=woven_id,
                filename=id_to_filename.get(woven_id, "Unknown")
            ))
    
    return PantoneColorDetail(
        name=pantone_color.name,
        hex=pantone_color.hex,
        nearest=nearest_wovens
    )
