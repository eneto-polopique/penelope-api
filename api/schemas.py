"""
Pydantic schemas for request validation and response serialization.
"""

from typing import List, Optional, Union
from datetime import date as date_type
from pydantic import BaseModel, Field, ConfigDict


# ==================== WOVEN SCHEMAS ====================

class VariantSummary(BaseModel):
    """Summary of a variant for woven list view."""
    variant_id: int
    variant_ref: str
    thumbnail: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class WovenListItem(BaseModel):
    """Schema for woven info in list responses."""
    id: int
    reference: Optional[str] = None
    draw: Optional[str] = None
    finishing: Optional[str] = None
    variant_count: int
    variants: List[VariantSummary]
    
    model_config = ConfigDict(from_attributes=True)


class WovenListResponse(BaseModel):
    """Schema for paginated woven list response."""
    items: List[WovenListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== VARIANT SCHEMAS ====================

class VariantListItem(BaseModel):
    """Schema for variant in list responses."""
    id: int
    variant_ref: str
    reference: Optional[str] = None
    draw: Optional[str] = None
    thumbnail: Optional[str] = None
    color_hex: List[str]
    
    model_config = ConfigDict(from_attributes=True)


class VariantListResponse(BaseModel):
    """Schema for paginated variant list response."""
    items: List[VariantListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class SimilarVariantItem(BaseModel):
    """Schema for similar variant in detail view."""
    id: int
    score_percent: float
    variant_ref: str
    reference: Optional[str] = None
    thumbnail: Optional[str] = None


class WovenSummary(BaseModel):
    """Schema for parent woven info in variant detail."""
    id: int
    reference: Optional[str] = None
    draw: Optional[str] = None
    composition: Optional[str] = None
    date: Optional[date_type] = None
    finishing: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class YarnItem(BaseModel):
    """Schema for yarn information."""
    name: Optional[str] = None
    ne: Optional[str] = None
    composition: Optional[str] = None
    colors: Optional[str] = None


class StockItem(BaseModel):
    """Schema for stock information in variant detail."""
    id: int
    description: Optional[str] = None
    quantity: Optional[float] = None
    perfect_match: bool = False


class VariantDetail(BaseModel):
    """Schema for detailed variant information."""
    id: int
    variant_ref: str
    filename: Optional[str] = None
    thumbnail: Optional[str] = None
    category: Optional[str] = None
    color_name: List[str]
    color_hex: List[str]
    similarity: List[SimilarVariantItem]
    woven: WovenSummary
    other_variants: List[VariantSummary]
    yarns: List[YarnItem]
    stock: List[StockItem]
    
    model_config = ConfigDict(from_attributes=True)


# ==================== STOCK SCHEMAS ====================

class VariantInStock(BaseModel):
    """Schema for variant info within stock response."""
    id: int
    variant_ref: str
    reference: Optional[str] = None
    category: Optional[str] = None
    thumbnail: Optional[str] = None


class StockListItem(BaseModel):
    """Schema for stock in list responses."""
    id: int
    variant_id: int
    description: Optional[str] = None
    quantity: Optional[float] = None
    perfect_match: bool = False
    variant: VariantInStock
    
    model_config = ConfigDict(from_attributes=True)


class StockListResponse(BaseModel):
    """Schema for paginated stock list response."""
    items: List[StockListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== PANTONE COLOR SCHEMAS ====================

class PantoneColorListItem(BaseModel):
    """Schema for Pantone color in list responses."""
    name: str
    hex: str
    
    model_config = ConfigDict(from_attributes=True)


class PantoneColorListResponse(BaseModel):
    """Schema for Pantone color list response."""
    items: List[PantoneColorListItem]
    total: int


class NearestVariantItem(BaseModel):
    """Schema for nearest variant in Pantone color detail."""
    id: int
    variant_ref: str
    reference: Optional[str] = None
    draw: Optional[str] = None
    category: Optional[str] = None
    thumbnail: Optional[str] = None
    has_stock: bool = False


class PantoneColorDetail(BaseModel):
    """Schema for detailed Pantone color with nearest variants."""
    name: str
    hex: str
    nearest: List[NearestVariantItem]
    
    model_config = ConfigDict(from_attributes=True)
