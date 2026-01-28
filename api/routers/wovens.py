"""
API router for woven, variant, and stock endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func, exists
import math

from api.database import get_db
from api.models import WovenInfo, VariantInfo, StockInfo
from api.schemas import (
    WovenListItem, WovenListResponse, VariantSummary,
    VariantListItem, VariantListResponse, VariantDetail,
    SimilarVariantItem, WovenSummary, YarnItem, StockItem,
    StockListItem, StockListResponse, VariantInStock
)
from api.config import get_settings

router = APIRouter(tags=["Wovens"])
settings = get_settings()


# ==================== WOVEN ENDPOINTS ====================

@router.get("/wovens", response_model=WovenListResponse)
def list_wovens(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(None, ge=1, description="Number of items per page"),
    reference: Optional[str] = Query(None, description="Filter by reference code (partial match, case-insensitive)"),
    draw: Optional[str] = Query(None, description="Filter by draw pattern (partial match, case-insensitive)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of wovens with their variants.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **reference**: Filter by reference code (partial match, case-insensitive)
    - **draw**: Filter by draw pattern (partial match, case-insensitive)
    """
    # Set default and max page size
    if page_size is None:
        page_size = settings.default_page_size
    page_size = min(page_size, settings.max_page_size)
    
    # Build query with filters
    query = db.query(WovenInfo)
    
    if reference:
        query = query.filter(WovenInfo.reference.ilike(f"%{reference}%"))
    
    if draw:
        query = query.filter(WovenInfo.draw.ilike(f"%{draw}%"))
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get paginated results with variants
    wovens = query.options(joinedload(WovenInfo.variant_infos)).order_by(WovenInfo.id).offset(offset).limit(page_size).all()
    
    # Build response items
    items = []
    for woven in wovens:
        variants = [
            VariantSummary(
                variant_id=v.id,
                variant_ref=v.variant_ref,
                thumbnail=v.thumbnail
            )
            for v in sorted(woven.variant_infos, key=lambda x: x.variant_ref)
        ]
        
        items.append(WovenListItem(
            id=woven.id,
            reference=woven.reference,
            draw=woven.draw,
            finishing=woven.finishing,
            variant_count=len(variants),
            variants=variants
        ))
    
    return WovenListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/wovens/{woven_id}", response_model=WovenListItem)
def get_woven(
    woven_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific woven by ID with its variants.
    
    - **woven_id**: ID of the woven to retrieve
    """
    woven = db.query(WovenInfo).options(
        joinedload(WovenInfo.variant_infos)
    ).filter(WovenInfo.id == woven_id).first()
    
    if not woven:
        raise HTTPException(status_code=404, detail=f"Woven with ID {woven_id} not found")
    
    variants = [
        VariantSummary(
            variant_id=v.id,
            variant_ref=v.variant_ref,
            thumbnail=v.thumbnail
        )
        for v in sorted(woven.variant_infos, key=lambda x: x.variant_ref)
    ]
    
    return WovenListItem(
        id=woven.id,
        reference=woven.reference,
        draw=woven.draw,
        finishing=woven.finishing,
        variant_count=len(variants),
        variants=variants
    )


# ==================== VARIANT ENDPOINTS ====================

@router.get("/variants", response_model=VariantListResponse)
def list_variants(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(None, ge=1, description="Number of items per page"),
    color_name: Optional[List[str]] = Query(None, description="Filter by color name(s) - must have ALL specified colors"),
    category: Optional[str] = Query(None, description="Filter by category (case-insensitive, partial match)"),
    reference: Optional[str] = Query(None, description="Filter by woven reference (partial match)"),
    draw: Optional[str] = Query(None, description="Filter by draw pattern (partial match)"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of variants with optional filters.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **color_name**: Filter by color name(s) (case-insensitive, must have ALL specified colors)
    - **category**: Filter by category (case-insensitive, partial match)
    - **reference**: Filter by woven reference (partial match)
    - **draw**: Filter by draw pattern (partial match)
    - **in_stock**: Filter by stock availability (true = has stock, false = no stock)
    """
    # Set default and max page size
    if page_size is None:
        page_size = settings.default_page_size
    page_size = min(page_size, settings.max_page_size)
    
    # Build query with filters
    query = db.query(VariantInfo).join(WovenInfo)
    
    if color_name:
        # Filter by color names (AND condition - must have ALL specified colors)
        for color in color_name:
            query = query.filter(VariantInfo.color_name.any(color.lower()))
    
    if category:
        query = query.filter(VariantInfo.category.ilike(f"%{category}%"))
    
    if reference:
        query = query.filter(WovenInfo.reference.ilike(f"%{reference}%"))
    
    if draw:
        query = query.filter(WovenInfo.draw.ilike(f"%{draw}%"))
    
    if in_stock is not None:
        stock_exists = exists().where(StockInfo.variant_id == VariantInfo.id)
        if in_stock:
            query = query.filter(stock_exists)
        else:
            query = query.filter(~stock_exists)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get paginated results
    variants = query.options(joinedload(VariantInfo.woven)).order_by(VariantInfo.id).offset(offset).limit(page_size).all()
    
    # Build response items
    items = [
        VariantListItem(
            id=v.id,
            variant_ref=v.variant_ref,
            reference=v.woven.reference if v.woven else None,
            draw=v.woven.draw if v.woven else None,
            thumbnail=v.thumbnail,
            color_hex=v.color_hex or []
        )
        for v in variants
    ]
    
    return VariantListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/variants/{variant_id}", response_model=VariantDetail)
def get_variant(
    variant_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific variant including similar variants, yarns, and stock.
    
    - **variant_id**: ID of the variant to retrieve
    """
    # Get the variant with its relationships
    variant = db.query(VariantInfo).options(
        joinedload(VariantInfo.woven).joinedload(WovenInfo.variant_infos),
        joinedload(VariantInfo.stock_entries)
    ).filter(VariantInfo.id == variant_id).first()
    
    if not variant:
        raise HTTPException(status_code=404, detail=f"Variant with ID {variant_id} not found")
    
    # Process similarity data to include variant details
    similar_variants = []
    if variant.similarity:
        # Extract IDs from similarity array
        similar_ids = [item['id'] for item in variant.similarity]
        
        # Fetch all similar variants in one query
        similar_variant_objs = db.query(VariantInfo).options(
            joinedload(VariantInfo.woven)
        ).filter(VariantInfo.id.in_(similar_ids)).all()
        
        # Create a mapping of id -> variant
        id_to_variant = {v.id: v for v in similar_variant_objs}
        
        # Build response with variant details
        for item in variant.similarity:
            similar_v = id_to_variant.get(item['id'])
            similar_variants.append(SimilarVariantItem(
                id=item['id'],
                score_percent=item.get('score_percent', 0),
                variant_ref=similar_v.variant_ref if similar_v else "Unknown",
                reference=similar_v.woven.reference if similar_v and similar_v.woven else None,
                thumbnail=similar_v.thumbnail if similar_v else None
            ))
    
    # Build woven summary
    woven_summary = WovenSummary(
        id=variant.woven.id,
        reference=variant.woven.reference,
        draw=variant.woven.draw,
        composition=variant.woven.composition,
        date=variant.woven.date,
        finishing=variant.woven.finishing
    ) if variant.woven else None
    
    # Get other variants from the same woven (excluding current variant)
    other_variants = []
    if variant.woven and variant.woven.variant_infos:
        other_variants = [
            VariantSummary(
                variant_id=v.id,
                variant_ref=v.variant_ref,
                thumbnail=v.thumbnail
            )
            for v in sorted(variant.woven.variant_infos, key=lambda x: x.variant_ref)
            if v.id != variant_id  # Exclude the current variant
        ]
    
    # Filter yarns by variant_ref
    yarns = []
    if variant.woven and variant.woven.yarns:
        for yarn in variant.woven.yarns:
            # Check if this yarn is for this variant
            yarn_variant_ref = yarn.get('variant_ref')
            if yarn_variant_ref is None or yarn_variant_ref == variant.variant_ref:
                yarns.append(YarnItem(
                    name=yarn.get('name'),
                    ne=yarn.get('ne'),
                    composition=yarn.get('composition'),
                    colors=yarn.get('colors')
                ))
    
    # Build stock items
    stock_items = [
        StockItem(
            id=s.id,
            description=s.description,
            quantity=float(s.quantity) if s.quantity else None,
            perfect_match=s.perfect_match or False
        )
        for s in variant.stock_entries
    ]
    
    return VariantDetail(
        id=variant.id,
        variant_ref=variant.variant_ref,
        filename=variant.filename,
        thumbnail=variant.thumbnail,
        category=variant.category,
        color_name=variant.color_name or [],
        color_hex=variant.color_hex or [],
        similarity=similar_variants,
        woven=woven_summary,
        other_variants=other_variants,
        yarns=yarns,
        stock=stock_items
    )


# ==================== STOCK ENDPOINTS ====================

@router.get("/stock", response_model=StockListResponse)
def list_stock(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(None, ge=1, description="Number of items per page"),
    variant_id: Optional[int] = Query(None, description="Filter by specific variant ID"),
    perfect_match: Optional[bool] = Query(None, description="Filter by perfect match status"),
    min_quantity: Optional[float] = Query(None, description="Minimum stock quantity"),
    description: Optional[str] = Query(None, description="Filter by description (partial match, case-insensitive)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of stock records with optional filters.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **variant_id**: Filter by specific variant ID
    - **perfect_match**: Filter by perfect match status
    - **min_quantity**: Minimum stock quantity
    - **description**: Filter by description (partial match, case-insensitive)
    """
    # Set default and max page size
    if page_size is None:
        page_size = settings.default_page_size
    page_size = min(page_size, settings.max_page_size)
    
    # Build query with filters
    query = db.query(StockInfo)
    
    if variant_id is not None:
        query = query.filter(StockInfo.variant_id == variant_id)
    
    if perfect_match is not None:
        query = query.filter(StockInfo.perfect_match == perfect_match)
    
    if min_quantity is not None:
        query = query.filter(StockInfo.quantity >= min_quantity)
    
    if description:
        query = query.filter(StockInfo.description.ilike(f"%{description}%"))
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get paginated results with variant info
    stocks = query.options(
        joinedload(StockInfo.variant).joinedload(VariantInfo.woven)
    ).order_by(StockInfo.id).offset(offset).limit(page_size).all()
    
    # Build response items
    items = []
    for stock in stocks:
        variant_info = VariantInStock(
            id=stock.variant.id,
            variant_ref=stock.variant.variant_ref,
            reference=stock.variant.woven.reference if stock.variant.woven else None,
            category=stock.variant.category,
            thumbnail=stock.variant.thumbnail
        ) if stock.variant else None
        
        items.append(StockListItem(
            id=stock.id,
            variant_id=stock.variant_id,
            description=stock.description,
            quantity=float(stock.quantity) if stock.quantity else None,
            perfect_match=stock.perfect_match or False,
            variant=variant_info
        ))
    
    return StockListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
