"""
Serviço de integração com o SICAR (Sistema Nacional de Cadastro Ambiental Rural).
Utiliza a API do Infosimples para buscar dados das propriedades.
"""

import logging
import httpx
from typing import Optional, List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class ServicoSICAR:
    """Serviço para interagir com os dados do SICAR via Infosimples."""
    
    def __init__(self):
        self.api_token = settings.infosimples_token
        self.base_url = "https://api.infosimples.com/api/v2/consultas/sicar/car"
        
    async def buscar_propriedade_por_car(self, numero_car: str) -> Optional[Dict[str, Any]]:
        """
        Busca os detalhes de uma propriedade pelo número do CAR.
        
        Args:
            numero_car: Número do CAR no formato UF-1234567-IDENTIFICADOR
            
        Returns:
            Dados da propriedade ou None se não encontrada
        """
        if not self.api_token:
            logger.warning("Token do Infosimples não configurado. Usando mock para desenvolvimento.")
            return self._mock_propriedade_por_car(numero_car)
            
        params = {
            "token": self.api_token,
            "codigo_imovel": numero_car,
            "json": "true"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                dados = response.json()
                
                if dados.get("code") == 200 and dados.get("data"):
                    # Extrai os dados relevantes da resposta do Infosimples
                    return self._processar_resposta_sicar(dados["data"][0])
                
                logger.error(f"Erro na consulta SICAR: {dados.get('code_message')}")
                return None
                
            except Exception as e:
                logger.error(f"Erro ao conectar com a API do Infosimples: {str(e)}")
                return None

    async def buscar_propriedades_por_coordenadas(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """
        Busca propriedades próximas a uma coordenada geográfica.
        Nota: O SICAR não tem uma busca direta por coordenada via API simples, 
        geralmente é necessário buscar pelo mapa ou via geo-serviços.
        Esta é uma implementação simplificada ou mockada.
        """
        logger.info(f"Buscando propriedades próximas a ({lat}, {lon})")
        # TODO: Implementar busca real se disponível na API
        return [self._mock_propriedade_por_car(f"GO-5208707-MOCK{int(lat*100)}{int(lon*100)}")]

    def _processar_resposta_sicar(self, dados_raw: Dict[str, Any]) -> Dict[str, Any]:
        """Processa e normaliza os dados vindos da API externa."""
        # Esta lógica dependeria do formato exato da resposta do Infosimples
        return {
            "numero_car": dados_raw.get("codigo_imovel"),
            "area_total_ha": dados_raw.get("area_imovel", 0.0),
            "status_car": dados_raw.get("situacao_imovel", "ATIVO").lower(),
            "geometria_geojson": dados_raw.get("geojson"),
            "dados_adicionais": dados_raw
        }

    def _mock_propriedade_por_car(self, numero_car: str) -> Dict[str, Any]:
        """Retorna dados fictícios para fins de teste/desenvolvimento."""
        return {
            "numero_car": numero_car,
            "area_total_ha": 150.5,
            "area_app_ha": 25.0,
            "area_reserva_legal_ha": 30.0,
            "status_car": "ativo",
            "geometria_geojson": {
                "type": "Polygon",
                "coordinates": [[
                    [-47.9, -15.8],
                    [-47.8, -15.8],
                    [-47.8, -15.7],
                    [-47.9, -15.7],
                    [-47.9, -15.8]
                ]]
            },
            "dados_adicionais": {"mock": True}
        }
