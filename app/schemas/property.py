"""
Esquemas Pydantic para Propriedade na Plataforma FazendaOk.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

from app.utils.validators import validar_numero_car, validar_coordenadas


class PedidoBuscaPorCAR(BaseModel):
    """Pedido para buscar uma propriedade pelo número do CAR."""
    
    numero_car: str = Field(..., description="Número do CAR no formato UF-1234567-ABCD1234")

    @field_validator("numero_car")
    def validar_formato_car(cls, v):
        """
        Valida o formato do número do CAR.
        
        Utiliza a função pura validar_numero_car() para garantir consistência
        com os testes de propriedade.
        """
        if not validar_numero_car(v):
            raise ValueError("Formato de CAR inválido. Esperado: UF-1234567-IDENTIFICADOR")
        return v


class PedidoBuscaPorCoordenadas(BaseModel):
    """Pedido para buscar uma propriedade por coordenadas geográficas."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PedidoBuscaPorEndereco(BaseModel):
    """Pedido para buscar uma propriedade por endereço."""
    
    endereco: str = Field(..., min_length=5)


class RespostaPropriedade(BaseModel):
    """Resposta contendo os dados da propriedade."""
    
    id: str
    numero_car: str
    area_total_ha: float
    area_app_ha: Optional[float] = None
    area_reserva_legal_ha: Optional[float] = None
    status_car: str
    poligono_geojson: dict
    dados_adicionais: Optional[dict] = None
    data_criacao: str
    
    model_config = ConfigDict(from_attributes=True)
