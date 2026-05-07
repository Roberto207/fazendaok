"""
Esquemas Pydantic para Diagnóstico na Plataforma FazendaOk.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class InterseccaoCamada(BaseModel):
    """Representa uma intersecção com uma camada ambiental (PRODES, DETER, etc)."""
    nome_camada: str
    area_interseccao_ha: float
    percentual_area_total: float
    detalhes: Optional[Dict[str, Any]] = None


class RespostaDiagnostico(BaseModel):
    """Resposta contendo o diagnóstico completo de uma propriedade."""
    id: str
    property_id: str
    risk_level: str  # baixo, medio, alto, critico
    explanation: str
    interseccoes: Optional[List[InterseccaoCamada]] = None
    created_at: datetime
    validado: Optional[bool] = True
    
    model_config = ConfigDict(from_attributes=True)


class RespostaStatusTarefa(BaseModel):
    """Resposta para consulta de status de tarefa assíncrona."""
    tarefa_id: str
    status: str  # PENDING, PROGRESS, SUCCESS, FAILURE
    resultado_id: Optional[str] = None
    progresso: Optional[float] = 0.0
    erro: Optional[str] = None
