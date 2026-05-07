"""
Esquemas Pydantic para Foto na Plataforma FazendaOk.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RespostaFoto(BaseModel):
    """Resposta contendo os detalhes de uma foto."""
    id: str
    property_id: str
    url_original: Optional[str] = None
    url_miniatura: Optional[str] = None
    status_validacao: str  # pending, valid, invalid
    coordenadas_gps: Optional[Dict[str, Any]] = None
    data_captura: Optional[str] = None
    erro_validacao: Optional[str] = None
    data_criacao: str
    
    model_config = ConfigDict(from_attributes=True)


class RespostaUploadFoto(BaseModel):
    """Resposta após o upload de um lote de fotos."""
    ids_fotos: List[str]
    ids_tarefas: List[str]
    quantidade_aceita: int
    quantidade_rejeitada: int
    mensagens: Optional[List[str]] = None
