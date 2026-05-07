"""
Endpoints de API para o dashboard administrativo e visão geral.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import List, Dict, Any

from app.database import obter_sessao_db
from app.models.property import Propriedade
from app.models.photo import Foto
from app.models.diagnostic import Diagnostico
from app.schemas.dashboard import ResumoDashboard, EstatisticasPropriedade, EstatisticasFoto

router = APIRouter()


@router.get("/resumo", response_model=ResumoDashboard)
async def obter_resumo_dashboard(db: AsyncSession = Depends(obter_sessao_db)):
    """
    Retorna estatísticas consolidadas para o dashboard principal.
    """
    # 1. Estatísticas de Propriedades
    resultado_prop = await db.execute(
        select(
            func.count(Propriedade.id).label("total"),
            func.sum(Propriedade.total_area_ha).label("area")
        )
    )
    estat_prop = resultado_prop.first()
    
    # 2. Estatísticas de Fotos
    resultado_foto = await db.execute(
        select(
            func.count(Foto.id).label("total"),
            func.count(Foto.id).filter(Foto.validation_status == "valid").label("validadas"),
            func.count(Foto.id).filter(Foto.validation_status == "invalid").label("invalidas"),
            func.count(Foto.id).filter(Foto.validation_status == "pending").label("pendentes")
        )
    )
    estat_foto = resultado_foto.first()
    
    # 3. Alertas recentes (Diagnósticos com risco alto/crítico)
    resultado_alertas = await db.execute(
        select(Diagnostico)
        .where(Diagnostico.risk_level.in_(["RISCO_ALTO", "BLOQUEIO_PROVAVEL", "BLOQUEIO_DIRETO"]))
        .order_by(Diagnostico.created_at.desc())
        .limit(5)
    )
    alertas_recentes = resultado_alertas.scalars().all()
    
    alertas_formatados = [
        {
            "id": str(a.id),
            "propriedade_id": str(a.property_id),
            "risk_level": a.risk_level,
            "data": a.created_at.isoformat()
        }
        for a in alertas_recentes
    ]
    
    return ResumoDashboard(
        propriedades=EstatisticasPropriedade(
            total_propriedades=estat_prop.total or 0,
            total_area_ha=float(estat_prop.area or 0),
            total_alertas_ativos=len(alertas_recentes)
        ),
        fotos=EstatisticasFoto(
            total_fotos=estat_foto.total or 0,
            fotos_validadas=estat_foto.validadas or 0,
            fotos_invalidas=estat_foto.invalidas or 0,
            fotos_pendentes=estat_foto.pendentes or 0
        ),
        alertas_recentes=alertas_formatados
    )
