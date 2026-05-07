"""
Serviço de Diagnóstico para a Plataforma FazendaOk.
Responsável por orquestrar a análise espacial e classificar o risco ambiental.
Requisitos atendidos: 4.8, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
from app.models.diagnostic import RiskLevel
from app.services.spatial_service import ServicoEspacial
from app.services.cache_service import ServicoCache

logger = logging.getLogger(__name__)

class ServicoDiagnostico:
    """Serviço que gerencia a lógica de diagnóstico e classificação de risco."""
    
    def __init__(self):
        self.servico_espacial = ServicoEspacial()
        self.servico_cache = ServicoCache()

    def classificar_risco(
        self, 
        status_car: str, 
        area_sobreposicao_prodes: float, 
        alertas_deter: List[Dict[str, Any]]
    ) -> RiskLevel:
        """
        Classifica o nível de risco ambiental com base nos critérios definidos.
        
        Args:
            status_car: Status do CAR (active, cancelled, suspended, etc)
            area_sobreposicao_prodes: Área total de sobreposição PRODES em hectares
            alertas_deter: Lista de alertas DETER encontrados. Cada alerta deve ter 'data_alerta'.
            
        Returns:
            RiskLevel: O nível de risco classificado
        """
        # Normalização do status do CAR
        status_normalizado = status_car.lower() if status_car else ""
        
        # 1. BLOQUEIO_DIRETO: Status do CAR não é ativo (Requisito 5.1)
        if status_normalizado not in ["ativo", "active"]:
            logger.info(f"Risco classificado como BLOQUEIO_DIRETO devido ao status do CAR: {status_car}")
            return RiskLevel.BLOQUEIO_DIRETO

        hoje = date.today()
        seis_meses_atras = hoje - timedelta(days=180)
        doze_meses_atras = hoje - timedelta(days=365)
        
        # Verifica datas dos alertas DETER
        alertas_recentes = [a for a in alertas_deter if a.get("data_alerta", date.min) >= seis_meses_atras]
        alertas_antigos = [a for a in alertas_deter if a.get("data_alerta", date.min) < doze_meses_atras]
        alertas_intermediarios = [a for a in alertas_deter if doze_meses_atras <= a.get("data_alerta", date.min) < seis_meses_atras]

        # 2. BLOQUEIO_PROVAVEL: PRODES > 10ha ou DETER nos últimos 6 meses (Requisito 5.5)
        if area_sobreposicao_prodes > 10.0 or len(alertas_recentes) > 0:
            return RiskLevel.BLOQUEIO_PROVAVEL

        # 3. RISCO_ALTO: PRODES entre 2 e 10ha ou múltiplos alertas DETER (Requisito 5.4)
        # Também incluímos aqui alertas únicos no período intermediário (6-12 meses)
        if (2.0 <= area_sobreposicao_prodes <= 10.0) or len(alertas_deter) > 1 or len(alertas_intermediarios) > 0:
            return RiskLevel.RISCO_ALTO

        # 4. RISCO_MEDIO: PRODES < 2ha ou alerta DETER antigo (> 12 meses) (Requisito 5.3)
        if (0.0 < area_sobreposicao_prodes < 2.0) or len(alertas_antigos) > 0:
            return RiskLevel.RISCO_MEDIO

        # 5. APTO: Ativo + Sem PRODES + Sem DETER (Requisito 5.2)
        return RiskLevel.APTO

    async def gerar_explicacao_base(self, nivel_risco: RiskLevel, dados: Dict[str, Any]) -> str:
        """
        Gera uma explicação textual básica baseada no nível de risco (fallback).
        
        Args:
            nivel_risco: O nível de risco calculado
            dados: Dados contextuais da análise
            
        Returns:
            str: Explicação em português
        """
        explicacoes = {
            RiskLevel.APTO: (
                "Sua propriedade está em conformidade socioambiental. "
                "Não foram detectados desmatamentos recentes ou alertas ativos nas bases PRODES e DETER."
            ),
            RiskLevel.RISCO_MEDIO: (
                "Identificamos um risco moderado. Há pequenas áreas de sobreposição com o PRODES (< 2ha) "
                "ou alertas DETER antigos. Recomenda-se verificar a regularização ambiental."
            ),
            RiskLevel.RISCO_ALTO: (
                "Risco elevado detectado. Foram encontradas sobreposições significativas com o PRODES "
                "ou múltiplos alertas de desmatamento DETER. Isso pode dificultar a obtenção de crédito rural."
            ),
            RiskLevel.BLOQUEIO_PROVAVEL: (
                "Alta probabilidade de bloqueio de crédito. Detectamos desmatamento recente (últimos 6 meses) "
                "ou grandes áreas de sobreposição (> 10ha) com a base PRODES."
            ),
            RiskLevel.BLOQUEIO_DIRETO: (
                "Crédito bloqueado. O status do seu CAR não está ativo (cancelado ou suspenso), "
                "o que impede a concessão de crédito rural segundo as normas vigentes."
            )
        }
        return explicacoes.get(nivel_risco, "Diagnóstico concluído. Verifique os detalhes técnicos.")
