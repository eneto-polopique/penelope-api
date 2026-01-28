"""
SQLAlchemy database models for the Penelope dataset.
"""

from sqlalchemy import Column, Integer, String, ARRAY, JSON, TIMESTAMP, Date, Numeric, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WovenInfo(Base):
    """Model for woven fabric base information (production/technical data)."""
    
    __tablename__ = "woven_info"
    
    id = Column(Integer, primary_key=True, index=True)
    draw = Column(String(100), index=True)
    finishing = Column(String(255))
    reference = Column(String(100), index=True)
    date = Column(Date)
    composition = Column(String(255))
    variants = Column(ARRAY(String), nullable=False, default=list)
    yarns = Column(JSON, nullable=False, default=list)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationship to variants
    variant_infos = relationship("VariantInfo", back_populates="woven", cascade="all, delete-orphan")


class VariantInfo(Base):
    """Model for variant information (visual/image analysis per variant)."""
    
    __tablename__ = "variant_info"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    woven_id = Column(Integer, ForeignKey("woven_info.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_ref = Column(String(50), nullable=False)
    filename = Column(String(255))
    thumbnail = Column(String(255))
    category = Column(String(100), index=True)
    color_name = Column(ARRAY(String), nullable=False, default=list)
    color_hex = Column(ARRAY(String), nullable=False, default=list)
    similarity = Column(JSON, nullable=False, default=list)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationship to woven
    woven = relationship("WovenInfo", back_populates="variant_infos")
    
    # Relationship to stock
    stock_entries = relationship("StockInfo", back_populates="variant", cascade="all, delete-orphan")


class PantoneColor(Base):
    """Model for Pantone colors."""
    
    __tablename__ = "pantone_colors"
    
    name = Column(String(100), primary_key=True, index=True)
    hex = Column(String(7), nullable=False)
    nearests = Column(ARRAY(Integer), nullable=False, default=list)


class StockInfo(Base):
    """Model for stock information per variant."""
    
    __tablename__ = "stock_info"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    variant_id = Column(Integer, ForeignKey("variant_info.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(255))
    quantity = Column(Numeric(10, 2))
    perfect_match = Column(Boolean, default=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationship to variant
    variant = relationship("VariantInfo", back_populates="stock_entries")
