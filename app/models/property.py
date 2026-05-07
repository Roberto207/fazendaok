"""
Modelo de banco de dados para Propriedade.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base


class Propriedade(Base):
    """Modelo de propriedade que representa uma propriedade rural do CAR."""
    
    __tablename__ = "propriedades"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_number = Column(String, unique=True, nullable=False, index=True)
    polygon = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    total_area_ha = Column(Float, nullable=False)
    app_area_ha = Column(Float)
    legal_reserve_area_ha = Column(Float)
    car_status = Column(String, nullable=False)  # active, cancelled, suspended
    dados_adicionais = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
