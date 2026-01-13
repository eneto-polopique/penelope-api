"""
SQLAlchemy database models for the Penelope dataset.
"""

from sqlalchemy import Column, Integer, String, ARRAY, JSON, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WovenInfo(Base):
    """Model for woven fabric information."""
    
    __tablename__ = "woven_info"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    category = Column(String(100), index=True)
    color_name = Column(ARRAY(String), nullable=False, default=list, index=True)
    color_hex = Column(ARRAY(String), nullable=False, default=list)
    similarity = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class PantoneColor(Base):
    """Model for Pantone colors."""
    
    __tablename__ = "pantone_colors"
    
    name = Column(String(100), primary_key=True, index=True)
    hex = Column(String(7), nullable=False)
    nearest = Column(ARRAY(Integer), nullable=False, default=list)
