"""
API Versão 1 para a Plataforma FazendaOk.
"""

from fastapi import APIRouter
from app.api.v1 import properties, diagnostics, photos, dashboard

router_v1 = APIRouter()
router_v1.include_router(properties.router, prefix="/propriedades", tags=["propriedades"])
router_v1.include_router(diagnostics.router, prefix="/diagnosticos", tags=["diagnosticos"])
router_v1.include_router(photos.router, prefix="/fotos", tags=["fotos"])
router_v1.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
