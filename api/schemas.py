"""
Pydantic schemas for request validation and response serialization.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


# Woven Info Schemas
class SimilarityItem(BaseModel):
    """Schema for similarity item in woven info."""
    id: int
    score_percent: float


class WovenBase(BaseModel):
    """Base schema for woven info."""
    id: int
    filename: str
    category: Optional[str] = None
    color_name: List[str]
    color_hex: List[str]


class WovenListItem(BaseModel):
    """Schema for woven info in list responses (minimal fields)."""
    id: int
    color_name: List[str]
    category: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SimilarWovenItem(BaseModel):
    """Schema for similar woven with filename."""
    id: int
    score_percent: float
    filename: str


class WovenDetail(BaseModel):
    """Schema for detailed woven info with similar items."""
    id: int
    filename: str
    category: Optional[str] = None
    color_name: List[str]
    color_hex: List[str]
    similarity: List[SimilarWovenItem]
    
    model_config = ConfigDict(from_attributes=True)


class WovenListResponse(BaseModel):
    """Schema for paginated woven list response."""
    items: List[WovenListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# Pantone Color Schemas
class PantoneColorBase(BaseModel):
    """Base schema for Pantone color."""
    name: str
    hex: str


class PantoneColorListItem(BaseModel):
    """Schema for Pantone color in list responses."""
    name: str
    hex: str
    
    model_config = ConfigDict(from_attributes=True)


class NearestWovenItem(BaseModel):
    """Schema for nearest woven with filename."""
    id: int
    filename: str


class PantoneColorDetail(BaseModel):
    """Schema for detailed Pantone color with nearest wovens."""
    name: str
    hex: str
    nearest: List[NearestWovenItem]
    
    model_config = ConfigDict(from_attributes=True)


class PantoneColorListResponse(BaseModel):
    """Schema for Pantone color list response."""
    items: List[PantoneColorListItem]
    total: int
