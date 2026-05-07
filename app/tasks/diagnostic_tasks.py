"""
Tarefas assíncronas do Celery para processamento de diagnósticos.
Requisitos atendidos: 4.1, 4.8, 4.9, 4.10, 11.1, 18.2, 18.5, 18.6
"""

import asyncio
import logging
from datetime import date, datetime
from celery.utils.log import get_task_logger
from sqlalchemy import select
from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.services.diagnostic_service import ServicoDiagnostico
from app.services.spatial_service import ServicoEspacial
from app.services.claude_service import ServicoClaude
from app.services.report_service import ServicoRelatorio
from app.models.property import Propriedade
from app.models.diagnostic import Diagnostico

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def processar_diagnostico_task(self, property_id: str):
    """
    Tarefa Celery para processar o diagnóstico completo de uma propriedade.
    
    Args:
        property_id: UUID da propriedade no banco de dados.
    """
    # Cria um novo event loop para rodar código assíncrono dentro da tarefa síncrona do Celery
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        return loop.run_until_complete(_executar_diagnostico(property_id))
    except Exception as exc:
        logger.error(f"Erro ao processar diagnóstico para {property_id}: {str(exc)}")
        # Tenta novamente em caso de falha temporária (ex: erro de conexão com DB ou API)
        raise self.retry(exc=exc, countdown=60)

async def _executar_diagnostico(property_id: str):
    """Execução assíncrona da lógica de diagnóstico."""
    logger.info(f"Iniciando processamento de diagnóstico para propriedade: {property_id}")
    
    servico_diagnostico = ServicoDiagnostico()
    servico_claude = ServicoClaude()
    servico_relatorio = ServicoRelatorio()
    
    async with AsyncSessionLocal() as db:
        # 1. Buscar a propriedade
        stmt = select(Propriedade).where(Propriedade.id == property_id)
        result = await db.execute(stmt)
        propriedade = result.scalar_one_or_none()
        
        if not propriedade:
            logger.error(f"Propriedade {property_id} não encontrada no banco de dados.")
            return None

        # 2. Análise Espacial (PRODES + DETER)
        # O polígono já está no formato adequado para queries espaciais se vier do GeoAlchemy2
        try:
            prodes_intersections = await ServicoEspacial.buscar_interseccoes_prodes(db, propriedade.polygon)
            deter_intersections = await ServicoEspacial.buscar_interseccoes_deter(db, propriedade.polygon)
        except Exception as e:
            logger.warning(f"Erro na análise espacial (tabelas podem não existir ainda): {str(e)}")
            prodes_intersections = []
            deter_intersections = []
        
        # Calcular totais
        total_prodes_area = sum(float(item["area_ha"]) for item in prodes_intersections)
        total_deter_count = len(deter_intersections)
        
        latest_deter_date = None
        if deter_intersections:
            # Filtra None e obtém a data mais recente
            datas = [item["alert_date"] for item in deter_intersections if item.get("alert_date")]
            if datas:
                latest_deter_date = max(datas)

        # 3. Classificação de Risco
        # Mapeia alertas DETER para o formato esperado pelo classificador
        alertas_formatados = [{"data_alerta": item["alert_date"]} for item in deter_intersections]
        
        nivel_risco = servico_diagnostico.classificar_risco(
            status_car=propriedade.car_status,
            area_sobreposicao_prodes=total_prodes_area,
            alertas_deter=alertas_formatados
        )
        
        # 4. Geração de Explicação com IA (Claude)
        dados_para_ai = {
            "nivel_risco": nivel_risco,
            "area_prodes": total_prodes_area,
            "contagem_deter": total_deter_count
        }
        
        explicacao = await servico_claude.gerar_explicacao(dados_para_ai)
        
        # 5. Salvar o Diagnóstico
        novo_diagnostico = Diagnostico(
            property_id=propriedade.id,
            risk_level=nivel_risco,
            prodes_overlap_area_ha=total_prodes_area,
            deter_alert_count=total_deter_count,
            latest_deter_date=latest_deter_date,
            prodes_intersections=prodes_intersections,
            deter_intersections=deter_intersections,
            explanation=explicacao
        )
        
        db.add(novo_diagnostico)
        await db.commit()
        await db.refresh(novo_diagnostico)
        
        # 6. Cachear o resultado
        await servico_diagnostico.servico_cache.salvar_diagnostico(
            numero_car=propriedade.car_number,
            dados={
                "id": str(novo_diagnostico.id),
                "risk_level": str(nivel_risco),
                "explanation": explicacao,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # 7. Gerar Relatório PDF
        try:
            # Por enquanto apenas gera os bytes. Em produção, isso seria enviado para S3.
            pdf_content = await servico_relatorio.gerar_pdf_diagnostico(novo_diagnostico, propriedade)
            logger.info(f"Relatório PDF gerado para {property_id} ({len(pdf_content)} bytes)")
            # TODO: Upload para S3 e salvar URL no diagnóstico se houver campo
        except Exception as e:
            logger.error(f"Erro ao gerar PDF do relatório: {str(e)}")
        
        logger.info(f"Diagnóstico finalizado para {property_id}. Risco: {nivel_risco}")
        return str(novo_diagnostico.id)
