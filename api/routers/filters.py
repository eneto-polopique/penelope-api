"""
API router for filter metadata endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from api.database import get_db
from api.models import WovenInfo
from api.filter_values import AVAILABLE_COLORS, AVAILABLE_CATEGORIES

router = APIRouter(prefix="/filters", tags=["Filters"])


@router.get("/colors", response_model=List[str])
def get_available_colors():
    """
    Get list of available color names for filtering.
    
    Returns a static list of supported color names that can be used
    in the `color_name` filter parameter.
    """
    return sorted(AVAILABLE_COLORS)


@router.get("/categories", response_model=List[str])
def get_available_categories():
    """
    Get list of available categories for filtering.
    
    Returns a static list of fabric categories that can be used
    in the `category` filter parameter.
    """
    return sorted(AVAILABLE_CATEGORIES)


@router.get("/references", response_model=List[str])
def get_available_references(db: Session = Depends(get_db)):
    """
    Get list of all unique reference codes from the database.
    
    Returns all distinct reference codes that can be used
    in the `reference` filter parameter.
    """
    references = db.query(distinct(WovenInfo.reference)).filter(
        WovenInfo.reference.isnot(None)
    ).order_by(WovenInfo.reference).all()
    
    return [ref[0] for ref in references]


@router.get("/draws", response_model=List[str])
def get_available_draws(db: Session = Depends(get_db)):
    """
    Get list of all unique draw patterns from the database.
    
    Returns all distinct draw patterns that can be used
    in the `draw` filter parameter.
    """
    draws = db.query(distinct(WovenInfo.draw)).filter(
        WovenInfo.draw.isnot(None)
    ).order_by(WovenInfo.draw).all()
    
    return [draw[0] for draw in draws]
