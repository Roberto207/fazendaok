"""
Database models for FazendaOk Platform.
"""

from app.models.base import Base
from app.models.property import Propriedade
from app.models.diagnostic import Diagnostico
from app.models.photo import Foto, ValidationStatus
from app.models.prodes import ProdesCerrado
from app.models.deter import DeterCerrado

__all__ = [
    "Base",
    "Propriedade",
    "Diagnostico",
    "Foto",
    "ValidationStatus",
    "ProdesCerrado",
    "DeterCerrado",
]
