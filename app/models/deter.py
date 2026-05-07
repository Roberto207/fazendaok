"""
DETER Cerrado database model.
"""

import uuid
from datetime import date
from sqlalchemy import Column, Date, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base


class DeterCerrado(Base):
    """DETER Cerrado deforestation alert data model."""
    
    __tablename__ = "deter_cerrado"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    alert_date = Column(Date, nullable=False, index=True)
    area_ha = Column(Float, nullable=False)
    source_metadata = Column(JSON)
