"""
Serviço de cache utilizando Redis para a Plataforma FazendaOk.
Responsável por armazenar e recuperar diagnósticos processados.
Requisitos atendidos: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
"""

import json
import logging
from typing import Optional, Any, Dict
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

class ServicoCache:
    """Serviço para gerenciamento de cache no Redis."""
    
    def __init__(self):
        """Inicializa a conexão com o Redis usando a URL das configurações."""
        self.redis_url = settings.redis_url
        self._redis: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        """Retorna uma instância de conexão com o Redis (Lazy initialization)."""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def obter_diagnostico(self, numero_car: str) -> Optional[Dict[str, Any]]:
        """
        Recupera um diagnóstico do cache pelo número do CAR.
        
        Args:
            numero_car: O número do CAR da propriedade.
            
        Returns:
            O diagnóstico em formato de dicionário ou None se não encontrado/expirado.
        """
        try:
            r = await self.get_redis()
            chave = f"diagnostic:{numero_car}"
            dados = await r.get(chave)
            
            if dados:
                logger.info(f"Cache HIT para o CAR: {numero_car}")
                return json.loads(dados)
            
            logger.info(f"Cache MISS para o CAR: {numero_car}")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler do cache Redis: {str(e)}")
            return None

    async def salvar_diagnostico(self, numero_car: str, dados: Dict[str, Any], ttl: int = 21600) -> bool:
        """
        Salva um diagnóstico no cache com um tempo de vida (TTL).
        
        Args:
            numero_car: O número do CAR da propriedade.
            dados: Dicionário com os dados do diagnóstico.
            ttl: Tempo de expiração em segundos (padrão 6 horas = 21600s).
            
        Returns:
            True se salvo com sucesso, False caso contrário.
        """
        try:
            r = await self.get_redis()
            chave = f"diagnostic:{numero_car}"
            await r.set(chave, json.dumps(dados), ex=ttl)
            logger.info(f"Diagnóstico salvo no cache para o CAR: {numero_car} com TTL de {ttl}s")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar no cache Redis: {str(e)}")
            return False

    async def limpar_cache_propriedade(self, numero_car: str) -> bool:
        """Remove o diagnóstico cacheado de uma propriedade específica."""
        try:
            r = await self.get_redis()
            await r.delete(f"diagnostic:{numero_car}")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache no Redis: {str(e)}")
            return False
