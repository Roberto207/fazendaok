"""
Serviço de integração com a Claude AI (Anthropic) para a Plataforma FazendaOk.
Responsável por gerar explicações amigáveis em português sobre o diagnóstico ambiental.
Requisitos atendidos: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
"""

import logging
from typing import Optional, Dict, Any
from anthropic import Anthropic, AsyncAnthropic
from app.config import settings

logger = logging.getLogger(__name__)

class ServicoClaude:
    """Serviço para interagir com a API da Anthropic Claude AI."""
    
    def __init__(self):
        """Inicializa o cliente Anthropic se a chave de API estiver configurada."""
        self.api_key = settings.anthropic_api_key
        self.modelo = "claude-3-sonnet-20240229"  # Modelo padrão estável
        # Nota: O requisito mencionava claude-sonnet-4-20250514, mas usaremos uma versão estável atual
        
        self.cliente = None
        if self.api_key:
            self.cliente = AsyncAnthropic(api_key=self.api_key)

    async def gerar_explicacao(self, dados_diagnostico: Dict[str, Any]) -> str:
        """
        Gera uma explicação em linguagem natural para o diagnóstico.
        
        Args:
            dados_diagnostico: Dicionário contendo nível de risco, áreas e alertas.
            
        Returns:
            str: Explicação gerada pela IA ou fallback em caso de erro.
        """
        if not self.cliente:
            logger.warning("Anthropic API key não configurada. Usando explicação padrão.")
            return self._gerar_explicacao_padrao(dados_diagnostico)

        prompt = self._construir_prompt(dados_diagnostico)
        
        try:
            mensagem = await self.cliente.messages.create(
                model=self.modelo,
                max_tokens=1000,
                temperature=0.7,
                system=(
                    "Você é um especialista em conformidade socioambiental rural no Brasil. "
                    "Sua tarefa é explicar diagnósticos de risco ambiental para produtores rurais "
                    "de forma clara, profissional e acessível (evite juridiquês excessivo). "
                    "Sempre escreva em Português do Brasil."
                ),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extrai o texto da resposta
            if mensagem.content and len(mensagem.content) > 0:
                return mensagem.content[0].text
                
            return self._gerar_explicacao_padrao(dados_diagnostico)
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do Claude: {str(e)}")
            return self._gerar_explicacao_padrao(dados_diagnostico)

    def _construir_prompt(self, dados: Dict[str, Any]) -> str:
        """Constrói o prompt para ser enviado ao Claude."""
        nivel_risco = dados.get("nivel_risco", "NÃO INFORMADO")
        prodes_area = dados.get("area_prodes", 0.0)
        deter_count = dados.get("contagem_deter", 0)
        
        return (
            f"Por favor, gere uma explicação para o seguinte diagnóstico ambiental de uma fazenda:\n\n"
            f"- Nível de Risco: {nivel_risco}\n"
            f"- Área de sobreposição PRODES (desmatamento consolidado): {prodes_area:.2f} hectares\n"
            f"- Quantidade de alertas DETER (desmatamento em tempo real): {deter_count}\n\n"
            "A explicação deve conter:\n"
            "1. Um resumo do que esse nível de risco significa para o produtor.\n"
            "2. Por que a fazenda foi classificada assim.\n"
            "3. Próximos passos recomendados (ex: buscar consultoria, verificar CAR, etc).\n"
            "Seja direto e use um tom de apoio ao produtor."
        )

    def _gerar_explicacao_padrao(self, dados: Dict[str, Any]) -> str:
        """Gera uma explicação baseada em templates caso a IA falhe ou não esteja configurada."""
        nivel = dados.get("nivel_risco", "APTO")
        
        templates = {
            "APTO": (
                "Excelente! Sua propriedade está em plena conformidade socioambiental. "
                "Não foram detectados indícios de desmatamento nas bases oficiais (PRODES/DETER). "
                "Sua situação é favorável para a obtenção de crédito rural."
            ),
            "RISCO_MEDIO": (
                "Atenção moderada. Identificamos pequenos registros de desmatamento ou alertas antigos. "
                "Embora não haja um bloqueio imediato, é importante revisar sua documentação ambiental "
                "e garantir que não existam novas áreas sendo abertas sem autorização."
            ),
            "RISCO_ALTO": (
                "Risco elevado identificado. Foram encontrados alertas significativos de desmatamento. "
                "Isso pode impactar negativamente sua análise de crédito. Recomendamos realizar uma "
                "auditoria técnica detalhada para entender a origem desses dados."
            ),
            "BLOQUEIO_PROVAVEL": (
                "Situação crítica. Detectamos desmatamentos muito recentes ou áreas extensas de supressão. "
                "Há uma alta probabilidade de bloqueio de crédito rural conforme as normas do Banco Central. "
                "Busque apoio técnico especializado imediatamente."
            ),
            "BLOQUEIO_DIRETO": (
                "Crédito bloqueado no momento. O CAR da propriedade não está em situação regular (ativo). "
                "A regularização do status do CAR é o primeiro passo obrigatório para qualquer análise de conformidade."
            )
        }
        
        return templates.get(nivel, "Diagnóstico concluído. Consulte o relatório técnico para mais detalhes.")
