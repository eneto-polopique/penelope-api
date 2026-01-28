"""
API router for Pantone color-related endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from api.database import get_db
from api.models import PantoneColor, VariantInfo, StockInfo
from api.schemas import (
    PantoneColorListItem, PantoneColorListResponse, 
    PantoneColorDetail, NearestVariantItem
)

router = APIRouter(prefix="/pantone-colors", tags=["Pantone Colors"])


@router.get("", response_model=PantoneColorListResponse)
def list_pantone_colors(
    db: Session = Depends(get_db)
):
    """
    Get list of all Pantone colors with their hex values and names.
    """
    colors = db.query(PantoneColor).order_by(PantoneColor.name).all()
    
    # Build response with name and hex only
    items = [
        PantoneColorListItem(
            name=color.name,
            hex=color.hex
        )
        for color in colors
    ]
    
    return PantoneColorListResponse(
        items=items,
        total=len(colors)
    )


@router.get("/detail", response_model=PantoneColorDetail)
def get_pantone_color(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific Pantone color including nearest variants.
    
    - **name**: Name of the Pantone color (e.g., "PANTONE Yellow C")
    """
    color_name = name
    # Get the Pantone color
    pantone_color = db.query(PantoneColor).filter(PantoneColor.name == color_name).first()
    
    if not pantone_color:
        raise HTTPException(status_code=404, detail=f"Pantone color '{color_name}' not found")
    
    # Process nearests data to include variant details
    nearest_variants = []
    if pantone_color.nearests:
        # Fetch all nearest variants with woven relationship in one query
        nearest_variant_objs = db.query(VariantInfo).options(
            joinedload(VariantInfo.woven)
        ).filter(
            VariantInfo.id.in_(pantone_color.nearests)
        ).all()
        
        # Create a mapping of id -> variant
        id_to_variant = {v.id: v for v in nearest_variant_objs}
        
        # Check which variants have stock
        variants_with_stock = set(
            db.query(StockInfo.variant_id)
            .filter(StockInfo.variant_id.in_(pantone_color.nearests))
            .distinct()
            .all()
        )
        variants_with_stock = {v[0] for v in variants_with_stock}
        
        # Build response with variant details (maintain order from nearests array)
        for variant_id in pantone_color.nearests:
            variant = id_to_variant.get(variant_id)
            if variant:
                nearest_variants.append(NearestVariantItem(
                    id=variant_id,
                    variant_ref=variant.variant_ref,
                    reference=variant.woven.reference if variant.woven else None,
                    draw=variant.woven.draw if variant.woven else None,
                    category=variant.category,
                    thumbnail=variant.thumbnail,
                    has_stock=variant_id in variants_with_stock
                ))
            else:
                # Variant not found, include with minimal info
                nearest_variants.append(NearestVariantItem(
                    id=variant_id,
                    variant_ref="Unknown",
                    reference=None,
                    draw=None,
                    category=None,
                    thumbnail=None,
                    has_stock=False
                ))
    
    return PantoneColorDetail(
        name=pantone_color.name,
        hex=pantone_color.hex,
        nearest=nearest_variants
    )
