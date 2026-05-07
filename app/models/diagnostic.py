"""
Diagnostic (Diagnostico) database model.
"""

import uuid
from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, String, Float, Integer, Date, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class RiskLevel(str, Enum):
    """Risk level classification for environmental compliance."""
    APTO = "APTO"
    RISCO_MEDIO = "RISCO_MEDIO"
    RISCO_ALTO = "RISCO_ALTO"
    BLOQUEIO_PROVAVEL = "BLOQUEIO_PROVAVEL"
    BLOQUEIO_DIRETO = "BLOQUEIO_DIRETO"


class Diagnostico(Base):
    """Diagnostic model representing an environmental risk assessment."""
    
    __tablename__ = "diagnosticos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("propriedades.id"), nullable=False)
    risk_level = Column(String, nullable=False)  # Store as string, validate with RiskLevel enum
    prodes_overlap_area_ha = Column(Float, default=0.0)
    deter_alert_count = Column(Integer, default=0)
    latest_deter_date = Column(Date)
    prodes_intersections = Column(JSON)  # GeoJSON
    deter_intersections = Column(JSON)   # GeoJSON
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
