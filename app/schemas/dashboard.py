"""
Esquemas Pydantic para Dashboard na Plataforma FazendaOk.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class EstatisticasPropriedade(BaseModel):
    """Estatísticas gerais de propriedades cadastradas."""
    total_propriedades: int
    total_area_ha: float
    total_alertas_ativos: int


class EstatisticasFoto(BaseModel):
    """Estatísticas gerais de fotos processadas."""
    total_fotos: int
    fotos_validadas: int
    fotos_invalidas: int
    fotos_pendentes: int


class ResumoDashboard(BaseModel):
    """Resumo geral para o dashboard principal."""
    propriedades: EstatisticasPropriedade
    fotos: EstatisticasFoto
    alertas_recentes: List[Dict[str, Any]]
