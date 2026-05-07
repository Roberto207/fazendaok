"""
Endpoints de API para geração e consulta de diagnósticos socioambientais.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import obter_sessao_db
from app.models.diagnostic import Diagnostico
from app.models.property import Propriedade
from app.schemas.diagnostic import RespostaDiagnostico, RespostaStatusTarefa
from app.celery_app import celery_app

router = APIRouter()


@router.post("/gerar/{propriedade_id}", status_code=status.HTTP_202_ACCEPTED)
async def gerar_diagnostico(
    propriedade_id: str,
    db: AsyncSession = Depends(obter_sessao_db)
):
    """
    Inicia a geração de um diagnóstico socioambiental para uma propriedade.
    Retorna o ID da tarefa para acompanhamento.
    """
    # 1. Verifica se a propriedade existe
    resultado = await db.execute(
        select(Propriedade).where(Propriedade.id == uuid.UUID(propriedade_id))
    )
    propriedade = resultado.scalar_one_or_none()
    
    if not propriedade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriedade não encontrada."
        )
    
    # 2. Inicia a tarefa Celery
    # Nota: A tarefa ainda será implementada em detalhes
    tarefa = celery_app.send_task(
        "app.tasks.diagnostic_tasks.processar_diagnostico_task",
        args=[propriedade_id]
    )
    
    return {"tarefa_id": tarefa.id, "status": "PENDING"}


@router.get("/status/{tarefa_id}", response_model=RespostaStatusTarefa)
async def consultar_status_tarefa(tarefa_id: str):
    """Consulta o status de uma tarefa de diagnóstico."""
    tarefa = celery_app.AsyncResult(tarefa_id)
    
    resposta = {
        "tarefa_id": tarefa_id,
        "status": tarefa.status,
    }
    
    if tarefa.status == "SUCCESS":
        resposta["resultado_id"] = str(tarefa.result)
    elif tarefa.status == "FAILURE":
        resposta["erro"] = str(tarefa.info)
        
    return resposta


@router.get("/{diagnostico_id}", response_model=RespostaDiagnostico)
async def obter_diagnostico(
    diagnostico_id: str,
    db: AsyncSession = Depends(obter_sessao_db)
):
    """Retorna os detalhes de um diagnóstico específico."""
    resultado = await db.execute(
        select(Diagnostico).where(Diagnostico.id == uuid.UUID(diagnostico_id))
    )
    diagnostico = resultado.scalar_one_or_none()
    
    if not diagnostico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico não encontrado."
        )
    
    return diagnostico


@router.get("/historico/{numero_car}", response_model=List[RespostaDiagnostico])
async def obter_historico_diagnosticos(
    numero_car: str,
    limite: int = Query(10, ge=1, le=100),
    pular: int = Query(0, ge=0),
    db: AsyncSession = Depends(obter_sessao_db)
):
    """Retorna o histórico de diagnósticos de uma propriedade pelo número do CAR."""
    # Busca a propriedade primeiro
    resultado_prop = await db.execute(
        select(Propriedade).where(Propriedade.car_number == numero_car)
    )
    propriedade = resultado_prop.scalar_one_or_none()
    
    if not propriedade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriedade não encontrada."
        )
    
    # Busca os diagnósticos
    resultado_diag = await db.execute(
        select(Diagnostico)
        .where(Diagnostico.property_id == propriedade.id)
        .order_by(Diagnostico.created_at.desc())
        .limit(limite)
        .offset(pular)
    )
    diagnosticos = resultado_diag.scalars().all()
    
    return diagnosticos
