"""
PRODES Cerrado database model.
"""

import uuid
from sqlalchemy import Column, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base


class ProdesCerrado(Base):
    """PRODES Cerrado deforestation data model."""
    
    __tablename__ = "prodes_cerrado"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    area_ha = Column(Float, nullable=False)
    source_metadata = Column(JSON)
