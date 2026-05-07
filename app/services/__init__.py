"""
Serviços da Plataforma FazendaOk.
"""

from app.services.photo_service import PhotoService
from app.services.sicar_service import ServicoSICAR
from app.services.spatial_service import ServicoEspacial

__all__ = ["PhotoService", "ServicoSICAR", "ServicoEspacial"]
