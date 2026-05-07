"""
Photo (Foto) database model.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base


class ValidationStatus(str, Enum):
    """Photo validation status."""
    VALIDATED = "validated"
    OUTSIDE_BOUNDARY = "outside_boundary"
    NO_GPS_SESSION_VALID = "no_gps_session_valid"
    PENDING = "pending"
    FAILED = "failed"


class Foto(Base):
    """Photo model representing an uploaded geotagged photo."""
    
    __tablename__ = "fotos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("propriedades.id"), nullable=False)
    diagnostic_id = Column(UUID(as_uuid=True), ForeignKey("diagnosticos.id"))
    s3_url = Column(String)
    thumbnail_s3_url = Column(String)
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    gps_point = Column(Geometry(geometry_type="POINT", srid=4326))
    validation_status = Column(String, nullable=False, default=ValidationStatus.PENDING.value)
    capture_date = Column(DateTime)
    exif_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
